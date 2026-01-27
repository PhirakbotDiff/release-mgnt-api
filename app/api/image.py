from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy import case
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.auth.security import get_current_user, get_db
from app.models.user import User
from app.schemas.paginaiton import PaginatedResponse
from app.schemas.image import ImageCreate, ImageResponse, ImageScanRequest, ImageScanDetailCreate
from app.models.image import Image, ImageScan, ImageScanDetail, ScanStatus
from app.logics.image import run_scan_task
from app.database import SessionLocal


router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
def create_image(
    payload: ImageCreate, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    image = Image(**payload.dict())
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@router.get("/", response_model=list[ImageResponse], status_code=status.HTTP_200_OK)
def list_images(
    environment_id: str | None = Query(None),
    status: ScanStatus | None = Query(None),
    namespace: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Image, User).\
        join(User, Image.created_by == User.id)

    if environment_id:
        query = query.filter(Image.environment_id == environment_id)

    if namespace:
        query = query.filter(Image.namespace == namespace)

    if status:
        query = query.filter(Image.status == status)

    images = query.all()

    list_data = []
    for image, user in images:
        dict_data = {
            "id": image.id,
            "service_id": image.service_id,
            "latest_version_scan": image.latest_version_scan,
            "environment_id": image.environment_id,
            "status": image.status,
            "critical": image.critical,
            "high": image.high,
            "medium": image.medium,
            "low": image.low,
            "namespace": image.namespace,
            "created_by": "%s %s" % (user.firstname, user.lastname) if user else "N/A",
            "created_at": user.created_at if user else "N/A",
            "created_position": user.role if user else "N/A",
            "updated_at": user.updated_at if user else None
        }
        list_data.append(dict_data)

    return list_data


@router.get("/{image_id}", response_model=ImageResponse, status_code=status.HTTP_200_OK)
def get_images(
    image_id: int,
    db: Session = Depends(get_db),
):
    images = (
        db.query(Image, User).\
            filter(Image.id == image_id).\
            join(User, Image.created_by == User.id)
    ).first()

    dict_data = {
        "id": images[0].id,
        "service_id": images[0].service_id,
        "latest_version_scan": images[0].latest_version_scan,
        "environment_id": images[0].environment_id,
        "status": images[0].status,
        "critical": images[0].critical,
        "high": images[0].high,
        "medium": images[0].medium,
        "low": images[0].low,
        "namespace": images[0].namespace,
        "created_by": "%s %s" % (images[1].firstname, images[1].lastname),
        "created_at": images[0].created_at,
        "created_position": images[1].role,
        "updated_at": images[0].updated_at
    }
    return dict_data


@router.post("/scans/execute")
def execute_scan(
    payload: ImageScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:

        scan = ImageScan(
            image_id=payload.image_id,
            image_current=payload.image_current,
            image_previous=payload.image_previous,
            environment_id=payload.environment_id,
            status=ScanStatus.QUEUE,
            progress=0,
            message="Queued",
            created_by=user.id
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        background_tasks.add_task(
            run_scan_task,
            scan.id,
            payload,
            SessionLocal
        )

        return {
            "scan_id": scan.id,
            "status": scan.status,
            "progress": scan.progress
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Scan execution failed: {str(e)}"
        )


@router.get("/scans/{scan_id}/progress")
def get_scan_progress(
    scan_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    scan = db.query(ImageScan).filter(ImageScan.id == scan_id).first()

    if not scan:
        raise HTTPException(404, "Scan not found")

    return {
        "id": scan.id,
        "progress": scan.progress,
        "status": scan.status,
        "message": scan.message,
        "summary": {
            "critical": scan.critical,
            "high": scan.high,
            "medium": scan.medium,
            "low": scan.low,
        }
    }


@router.post("/scans/{scan_id}/details")
def create_scan_detail(
    scan_id: int,
    payload: ImageScanDetailCreate,
    db: Session = Depends(get_db)
):
    detail = ImageScanDetail(
        image_scan_id=scan_id,
        **payload.dict()
    )
    db.add(detail)
    db.commit()
    return {"message": "Scan detail added"}


@router.get("/scans/{scan_id}/vulnerabilities")
def list_scan_details(
    scan_id: int,
    page: int = 1,
    size: int = 10,
    search: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db)
):
    
    severity_order = case(
        (ImageScanDetail.severity == "CRITICAL", 1),
        (ImageScanDetail.severity == "HIGH", 2),
        (ImageScanDetail.severity == "MEDIUM", 3),
        (ImageScanDetail.severity == "LOW", 4),
        else_=5
    )
        
    query = db.query(ImageScanDetail).\
        filter(ImageScanDetail.image_scan_id == scan_id).\
        order_by(severity_order)
    
    if search:
        query = query.filter(
            ImageScanDetail.severity.ilike(f"%{search}%")
        )
    
    if status:
        query = query.filter(
            ImageScanDetail.status == status
        )

    total = query.count()

    details = query.all()
    details = details if details else {}

    return {
        "data": details,
        "meta": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": (total + size - 1) // size,
        },
    }