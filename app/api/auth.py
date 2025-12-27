from fastapi import APIRouter, HTTPException, Depends
from app.auth.auth import authenticate_user, create_access_token
from app.auth.security import ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth.service import authenticate_user
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": user.username,
        "role": user.role,
        "user_id": user.id
    })

    return {"access_token": token, "token_type": "bearer"}
