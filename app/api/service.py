from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.auth.security import get_current_user, get_db
from app.models.user import User
from app.schemas.service import Service, ServiceCreate, ServiceUpdate
from app.models.service import Service as ServiceModel

router = APIRouter(prefix="/services", tags=["Services"])

@router.post("/create", response_model=Service, summary="Create a new service",)
def create_service(
    service: ServiceCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # The 'service' variable is already validated by Pydantic here
    db_service = ServiceModel(**service.model_dump())
    try:
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service with slug '{service.slug}' already exists."
        )
    except Exception as e:
        db.rollback()
        # Log the error here for internal debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the service."
        )

@router.get("/list", response_model=list[Service], summary="List all services")
def read_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(ServiceModel).all()


@router.put("/get/{service_id}", response_model=Service)
def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Convert input data to a dict, excluding unset fields
    update_data = service_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_service, field, value)

    try:
        db.commit()
        db.refresh(db_service)
        return db_service
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Slug already exists")