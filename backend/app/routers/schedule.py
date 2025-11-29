from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database, parser, scheduler

router = APIRouter(
    tags=["schedule"]
)

# Monthly Schedules Management
@router.get("/months", response_model=List[schemas.MonthlySchedule])
def list_monthly_schedules(db: Session = Depends(database.get_db)):
    """List all existing monthly schedules"""
    return crud.get_all_monthly_schedules(db)

@router.post("/months", response_model=schemas.MonthlySchedule)
def create_monthly_schedule(request: schemas.MonthlyScheduleCreate, db: Session = Depends(database.get_db)):
    """Create a new monthly schedule context"""
    return crud.get_or_create_monthly_schedule(db, request.month)

@router.delete("/months/{month}")
def delete_monthly_schedule(month: str, db: Session = Depends(database.get_db)):
    """Delete a monthly schedule and all associated data"""
    success = crud.delete_monthly_schedule(db, month)
    if not success:
        raise HTTPException(status_code=404, detail="Monthly schedule not found")
    return {"status": "ok", "message": f"Deleted schedule for {month}"}

# Instructor Capacity
@router.post("/months/{month}/instructor-capacity/import")
def import_capacity_with_month(month: str, body: str = Body(..., media_type="text/plain"), db: Session = Depends(database.get_db)):
    """Import instructor capacity from HTML table"""

    # Debug: Save the raw input to a file
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"=== RAW INPUT (first 500 chars) ===")
    logger.info(body[:500])
    logger.info(f"=== END RAW INPUT ===")

    # Save to file for debugging
    with open('/tmp/capacity_import_debug.txt', 'w') as f:
        f.write(body)
    logger.info("Saved raw input to /tmp/capacity_import_debug.txt")

    parsed_data = parser.parse_html_table(body, month)
    created_count = 0
    for item in parsed_data:
        crud.create_instructor_capacity(db, month, schemas.InstructorCapacityCreate(**item))
        created_count += 1
    return {"message": f"Imported {created_count} capacity records for {month}"}

@router.post("/shifts/import", response_model=List[schemas.ShiftDefinition])
def import_shift_definitions(shifts: List[schemas.ShiftDefinitionCreate], db: Session = Depends(database.get_db)):
    """Import or update shift definitions"""
    created_shifts = []
    for shift in shifts:
        created_shifts.append(crud.create_shift_definition(db, shift))
    return created_shifts

import logging
logger = logging.getLogger(__name__)

@router.post("/months/{month}/instructor-capacity/import-json")
def import_capacity_json(month: str, data: List[schemas.DailyAvailability], db: Session = Depends(database.get_db)):
    """Import instructor capacity from JSON list with specific aggregation logic using persisted shift definitions"""

    from .. import models

    print(f"DEBUG: Received import request for {month}")
    print(f"DEBUG: Data length: {len(data)}")
    if len(data) > 0:
        print(f"DEBUG: First item keys: {data[0].dict().keys()}")
        print(f"DEBUG: First item data: {data[0].data}")
    else:
        print("DEBUG: Data is empty!")

    # 1. Get or create monthly schedule
    schedule = crud.get_or_create_monthly_schedule(db, month)

    # 2. Fetch shift definitions from DB
    db_shifts = crud.get_all_shift_definitions(db)
    shift_map = {s.id: s for s in db_shifts}

    if not shift_map:
        raise HTTPException(status_code=400, detail="No shift definitions found. Please import shifts first.")

    # 3. Helper to check if a shift is complementary to a main shift
    def is_complementary_to(shift_id: int, main_shift_id: int) -> bool:
        if shift_id == main_shift_id:
            return True
        shift_def = shift_map.get(shift_id)
        if shift_def and shift_def.turno_pricipal_id == main_shift_id:
            return True
        return False

    # 4. Collect all capacity records to insert/update
    capacity_records = []

    for daily_data in data:
        # daily_data.data is "YYYY-MM-DD"
        date_obj = parser.date.fromisoformat(daily_data.data)

        # Initialize totals
        manha_total = 0
        tarde_total = 0
        pernoite_total = 0

        for shift_total in daily_data.soma_total:
            shift_id = shift_total.turno
            total = shift_total.total

            if is_complementary_to(shift_id, 1): # Manhã
                manha_total += total
            elif is_complementary_to(shift_id, 2): # Tarde
                tarde_total += total
            elif is_complementary_to(shift_id, 3): # Pernoite
                pernoite_total += total

        # Add to records list
        capacity_records.append((date_obj, schemas.Shift.manha, manha_total))
        capacity_records.append((date_obj, schemas.Shift.tarde, tarde_total))
        capacity_records.append((date_obj, schemas.Shift.pernoite, pernoite_total))

    # 5. Delete all existing capacity records for this month (simpler than upsert)
    year, month_num = map(int, month.split('-'))
    deleted = db.query(models.InstructorCapacity).filter(
        models.InstructorCapacity.monthly_schedule_id == schedule.id,
        models.InstructorCapacity.date >= parser.date(year, month_num, 1),
        models.InstructorCapacity.date < parser.date(year if month_num < 12 else year + 1, month_num + 1 if month_num < 12 else 1, 1)
    ).delete(synchronize_session=False)

    print(f"DEBUG: Deleted {deleted} existing records")

    # 6. Use bulk_insert_mappings for maximum performance
    capacity_dicts = []
    for date_obj, shift, total in capacity_records:
        capacity_dicts.append({
            'monthly_schedule_id': schedule.id,
            'date': date_obj,
            'shift': shift,
            'total_instructors': total
        })

    print(f"DEBUG: Prepared {len(capacity_dicts)} records for bulk insert")

    if capacity_dicts:
        db.bulk_insert_mappings(models.InstructorCapacity, capacity_dicts)

    print(f"DEBUG: Bulk insert completed, committing...")

    # 7. Single commit at the end
    db.commit()

    print(f"DEBUG: Commit completed!")

    created_count = len(capacity_dicts)

    return {"message": f"Imported {created_count} capacity records for {month}"}

@router.get("/months/{month}/instructor-capacity", response_model=List[schemas.InstructorCapacity])
def get_instructor_capacity(month: str, db: Session = Depends(database.get_db)):
    """Get instructor capacity for a specific month"""
    return crud.get_capacities(db, month)

# Schedule Generation
@router.post("/months/{month}/schedule/generate")
def generate_schedule(month: str, db: Session = Depends(database.get_db)):
    """Generate schedule for a specific month"""
    count = scheduler.generate_schedule(db, month)
    return {"message": f"Generated {count} assignments for {month}"}

@router.delete("/months/{month}/schedule")
def clear_schedule(month: str, db: Session = Depends(database.get_db)):
    """Clear all schedule assignments for a specific month"""
    crud.delete_assignments_for_month(db, month)
    return {"message": f"Cleared schedule for {month}"}

@router.delete("/months/{month}/trainees/{trainee_id}/schedule")
def clear_trainee_schedule(month: str, trainee_id: int, db: Session = Depends(database.get_db)):
    """Clear schedule assignments for a specific trainee in a month"""
    crud.delete_assignments_for_trainee(db, month, trainee_id)
    return {"message": f"Cleared schedule for trainee {trainee_id} in {month}"}

@router.get("/months/{month}/schedule", response_model=List[schemas.TraineeAssignment])
def get_schedule(month: str, db: Session = Depends(database.get_db)):
    """Get generated schedule for a specific month"""
    return crud.get_assignments(db, month)
