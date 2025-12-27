from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.auth.security import SECRET_KEY, ALGORITHM
import bcrypt

from app.config import settings


# Replace your pwd_context
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# def verify_password(plain, hashed):
#     return pwd_context.verify(plain, hashed)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": get_password_hash("admin"),
        "role": "developer"
    },
    "bob": {
        "username": "bob",
        "hashed_password": get_password_hash("admin"),
        "role": "lead"
    }
}