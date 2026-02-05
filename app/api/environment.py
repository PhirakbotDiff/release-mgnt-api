from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime

from app.models.environment import Environment as EnvironmentModel
from app.schemas.environment import Environment, EnvironmentCreate, EnvironmentUpdate
from app.auth.security import get_current_user, get_db
from app.models.user import User

router = APIRouter(prefix="/environments", tags=["Environments"])

@router.post(
    "/create", 
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
    now = datetime.utcnow()

    db_env = EnvironmentModel(
        **env_in.model_dump(),
        created_at = now,
        created_by=current_user.id
    )
    
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

@router.get("/list", response_model=List[Environment])
def list_environments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch all available environments."""
    return db.query(EnvironmentModel).all()


@router.get("/get/{env_id}", response_model=Environment)
def get_environment(
    env_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch a specific environment by its ID."""
    env_obj = db.query(
            EnvironmentModel,
            User,
        ).\
        join(User, EnvironmentModel.created_by == User.id).\
        filter(EnvironmentModel.id == env_id).\
        first()
    
    if not env_obj:
        raise HTTPException(
            status_code=404, 
            detail="Environment not found"
        )
    
    dict_data = {
        "id": env_obj[0].id,
        "name": env_obj[0].name,
        "description": env_obj[0].description,
        "created_by": "%s %s" % (env_obj[1].firstname, env_obj[1].lastname),
        "created_at": env_obj[1].created_at,
        "created_position": env_obj[1].role,
        "updated_at": env_obj[1].updated_at
    }

    return dict_data


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


@router.put("/update/{env_id}", response_model=Environment)
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