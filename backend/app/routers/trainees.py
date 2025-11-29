from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database, models
import calendar
from datetime import date as dt_date, datetime

router = APIRouter(
    prefix="/months/{month}/trainees",
    tags=["trainees"]
)

@router.post("/", response_model=schemas.Trainee)
def create_trainee(month: str, trainee: schemas.TraineeCreate, db: Session = Depends(database.get_db)):
    return crud.create_trainee(db=db, month=month, trainee=trainee)

@router.get("/", response_model=List[schemas.Trainee])
def read_trainees(month: str, db: Session = Depends(database.get_db)):
    return crud.get_trainees_for_month(db, month=month)

@router.put("/{trainee_id}", response_model=schemas.Trainee)
def update_trainee(month: str, trainee_id: int, trainee: schemas.TraineeCreate, db: Session = Depends(database.get_db)):
    db_trainee = crud.update_trainee(db, trainee_id, trainee)
    if db_trainee is None:
        raise HTTPException(status_code=404, detail="Trainee not found")
    return db_trainee

@router.delete("/{trainee_id}", response_model=schemas.Trainee)
def delete_trainee(month: str, trainee_id: int, db: Session = Depends(database.get_db)):
    db_trainee = crud.delete_trainee(db, trainee_id)
    if db_trainee is None:
        raise HTTPException(status_code=404, detail="Trainee not found")
    return db_trainee

@router.get("/{trainee_id}/availability", response_model=List[schemas.TraineeAvailability])
def read_availability(month: str, trainee_id: int, db: Session = Depends(database.get_db)):
    return crud.get_availability(db, trainee_id, month)

@router.post("/{trainee_id}/availability/bulk")
def bulk_availability(month: str, trainee_id: int, request: schemas.BulkAvailabilityRequest, db: Session = Depends(database.get_db)):
    crud.bulk_create_availability(db, month, trainee_id, request.availabilities)
    return {"status": "ok"}

# Get all availability for the month (across all trainees)
availability_router = APIRouter(
    prefix="/months/{month}",
    tags=["availability"]
)

@availability_router.get("/availability", response_model=List[schemas.TraineeAvailability])
def get_month_availability(month: str, db: Session = Depends(database.get_db)):
    """Get all trainee availability records for a specific month"""
    return crud.get_all_availability_for_month(db, month)

@router.post("/import-text")
def import_trainees_text(month: str, body: str = Body(..., media_type="text/plain"), db: Session = Depends(database.get_db)):
    """
    Import trainees and unavailability from raw text format.
    """
    from ..parsers.text_parser import parse_unavailability_text
    from datetime import timedelta
    
    entries = parse_unavailability_text(body)
    
    year, month_num = map(int, month.split('-'))
    _, last_day = calendar.monthrange(year, month_num)
    month_start = dt_date(year, month_num, 1)
    month_end = dt_date(year, month_num, last_day)
    
    imported_count = 0
    trainees_found = set()
    
    for entry in entries:
        name = entry.get("name")
        start_dt = entry.get("start")
        end_dt = entry.get("end")
        reason = entry.get("reason")
        
        if not name or not start_dt or not end_dt:
            continue
            
        # 1. Get or Create Trainee
        try:
            # Check if exists first to avoid error
            existing = db.query(models.Trainee).join(models.MonthlySchedule).filter(
                models.Trainee.name == name,
                models.MonthlySchedule.month == month
            ).first()
            
            if existing:
                trainee_id = existing.id
            else:
                trainee = crud.create_trainee(db, month, schemas.TraineeCreate(name=name, active=True))
                trainee_id = trainee.id
        except Exception as e:
            # Fallback if race condition or other error
            print(f"Error getting/creating trainee {name}: {e}")
            continue
            
        trainees_found.add(name)
        
        # 2. Calculate days and shifts
        # Iterate through days in the range
        curr = start_dt.date()
        end = end_dt.date()
        
        while curr <= end:
            # Only process if within the target month
            if curr < month_start or curr > month_end:
                curr += timedelta(days=1)
                continue
                
            # Determine which shifts are affected
            # Logic:
            # If full day (00:00 - 23:59), all shifts.
            # If partial, check overlap.
            # Shifts (approximate):
            # Manhã: 07:00 - 13:00
            # Tarde: 13:00 - 19:00
            # Pernoite: 19:00 - 07:00 (next day)
            
            # For simplicity, if the event covers a significant part of the shift, mark unavailable.
            # Or just mark all shifts if it's a "day off" type event.
            # The input format "Quantidade de dias: 1" suggests day granularity often.
            # But "Expediente" is 13:00 - 19:00. This matches "Tarde".
            
            # Mark ALL shifts as unavailable for this day
            day_availabilities = []
            for shift_name in ["manha", "tarde", "pernoite"]:
                day_availabilities.append(schemas.TraineeAvailabilityBase(
                    date=curr,
                    shift=shift_name,
                    available=False,
                    reason=reason
                ))

            crud.bulk_create_availability(db, month, trainee_id, day_availabilities)
                
            curr += timedelta(days=1)
            
        imported_count += 1
        
    return {"status": "ok", "imported_entries": imported_count, "trainees_affected": list(trainees_found)}

@router.post("/import-list")
def import_trainee_list(month: str, names: List[str], db: Session = Depends(database.get_db)):
    """
    Import a list of trainees (names only).
    Creates them if they don't exist.
    """
    imported = []
    errors = []
    
    for name in names:
        try:
            # Check if exists
            existing = db.query(models.Trainee).join(models.MonthlySchedule).filter(
                models.Trainee.name == name,
                models.MonthlySchedule.month == month
            ).first()
            
            if not existing:
                crud.create_trainee(db, month, schemas.TraineeCreate(name=name, active=True))
                imported.append(name)
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
            
    return {"status": "ok", "imported": len(imported), "imported_names": imported, "errors": errors}
