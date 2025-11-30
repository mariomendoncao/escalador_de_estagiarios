from sqlalchemy.orm import Session
from sqlalchemy import extract
from . import crud, models, schemas
from datetime import date, timedelta
import calendar
from collections import defaultdict

def generate_schedule(db: Session, month_str: str):
    year, month = map(int, month_str.split('-'))
    _, last_day = calendar.monthrange(year, month)

    # 1. Get Monthly Schedule Parameters
    schedule_context = crud.get_monthly_schedule(db, month_str)
    if not schedule_context:
        raise ValueError(f"Monthly schedule for {month_str} not found")

    params = {
        'total_shifts': schedule_context.params_total_shifts,
        'night_shifts': schedule_context.params_night_shifts,
        'max_consecutive_days_off': schedule_context.params_max_consecutive_days_off,
        'max_consecutive_work_days': schedule_context.params_max_consecutive_work_days,
        'unavailability_weight': schedule_context.params_unavailability_weight,
        'post_night_shift_off': schedule_context.params_post_night_shift_off
    }

    # 2. Clear existing assignments
    crud.delete_assignments_for_month(db, month_str)

    # 3. Get all capacities for the month
    capacities = crud.get_capacities(db, month_str)
    capacity_map = {}
    for cap in capacities:
        capacity_map[(cap.date, cap.shift)] = cap.total_instructors

    # 4. Get all active trainees
    trainees = crud.get_trainees_for_month(db, month_str)
    active_trainees = [t for t in trainees if t.active]
    
    # 5. Get all unavailabilities
    all_availabilities = db.query(models.TraineeAvailability).filter(
        extract('year', models.TraineeAvailability.date) == year,
        extract('month', models.TraineeAvailability.date) == month
    ).all()

    unavailability_lookup = set()
    trainee_unavailability_counts = defaultdict(int)

    for av in all_availabilities:
        if not av.available:
            unavailability_lookup.add((av.trainee_id, av.date, av.shift))
            # Count distinct days of unavailability for weight calculation? 
            # Requirement: "se o estagiario tem 2 indisponibilides elas contam como 1 servico cada"
            # Assuming this means per shift unavailability or per day? 
            # Usually unavailability is per shift. Let's count per record.
            trainee_unavailability_counts[av.trainee_id] += params['unavailability_weight']

    # 6. Initialize Trackers
    # Shift counts (starts with unavailability weight)
    # We separate "Weighted Count" (for fairness logic if needed) from "Actual Work Count" (for hard limits)
    trainee_weighted_counts = {t.id: trainee_unavailability_counts[t.id] for t in active_trainees}
    trainee_actual_work_counts = {t.id: 0 for t in active_trainees}
    
    trainee_night_shift_counts = {t.id: 0 for t in active_trainees}
    
    # Consecutive work days tracker: trainee_id -> current streak
    consecutive_work_days = {t.id: 0 for t in active_trainees}
    
    # Consecutive days off tracker: trainee_id -> current streak
    consecutive_days_off = {t.id: 0 for t in active_trainees}
    
    # Last worked date: trainee_id -> date
    last_worked_date = {t.id: None for t in active_trainees}

    # Assignments: list of (trainee_id, date, shift)
    assignments = []
    
    # Daily assignments: date -> set(trainee_id)
    daily_assignments = defaultdict(set)

    # 7. Iterate through days and shifts
    # Order: Pernoite first (harder to fill), then Manhã, then Tarde? 
    # Or strict chronological? 
    # Let's stick to chronological day by day, but prioritize Pernoite within the day if needed.
    # Actually, filling Pernoite first for the whole month might be better for the "2 night shifts" rule.
    # But let's try day-by-day for now to handle consecutive rules easier.
    
    shifts_order = [models.Shift.pernoite, models.Shift.manha, models.Shift.tarde]
    
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        
        # Update consecutive counters at start of day (pre-assignment)
        # Actually, we update them at the end of the day based on if they worked.
        
        for shift in shifts_order:
            required_capacity = capacity_map.get((current_date, shift), 0)
            if required_capacity <= 0:
                continue
            
            # Filter candidates
            candidates = []
            for trainee in active_trainees:
                tid = trainee.id
                
                # --- HARD CONSTRAINTS ---

                # 1. Must be available
                if (tid, current_date, shift) in unavailability_lookup:
                    continue

                # 2. Must not have worked today already
                if tid in daily_assignments[current_date]:
                    continue

                # 3. Post-Night Shift Rule (No work day after Pernoite)
                if params['post_night_shift_off']:
                    yesterday = current_date - timedelta(days=1)
                    # Check if worked Pernoite yesterday
                    # We need to check assignments list or a tracker
                    # Optimization: check assignments for yesterday + Pernoite
                    # Since we fill day by day, yesterday is already processed.
                    worked_yesterday_night = False
                    for a_tid, a_date, a_shift in assignments:
                        if a_tid == tid and a_date == yesterday and a_shift == models.Shift.pernoite:
                            worked_yesterday_night = True
                            break
                    if worked_yesterday_night:
                        continue

                # 4. Max Consecutive Work Days
                if consecutive_work_days[tid] >= params['max_consecutive_work_days']:
                    continue

                # --- SOFT CONSTRAINTS / BALANCING (handled by sort) ---
                
                # Check Night Shift Limit (Hard Constraint)
                if shift == models.Shift.pernoite and trainee_night_shift_counts[tid] >= params['night_shifts']:
                     continue

                # Check Total Shift Limit (Hard Constraint)
                # Fix: Use ACTUAL work counts, not weighted counts. 
                # Unavailability shouldn't prevent you from working your target shifts.
                if trainee_actual_work_counts[tid] >= params['total_shifts']:
                    continue

                candidates.append(trainee)
            
            # Sort candidates
            # 1. Night Shift Priority (if current is night shift): 
            #    Those with fewer night shifts go first.
            # 2. Consecutive Days Off Priority:
            #    Those approaching max consecutive days off should be prioritized to avoid breaking rule.
            # 3. Total Shifts: Least shifts worked go first.
            
            def sort_key(t):
                tid = t.id
                
                # Night shift balancing
                night_score = 0
                if shift == models.Shift.pernoite:
                    night_score = trainee_night_shift_counts[tid]
                
                # Total shift balancing
                # Fix: Use ACTUAL work counts for sorting to ensure everyone works evenly.
                # If we use weighted counts, people with unavailability (classes) will be deprioritized and never work.
                total_score = trainee_actual_work_counts[tid]
                
                # Urgency to work (avoid max consecutive days off)
                # Higher consecutive_days_off -> Lower score (to be first)
                urgency_score = -consecutive_days_off[tid] 
                
                return (
                    night_score,      # Prioritize filling night shifts for those who have few
                    urgency_score,    # Prioritize those who have been off for too long
                    total_score,      # Prioritize those with fewest total shifts
                    t.id              # Deterministic tie-breaker
                )

            candidates.sort(key=sort_key)
            
            # Select top N
            selected = candidates[:required_capacity]
            
            for trainee in selected:
                # Create assignment
                crud.create_assignment(db, month_str, schemas.TraineeAssignmentCreate(
                    trainee_id=trainee.id,
                    date=current_date,
                    shift=shift
                ))

                # Update trackers
                trainee_actual_work_counts[trainee.id] += 1
                if shift == models.Shift.pernoite:
                    trainee_night_shift_counts[trainee.id] += 1
                
                daily_assignments[current_date].add(trainee.id)
                assignments.append((trainee.id, current_date, shift))

        # End of Day Processing: Update Consecutive Counters
        for trainee in active_trainees:
            tid = trainee.id
            worked_today = tid in daily_assignments[current_date]
            
            # Check for "Post-P counts as work" rule
            # "o dia seguinte ao P conta como se fosse um dia trabalhado"
            is_post_night_rest = False
            if params['post_night_shift_off']:
                yesterday = current_date - timedelta(days=1)
                for a_tid, a_date, a_shift in assignments:
                    if a_tid == tid and a_date == yesterday and a_shift == models.Shift.pernoite:
                        is_post_night_rest = True
                        break
            
            # "os afastamentos contam como dia trabalhado na sequencia"
            # Fix: Only count as "work" if unavailable for ALL shifts (Afastamento/Leave).
            # Partial unavailability (e.g. just Morning) should NOT prevent a reset if they didn't work.
            
            is_fully_unavailable = True
            for s in [models.Shift.manha, models.Shift.tarde, models.Shift.pernoite]:
                if (tid, current_date, s) not in unavailability_lookup:
                    is_fully_unavailable = False
                    break

            if worked_today or is_post_night_rest or is_fully_unavailable:
                consecutive_work_days[tid] += 1
                consecutive_days_off[tid] = 0
                if worked_today:
                    last_worked_date[tid] = current_date
            else:
                consecutive_days_off[tid] += 1
                consecutive_work_days[tid] = 0

    return len(assignments)
