from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base
from .routers import trainees, schedule
from .routers.trainees import availability_router
from .services import shift_service

# Create tables
Base.metadata.create_all(bind=engine)

# Load shift definitions
with Session(engine) as db:
    shift_service.load_shifts_from_json(db)

app = FastAPI(title="Intern Schedule System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trainees.router)
app.include_router(availability_router)
app.include_router(schedule.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Intern Schedule API"}
