import json
import os
from sqlalchemy.orm import Session
from .. import crud, schemas

def load_shifts_from_json(db: Session):
    """
    Load shift definitions from shifts.json and upsert them into the database.
    """
    json_path = os.path.join(os.path.dirname(__file__), "../data/shifts.json")
    
    if not os.path.exists(json_path):
        print(f"WARNING: shifts.json not found at {json_path}")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            shifts_data = json.load(f)
            
        print(f"Loading {len(shifts_data)} shifts from {json_path}...")
        
        for shift_dict in shifts_data:
            # Ensure turno_pricipal_id is None if it's null in JSON (though json.load handles null as None)
            # Create schema object
            shift_create = schemas.ShiftDefinitionCreate(**shift_dict)
            crud.create_shift_definition(db, shift_create)
            
        print("Shifts loaded successfully.")
        
    except Exception as e:
        print(f"ERROR loading shifts from JSON: {e}")
