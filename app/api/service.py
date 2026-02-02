from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.paginaiton import PaginatedResponse
from app.auth.security import get_current_user, get_db
from app.models.user import User
from app.schemas.service import Service, ServiceCreate, ServiceUpdate
from app.models.service import Service as ServiceModel
from app.models.image import Image as ImageModel

router = APIRouter(prefix="/services", tags=["Services"])

@router.post("/create", response_model=Service, summary="Create a new service",)
def create_service(
    service: ServiceCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    # 1️⃣ Check existing service by slug
    existing_service = (
        db.query(ServiceModel)
        .filter(ServiceModel.slug == service.slug)
        .first()
    )

    if existing_service:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service with this slug already exists",
        )
    
    try:
        # The 'service' variable is already validated by Pydantic here
        db_service = ServiceModel(
            **service.model_dump(),
            created_by=current_user.id
        )
        db.add(db_service)

        db_image = ImageModel(
            service_id=service.slug,
            latest_version_scan="latest",
            environment_id="UAT",
            status="INIT",
            critical=0,
            high=0,
            medium=0,
            low=0,
            namespace=service.namespace,
        )
        db.add(db_image)

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
        print("e",e)
        db.rollback()
        # Log the error here for internal debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the service."
        )

@router.get("/list", response_model=PaginatedResponse[Service], summary="List all services")
def read_services(
    page: int = 1,
    size: int = 10,
    search: str | None = None,
    namespace: str | None = None,
    slug: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    list_data = []

    # list_data = db.query(ServiceModel).all()

    q = db.query(ServiceModel, User).\
        join(User, ServiceModel.created_by == User.id)

    if search:
        q = q.filter(
            ServiceModel.namespace.ilike(f"%{search}%") |
            ServiceModel.description.ilike(f"%{search}%")
        )

    if namespace:
        q = q.filter(ServiceModel.namespace == namespace)

    if slug:
        q = q.filter(ServiceModel.slug == slug)

    total = q.count()

    data = (
        q.order_by(ServiceModel.created_at.desc())
         .offset((page - 1) * size)
         .limit(size)
         .all()
    )

    for deployment, user in data:
        dict_data = {
            "id": deployment.id,
            "name": deployment.name,
            "namespace": deployment.namespace,
            "slug": deployment.slug, 
            "manifest_path": deployment.manifest_path,
            "description": deployment.description,
            "created_by": "%s %s" % (user.firstname, user.lastname),
            "created_at": user.created_at,
            "created_position": user.role,
            "updated_at": user.updated_at

        }
        list_data.append(dict_data)

    return {
        "data": list_data,
        "meta": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": (total + size - 1) // size,
        },
    }


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