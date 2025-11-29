from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date
from .models import Shift

class MonthlyScheduleBase(BaseModel):
    month: str  # YYYY-MM

class MonthlyScheduleCreate(MonthlyScheduleBase):
    pass

class MonthlySchedule(MonthlyScheduleBase):
    id: int
    created_at: date

    class Config:
        from_attributes = True

class TraineeBase(BaseModel):
    name: str
    active: bool = True

class TraineeCreate(TraineeBase):
    pass

class Trainee(TraineeBase):
    id: int
    monthly_schedule_id: int
    created_at: date

    class Config:
        from_attributes = True

class TraineeAvailabilityBase(BaseModel):
    date: date
    shift: Shift
    available: bool
    reason: Optional[str] = None

class TraineeAvailabilityCreate(TraineeAvailabilityBase):
    trainee_id: int

class TraineeAvailability(TraineeAvailabilityBase):
    id: int
    trainee_id: int
    monthly_schedule_id: int

    class Config:
        from_attributes = True

class InstructorCapacityBase(BaseModel):
    date: date
    shift: Shift
    total_instructors: int

class InstructorCapacityCreate(InstructorCapacityBase):
    pass

class InstructorCapacity(InstructorCapacityBase):
    id: int
    monthly_schedule_id: int

    class Config:
        from_attributes = True

class TraineeAssignmentBase(BaseModel):
    date: date
    shift: Shift

class TraineeAssignmentCreate(TraineeAssignmentBase):
    trainee_id: int

class TraineeAssignment(TraineeAssignmentBase):
    id: int
    trainee_id: int
    monthly_schedule_id: int
    trainee: Optional[Trainee] = None

    class Config:
        from_attributes = True

class ScheduleGenerationRequest(BaseModel):
    month: str # YYYY-MM

class BulkAvailabilityRequest(BaseModel):
    availabilities: List[TraineeAvailabilityBase]

class BulkImportRequest(BaseModel):
    month: str  # YYYY-MM
    data: Dict[str, Dict[str, str]]  # {"Trainee Name": {"06": "RIS", ...}}

class TurnoDefinition(BaseModel):
    id: int
    simbolo: str
    nome: str
    inicio: str
    fim: str
    etapa: int
    complementar: int
    turno_pricipal_id: Optional[int]
    turno_noturno: int
    duracao: int

class ShiftDefinitionCreate(TurnoDefinition):
    pass

class ShiftDefinition(TurnoDefinition):
    class Config:
        from_attributes = True

class ShiftTotal(BaseModel):
    turno: int
    total: int

class DailyAvailability(BaseModel):
    data: str # YYYY-MM-DD
    soma_total: List[ShiftTotal]

class InstructorCapacityImportRequest(BaseModel):
    # shifts: List[TurnoDefinition] # Removed as we now use persisted definitions
    data: List[DailyAvailability]
