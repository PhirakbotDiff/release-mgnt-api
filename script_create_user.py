from app.database import SessionLocal
from app.models.user import User
from app.auth.auth import get_password_hash

db = SessionLocal()

user = User(
    username="admin",
    password_hash=get_password_hash("admin"),
    role="lead"
)

db.add(user)
db.commit()
print("User created")
