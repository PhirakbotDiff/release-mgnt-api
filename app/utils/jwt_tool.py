from jose import jwt
from datetime import datetime, timedelta

SECRET = "super-secret"
ALGO = "HS256"

def create_token(user_id: str):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)
