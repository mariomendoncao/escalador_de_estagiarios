from sqlalchemy.orm import Session
from sqlalchemy import and_, extract
from . import models, schemas
from datetime import date

# Monthly Schedules
def get_monthly_schedule(db: Session, month: str):
    """Get a monthly schedule context (returns None if not found)"""
    return db.query(models.MonthlySchedule).filter(models.MonthlySchedule.month == month).first()

def get_or_create_monthly_schedule(db: Session, month: str):
    """Get or create a monthly schedule context - USE ONLY for explicit creation"""
    db_schedule = get_monthly_schedule(db, month)
    if not db_schedule:
        db_schedule = models.MonthlySchedule(month=month)
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
    return db_schedule

def get_all_monthly_schedules(db: Session):
    """Get all monthly schedules"""
    return db.query(models.MonthlySchedule).order_by(models.MonthlySchedule.month.desc()).all()

def delete_monthly_schedule(db: Session, month: str):
    """Delete a monthly schedule and all associated data (cascade)"""
    db_schedule = db.query(models.MonthlySchedule).filter(models.MonthlySchedule.month == month).first()
    if db_schedule:
        db.delete(db_schedule)
        db.commit()
        return True
    return False

# Trainees (month-specific)
def get_trainee(db: Session, trainee_id: int):
    return db.query(models.Trainee).filter(models.Trainee.id == trainee_id).first()

def get_trainees_for_month(db: Session, month: str):
    """Get all trainees for a specific month"""
    schedule = get_monthly_schedule(db, month)
    if not schedule:
        return []
    return db.query(models.Trainee).filter(
        models.Trainee.monthly_schedule_id == schedule.id
    ).all()

def create_trainee(db: Session, month: str, trainee: schemas.TraineeCreate):
    """Create a trainee in a specific month context"""
    schedule = get_or_create_monthly_schedule(db, month)
    db_trainee = models.Trainee(
        monthly_schedule_id=schedule.id,
        name=trainee.name,
        active=trainee.active
    )
    db.add(db_trainee)
    db.commit()
    db.refresh(db_trainee)
    return db_trainee

def update_trainee(db: Session, trainee_id: int, trainee: schemas.TraineeCreate):
    db_trainee = get_trainee(db, trainee_id)
    if db_trainee:
        db_trainee.name = trainee.name
        db_trainee.active = trainee.active
        db.commit()
        db.refresh(db_trainee)
    return db_trainee

def delete_trainee(db: Session, trainee_id: int):
    db_trainee = get_trainee(db, trainee_id)
    if db_trainee:
        db.delete(db_trainee)
        db.commit()
    return db_trainee

# Availability
def get_availability(db: Session, trainee_id: int, month: str):
    schedule = get_monthly_schedule(db, month)
    if not schedule:
        return []
    year, month_num = map(int, month.split('-'))
    return db.query(models.TraineeAvailability).filter(
        models.TraineeAvailability.trainee_id == trainee_id,
        models.TraineeAvailability.monthly_schedule_id == schedule.id,
        extract('year', models.TraineeAvailability.date) == year,
        extract('month', models.TraineeAvailability.date) == month_num
    ).all()

def get_all_availability_for_month(db: Session, month: str):
    """Get all availability records for a month across all trainees"""
    schedule = get_monthly_schedule(db, month)
    if not schedule:
        return []
    year, month_num = map(int, month.split('-'))
    return db.query(models.TraineeAvailability).filter(
        models.TraineeAvailability.monthly_schedule_id == schedule.id,
        extract('year', models.TraineeAvailability.date) == year,
        extract('month', models.TraineeAvailability.date) == month_num
    ).all()

def is_trainee_available(db: Session, trainee_id: int, date_obj: date, shift: str) -> bool:
    """
    Check if a trainee is available for a specific date and shift.
    Returns True if:
    - No availability record exists (DEFAULT = AVAILABLE)
    - Availability record exists with available=True

    Returns False if:
    - Availability record exists with available=False
    """
    record = db.query(models.TraineeAvailability).filter(
        models.TraineeAvailability.trainee_id == trainee_id,
        models.TraineeAvailability.date == date_obj,
        models.TraineeAvailability.shift == shift
    ).first()

    # No record = available by default
    if record is None:
        return True

    # Record exists, return its availability value
    return record.available

def create_or_update_availability(db: Session, month: str, availability: schemas.TraineeAvailabilityCreate):
    schedule = get_or_create_monthly_schedule(db, month)

    db_availability = db.query(models.TraineeAvailability).filter(
        models.TraineeAvailability.trainee_id == availability.trainee_id,
        models.TraineeAvailability.date == availability.date,
        models.TraineeAvailability.shift == availability.shift
    ).first()

    if db_availability:
        db_availability.available = availability.available
        db_availability.reason = availability.reason
    else:
        db_availability = models.TraineeAvailability(
            monthly_schedule_id=schedule.id,
            trainee_id=availability.trainee_id,
            date=availability.date,
            shift=availability.shift,
            available=availability.available,
            reason=availability.reason
        )
        db.add(db_availability)

    db.commit()
    db.refresh(db_availability)
    return db_availability

def bulk_create_availability(db: Session, month: str, trainee_id: int, availabilities: list[schemas.TraineeAvailabilityBase]):
    for av in availabilities:
        create_or_update_availability(db, month, schemas.TraineeAvailabilityCreate(
            trainee_id=trainee_id,
            date=av.date,
            shift=av.shift,
            available=av.available,
            reason=av.reason
        ))
    return True

# Capacity
def create_instructor_capacity(db: Session, month: str, capacity: schemas.InstructorCapacityCreate):
    schedule = get_or_create_monthly_schedule(db, month)

    # Check if exists, update or create
    db_cap = db.query(models.InstructorCapacity).filter(
        models.InstructorCapacity.monthly_schedule_id == schedule.id,
        models.InstructorCapacity.date == capacity.date,
        models.InstructorCapacity.shift == capacity.shift
    ).first()

    if db_cap:
        db_cap.total_instructors = capacity.total_instructors
    else:
        db_cap = models.InstructorCapacity(
            monthly_schedule_id=schedule.id,
            date=capacity.date,
            shift=capacity.shift,
            total_instructors=capacity.total_instructors
        )
        db.add(db_cap)

    db.commit()
    db.refresh(db_cap)
    return db_cap

def get_capacities(db: Session, month: str):
    schedule = get_monthly_schedule(db, month)
    if not schedule:
        return []
    year, month_num = map(int, month.split('-'))
    return db.query(models.InstructorCapacity).filter(
        models.InstructorCapacity.monthly_schedule_id == schedule.id,
        extract('year', models.InstructorCapacity.date) == year,
        extract('month', models.InstructorCapacity.date) == month_num
    ).all()

# Assignments
def delete_assignments_for_month(db: Session, month: str):
    schedule = get_monthly_schedule(db, month)
    if not schedule:
        return
    year, month_num = map(int, month.split('-'))
    db.query(models.TraineeAssignment).filter(
        models.TraineeAssignment.monthly_schedule_id == schedule.id,
        extract('year', models.TraineeAssignment.date) == year,
        extract('month', models.TraineeAssignment.date) == month_num
    ).delete(synchronize_session=False)
    db.commit()

def delete_assignments_for_trainee(db: Session, month: str, trainee_id: int):
    """Delete all assignments for a specific trainee in a given month"""
    schedule = get_monthly_schedule(db, month)
    if not schedule:
        return
    year, month_num = map(int, month.split('-'))
    db.query(models.TraineeAssignment).filter(
        models.TraineeAssignment.monthly_schedule_id == schedule.id,
        models.TraineeAssignment.trainee_id == trainee_id,
        extract('year', models.TraineeAssignment.date) == year,
        extract('month', models.TraineeAssignment.date) == month_num
    ).delete(synchronize_session=False)
    db.commit()

def create_assignment(db: Session, month: str, assignment: schemas.TraineeAssignmentCreate):
    schedule = get_or_create_monthly_schedule(db, month)
    db_assign = models.TraineeAssignment(
        monthly_schedule_id=schedule.id,
        trainee_id=assignment.trainee_id,
        date=assignment.date,
        shift=assignment.shift
    )
    db.add(db_assign)
    db.commit()
    db.refresh(db_assign)
    return db_assign

def get_assignments(db: Session, month: str):
    schedule = get_monthly_schedule(db, month)
    if not schedule:
        return []
    year, month_num = map(int, month.split('-'))
    return db.query(models.TraineeAssignment).filter(
        models.TraineeAssignment.monthly_schedule_id == schedule.id,
        extract('year', models.TraineeAssignment.date) == year,
        extract('month', models.TraineeAssignment.date) == month_num
    ).all()

# Shift Definitions
def create_shift_definition(db: Session, shift: schemas.ShiftDefinitionCreate):
    db_shift = models.ShiftDefinition(
        id=shift.id,
        simbolo=shift.simbolo,
        nome=shift.nome,
        inicio=shift.inicio,
        fim=shift.fim,
        etapa=shift.etapa,
        complementar=shift.complementar,
        turno_pricipal_id=shift.turno_pricipal_id,
        turno_noturno=shift.turno_noturno,
        duracao=shift.duracao
    )
    # Check if exists to update or create
    existing = db.query(models.ShiftDefinition).filter(models.ShiftDefinition.id == shift.id).first()
    if existing:
        existing.simbolo = shift.simbolo
        existing.nome = shift.nome
        existing.inicio = shift.inicio
        existing.fim = shift.fim
        existing.etapa = shift.etapa
        existing.complementar = shift.complementar
        existing.turno_pricipal_id = shift.turno_pricipal_id
        existing.turno_noturno = shift.turno_noturno
        existing.duracao = shift.duracao
        db_shift = existing
    else:
        db.add(db_shift)
    
    db.commit()
    db.refresh(db_shift)
    return db_shift

def get_all_shift_definitions(db: Session):
    return db.query(models.ShiftDefinition).all()
