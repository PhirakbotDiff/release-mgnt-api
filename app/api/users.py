from fastapi import APIRouter, Depends
from app.auth.security import get_current_user, get_db
from app.schemas.user import UserProfile, UserUpdate
from app.models.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserProfile)
def get_my_profile(user: User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserProfile)
def update_user_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if payload.firstname is not None:
            current_user.firstname = payload.firstname

        if payload.lastname is not None:
            current_user.lastname = payload.lastname

        if payload.email is not None:
            current_user.email = payload.email

        if payload.bio is not None:
            current_user.bio = payload.bio

        db.commit()
        db.refresh(current_user)
        return current_user

    except Exception as e:
        db.rollback()
        raise e
