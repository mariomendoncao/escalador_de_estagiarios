import os
# Set env var BEFORE importing app modules to avoid connecting to real DB
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

# Use an in-memory SQLite database for testing logic
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Data
shifts_data = [
    {
        "id": 1,
        "simbolo": "m",
        "nome": "manh\u00e3",
        "inicio": "05:30:00",
        "fim": "13:45:00",
        "etapa": 1,
        "complementar": 0,
        "turno_pricipal_id": None,
        "turno_noturno": 0,
        "duracao": 495
    },
    {
        "id": 4,
        "simbolo": "m2",
        "nome": "manh\u00e3 2",
        "inicio": "06:30:00",
        "fim": "13:45:00",
        "etapa": 0,
        "complementar": 1,
        "turno_pricipal_id": 1,
        "turno_noturno": 0,
        "duracao": 435
    },
    {
        "id": 2,
        "simbolo": "t",
        "nome": "tarde",
        "inicio": "13:30:00",
        "fim": "21:15:00",
        "etapa": 0,
        "complementar": 0,
        "turno_pricipal_id": None,
        "turno_noturno": 0,
        "duracao": 465
    },
    {
        "id": 7,
        "simbolo": "T4",
        "nome": "tarde 4",
        "inicio": "13:30:00",
        "fim": "22:00:00",
        "etapa": 1,
        "complementar": 1,
        "turno_pricipal_id": 2,
        "turno_noturno": 0,
        "duracao": 510
    },
    {
        "id": 3,
        "simbolo": "p",
        "nome": "pernoite",
        "inicio": "21:00:00",
        "fim": "05:45:00",
        "etapa": 1,
        "complementar": 0,
        "turno_pricipal_id": 0,
        "turno_noturno": 1,
        "duracao": 525
    }
]

daily_data = [
    {
        "data": "2025-11-01",
        "soma_total": [
            { "turno": 1, "total": 2 },
            { "turno": 4, "total": 0 },
            { "turno": 2, "total": 0 },
            { "turno": 7, "total": 2 },
            { "turno": 3, "total": 1 }
        ]
    }
]

def test_logic():
    # 1. Import Shifts
    print("Importing Shifts...")
    response = client.post("/shifts/import", json=shifts_data)
    assert response.status_code == 200
    print("Shifts imported.")

    # 2. Import Capacity
    print("Importing Capacity...")
    # payload = {"data": daily_data} # Old format
    payload = daily_data # New format (list directly)
    response = client.post("/months/2025-11/instructor-capacity/import-json", json=payload)
    assert response.status_code == 200
    print("Capacity imported.")

    # 3. Verify Results
    print("Verifying Results...")
    response = client.get("/months/2025-11/instructor-capacity")
    assert response.status_code == 200
    capacities = response.json()
    
    day_caps = [c for c in capacities if c['date'] == '2025-11-01']
    for cap in day_caps:
        print(f"Shift: {cap['shift']}, Total: {cap['total_instructors']}")
    
    manha = next((c for c in day_caps if c['shift'] == 'manha'), None)
    tarde = next((c for c in day_caps if c['shift'] == 'tarde'), None)
    pernoite = next((c for c in day_caps if c['shift'] == 'pernoite'), None)
    
    assert manha['total_instructors'] == 2 # 2 (shift 1) + 0 (shift 4)
    assert tarde['total_instructors'] == 2 # 0 (shift 2) + 2 (shift 7)
    assert pernoite['total_instructors'] == 1 # 1 (shift 3)
    
    print("SUCCESS: Logic verified locally!")

if __name__ == "__main__":
    test_logic()
