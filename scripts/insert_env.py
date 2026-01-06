from app.database import SessionLocal
from app.models.environment import Environment
from app.auth.auth import get_password_hash

db = SessionLocal()

environments_to_add = [
    {"name": "PROD", "description": "Live user-facing environment."},
    {"name": "UAT", "description": "User Acceptance Testing environment."},
    {"name": "DEV", "description": "Internal sandbox for feature development."},
    # {"name": "Staging", "description": "Pre-production environment for final testing."},
    # {"name": "Lab", "description": "Experimental environment for R&D."}
]
try:
    # Convert dictionaries to model objects
    for env_data in environments_to_add:
        # Check if environment already exists to avoid Unique Constraint errors
        exists = db.query(Environment).filter(Environment.name == env_data["name"]).first()
        if not exists:
            new_env = Environment(**env_data)
            db.add(new_env)
            
    db.commit()
    print(f"Successfully created {len(environments_to_add)} environments.")

except Exception as e:
    db.rollback()
    print(f"Error during bulk insert: {e}")
finally:
    db.close()