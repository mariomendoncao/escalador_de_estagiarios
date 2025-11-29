#!/usr/bin/env python3
"""
Script to drop all tables and recreate them with the new schema.
WARNING: This will delete all existing data!
"""

from app.database import engine, Base
from app import models

def reset_database():
    print("WARNING: This will drop all existing tables and data!")
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() != 'yes':
        print("Aborted.")
        return

    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")

    print("Creating new tables with updated schema...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    print("\nDatabase has been reset. You can now start fresh with the new schema.")

if __name__ == "__main__":
    reset_database()
