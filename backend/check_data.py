from sqlalchemy import create_engine, text
import os

DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/intern_schedule"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM shift_definitions"))
    count = result.scalar()
    print(f"Shift definitions count: {count}")
    
    if count > 0:
        print("Data verification successful.")
    else:
        print("Data verification failed: Table is empty.")
