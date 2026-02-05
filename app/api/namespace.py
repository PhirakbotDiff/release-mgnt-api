from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime

from app.models.namespace import Namespace as NamespaceModel
from app.schemas.namespace import Namespace, NamespaceLOV, NamespaceCreate, NamespaceUpdate
from app.auth.security import get_current_user, get_db
from app.models.user import User

router = APIRouter(prefix="/namespaces", tags=["Namespaces"])

@router.post(
    "/create", 
    response_model=Namespace, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new namespace"
)
def create_namespace(
    ns_in: NamespaceCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a deployment namespace (e.g., sfa, default).
    Requires an authenticated user.
    """
    now = datetime.utcnow()
    
    db_env = NamespaceModel(
        created_at = now,
        created_by=current_user.id,
        **ns_in.model_dump()
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
            detail=f"Namespace with name '{ns_in.name}' already exists."
        )

@router.get("/list", response_model=List[Namespace])
def list_namespaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch all available namepsaces."""
    return db.query(NamespaceModel).all()


@router.get("/get/{ns_id}", response_model=Namespace)
def get_namespace(
    ns_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch a specific namepsace by its ID."""
    db_env = db.query(NamespaceModel).filter(NamespaceModel.id == ns_id).first()
    if not db_env:
        raise HTTPException(status_code=404, detail="Namepsace not found")
    return db_env


@router.delete("/{ns_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_namespace(
    ns_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove an namepsace. Use with caution."""
    db_env = db.query(NamespaceModel).filter(NamespaceModel.id == ns_id).first()
    if not db_env:
        raise HTTPException(status_code=404, detail="Namepsace not found")
    
    db.delete(db_env)
    db.commit()
    return None


@router.put("/{ns_id}", response_model=Namespace)
def update_namespace(
    ns_id: int,
    env_in: NamespaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_env = db.query(NamespaceModel).filter(NamespaceModel.id == ns_id).first()
    if not db_env:
        raise HTTPException(status_code=404, detail="Namepsace not found")

    update_data = env_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_env, field, value)

    try:
        db.commit()
        db.refresh(db_env)
        return db_env
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Namepsace name already exists")