from fastapi import APIRouter, Depends
from app.auth.security import get_current_user
from app.schemas.user import UserProfile
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserProfile)
def get_my_profile(user: User = Depends(get_current_user)):
    return user
