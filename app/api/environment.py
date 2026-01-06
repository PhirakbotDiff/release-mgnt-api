from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.models.environment import Environment as EnvironmentModel
from app.schemas.environment import Environment, EnvironmentCreate, EnvironmentUpdate
from app.auth.security import get_current_user, get_db
from app.models.user import User

router = APIRouter(prefix="/environments", tags=["Environments"])

@router.post(
    "/", 
    response_model=Environment, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new environment"
)
def create_environment(
    env_in: EnvironmentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a deployment environment (e.g., Production, Staging).
    Requires an authenticated user.
    """
    db_env = EnvironmentModel(**env_in.model_dump())
    
    try:
        db.add(db_env)
        db.commit()
        db.refresh(db_env)
        return db_env
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Environment with name '{env_in.name}' already exists."
        )

@router.get("/", response_model=List[Environment])
def list_environments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch all available environments."""
    return db.query(EnvironmentModel).all()


@router.get("/{env_id}", response_model=Environment)
def get_environment(
    env_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch a specific environment by its ID."""
    db_env = db.query(EnvironmentModel).filter(EnvironmentModel.id == env_id).first()
    if not db_env:
        raise HTTPException(status_code=404, detail="Environment not found")
    return db_env


@router.delete("/{env_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(
    env_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove an environment. Use with caution."""
    db_env = db.query(EnvironmentModel).filter(EnvironmentModel.id == env_id).first()
    if not db_env:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    db.delete(db_env)
    db.commit()
    return None


@router.put("/{env_id}", response_model=Environment)
def update_environment(
    env_id: int,
    env_in: EnvironmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_env = db.query(EnvironmentModel).filter(EnvironmentModel.id == env_id).first()
    if not db_env:
        raise HTTPException(status_code=404, detail="Environment not found")

    update_data = env_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_env, field, value)

    try:
        db.commit()
        db.refresh(db_env)
        return db_env
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Environment name already exists")