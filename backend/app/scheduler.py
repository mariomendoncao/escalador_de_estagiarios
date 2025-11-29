from sqlalchemy.orm import Session
from sqlalchemy import extract
from . import crud, models, schemas
from datetime import date, timedelta
import calendar
from collections import defaultdict

def generate_schedule(db: Session, month_str: str):
    year, month = map(int, month_str.split('-'))
    _, last_day = calendar.monthrange(year, month)

    # 1. Clear existing assignments
    crud.delete_assignments_for_month(db, month_str)

    # 2. Get all capacities for the month
    capacities = crud.get_capacities(db, month_str)
    # Organize capacity by date and shift
    capacity_map = {}
    for cap in capacities:
        capacity_map[(cap.date, cap.shift)] = cap.total_instructors

    # 3. Get all active trainees for this month
    trainees = crud.get_trainees_for_month(db, month_str)
    active_trainees = [t for t in trainees if t.active]
    
    # 4. Track shifts worked per trainee to balance load
    # We could query the DB, but since we just cleared the month, we start from 0 for this month.
    # If we wanted to balance across months, we'd need to query previous months. 
    # For now, we balance within the generated month as implied.
    trainee_shift_counts = {t.id: 0 for t in active_trainees}
    
    # 5. Iterate through days and shifts
    shifts = [models.Shift.manha, models.Shift.tarde, models.Shift.pernoite]
    
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        
        for shift in shifts:
            required_capacity = capacity_map.get((current_date, shift), 0)
            
            if required_capacity <= 0:
                continue
            
            # Find available trainees
            available_candidates = []
            for trainee in active_trainees:
                # Check if trainee is available
                # We need to fetch availability. Optimization: Fetch all availabilities for month once.
                # For now, let's fetch per day/trainee or assume we have it.
                # Let's do a query inside the loop for simplicity or refactor to fetch all.
                # Better: Fetch all availabilities for the month upfront.
                pass 

    # Refactoring for performance: Fetch all UNAVAILABILITY upfront
    # Changed logic: Now we track who is UNAVAILABLE, not who is available
    # This way, missing records default to AVAILABLE
    all_availabilities = db.query(models.TraineeAvailability).filter(
        extract('year', models.TraineeAvailability.date) == year,
        extract('month', models.TraineeAvailability.date) == month
    ).all()

    unavailability_lookup = set()
    for av in all_availabilities:
        if not av.available:  # Track UNavailable, not available
            unavailability_lookup.add((av.trainee_id, av.date, av.shift))

    # Re-iterate
    assignments = []
    
    # Track who worked today to enforce "1 shift per day"
    # Map: date -> set(trainee_ids)
    daily_assignments = defaultdict(set)

    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        
        for shift in shifts:
            required_capacity = capacity_map.get((current_date, shift), 0)
            if required_capacity <= 0:
                continue
            
            # Filter candidates
            candidates = []
            for trainee in active_trainees:
                # 1. Must be available (NOT in unavailability lookup)
                # Default is available, so if NOT in unavailability_lookup, they're available
                if (trainee.id, current_date, shift) in unavailability_lookup:
                    continue

                # 2. Must not have worked today already
                if trainee.id in daily_assignments[current_date]:
                    continue

                candidates.append(trainee)
            
            # Sort candidates
            # Primary: Least shifts worked (asc)
            # Secondary: ID (asc) for determinism
            candidates.sort(key=lambda t: (trainee_shift_counts[t.id], t.id))
            
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
                trainee_shift_counts[trainee.id] += 1
                daily_assignments[current_date].add(trainee.id)
                assignments.append((trainee.id, current_date, shift))
                
    return len(assignments)
