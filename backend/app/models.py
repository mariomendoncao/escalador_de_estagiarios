from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class Shift(str, enum.Enum):
    manha = "manha"
    tarde = "tarde"
    pernoite = "pernoite"

class MonthlySchedule(Base):
    __tablename__ = "monthly_schedules"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String(7), nullable=False, unique=True)  # YYYY-MM format
    created_at = Column(Date, default=datetime.utcnow)

    trainees = relationship("Trainee", back_populates="monthly_schedule", cascade="all, delete-orphan")
    availabilities = relationship("TraineeAvailability", back_populates="monthly_schedule", cascade="all, delete-orphan")
    capacities = relationship("InstructorCapacity", back_populates="monthly_schedule", cascade="all, delete-orphan")
    assignments = relationship("TraineeAssignment", back_populates="monthly_schedule", cascade="all, delete-orphan")

class Trainee(Base):
    __tablename__ = "trainees"

    id = Column(Integer, primary_key=True, index=True)
    monthly_schedule_id = Column(Integer, ForeignKey("monthly_schedules.id"), nullable=False)
    name = Column(String(255), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(Date, default=datetime.utcnow)

    monthly_schedule = relationship("MonthlySchedule", back_populates="trainees")
    availabilities = relationship("TraineeAvailability", back_populates="trainee", cascade="all, delete-orphan")
    assignments = relationship("TraineeAssignment", back_populates="trainee", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('monthly_schedule_id', 'name', name='uix_trainee_per_month'),
    )

class TraineeAvailability(Base):
    __tablename__ = "trainee_availability"

    id = Column(Integer, primary_key=True, index=True)
    monthly_schedule_id = Column(Integer, ForeignKey("monthly_schedules.id"), nullable=False)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    date = Column(Date, nullable=False)
    shift = Column(Enum(Shift), nullable=False)
    available = Column(Boolean, default=False)
    reason = Column(String(255), nullable=True)

    monthly_schedule = relationship("MonthlySchedule", back_populates="availabilities")
    trainee = relationship("Trainee", back_populates="availabilities")

    __table_args__ = (
        UniqueConstraint('trainee_id', 'date', 'shift', name='uix_trainee_availability'),
    )

class InstructorCapacity(Base):
    __tablename__ = "instructor_capacity"

    id = Column(Integer, primary_key=True, index=True)
    monthly_schedule_id = Column(Integer, ForeignKey("monthly_schedules.id"), nullable=False)
    date = Column(Date, nullable=False)
    shift = Column(Enum(Shift), nullable=False)
    total_instructors = Column(Integer, default=0)

    monthly_schedule = relationship("MonthlySchedule", back_populates="capacities")

    __table_args__ = (
        UniqueConstraint('monthly_schedule_id', 'date', 'shift', name='uix_instructor_capacity_per_month'),
    )

class TraineeAssignment(Base):
    __tablename__ = "trainee_assignments"

    id = Column(Integer, primary_key=True, index=True)
    monthly_schedule_id = Column(Integer, ForeignKey("monthly_schedules.id"), nullable=False)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=False)
    date = Column(Date, nullable=False)
    shift = Column(Enum(Shift), nullable=False)

    monthly_schedule = relationship("MonthlySchedule", back_populates="assignments")
    trainee = relationship("Trainee", back_populates="assignments")

    __table_args__ = (
        UniqueConstraint('trainee_id', 'date', name='uix_trainee_assignment_day'), # One shift per day per trainee
    )

class ShiftDefinition(Base):
    __tablename__ = "shift_definitions"

    id = Column(Integer, primary_key=True, index=True) # Using the ID from the JSON as primary key if possible, or just a column
    # The JSON has "id": 1, "id": 4 etc. It's better to treat them as the primary key or a unique external ID.
    # Let's use the provided ID as the primary key to simplify mapping.
    
    simbolo = Column(String(10), nullable=False)
    nome = Column(String(50), nullable=False)
    inicio = Column(String(10), nullable=False)
    fim = Column(String(10), nullable=False)
    etapa = Column(Integer, default=0)
    complementar = Column(Integer, default=0)
    turno_pricipal_id = Column(Integer, nullable=True)
    turno_noturno = Column(Integer, default=0)
    duracao = Column(Integer, default=0)
