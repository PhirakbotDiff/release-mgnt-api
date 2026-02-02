from app.database import SessionLocal
from app.models.namespace import Namespace

db = SessionLocal()

namespace_to_add = [
    {"name": "default", "description": "Default namespace."},
    {"name": "sfa", "description": "SFA namespace."},
    {"name": "ticket", "description": "Ticket namespace."},
]
try:
    # Convert dictionaries to model objects
    for env_data in namespace_to_add:
        # Check if namespace already exists to avoid Unique Constraint errors
        exists = db.query(Namespace).filter(Namespace.name == env_data["name"]).first()
        if not exists:
            new_env = Namespace(**env_data)
            db.add(new_env)
            
    db.commit()
    print(f"Successfully created {len(namespace_to_add)} namespace.")

except Exception as e:
    db.rollback()
    print(f"Error during bulk insert: {e}")
finally:
    db.close()