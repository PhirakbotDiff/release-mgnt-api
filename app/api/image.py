from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.auth.security import get_current_user, get_db
from app.models.user import User
from app.schemas.paginaiton import PaginatedResponse
from app.schemas.image import ImageCreate, ImageResponse, ImageScanRequest, ImageScanDetailCreate
from app.models.image import Image, ImageScan, ImageScanDetail, ScanStatus
from app.utils.trivy import run_trivy

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/", 
    response_model=ImageResponse, 
    status_code=status.HTTP_201_CREATED
)
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

@router.get("/", 
    response_model=list[ImageResponse],
    status_code=status.HTTP_200_OK
)
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
        }
        list_data.append(dict_data)

    return list_data

@router.get("/{image_id}", 
    response_model=ImageResponse,
    status_code=status.HTTP_200_OK
)
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
        "created_at": images[1].created_at,
        "created_position": images[1].role,
    }
    return dict_data


@router.post("/scans/execute")
def execute_scan(
    payload: ImageScanRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        # 1️⃣ Insert ImageScan (PENDING)
        scan = ImageScan(
            image_id=payload.image_id,
            image_current=payload.image_current,
            image_previous=payload.image_previous,
            environment_id=payload.environment_id,
            status=ScanStatus.PENDING
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

        # 2️⃣ Execute scan
        summary = run_trivy(payload.image_current, payload.severities, payload.insecure)

        summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        vulns = []

        for result in summary.get("Results", []):

            for v in result.get("Vulnerabilities", []):

                sev = v["Severity"]
                stus = v["Status"]
                title = v["Title"]
                summary[sev] = summary.get(sev, 0) + 1

                detail = ImageScanDetail(
                    image_scan_id=scan.id,
                    cve_name=v["id"],
                    severity=v["severity"],
                    status=v["status"],
                    package_name=v["package"],
                    package_version=v["installed"],
                    fixed_version=v["fixed"]
                )
                db.add(detail)
                
                vulns.append({
                    "id": v["VulnerabilityID"],
                    "severity": sev,
                    "status": stus,
                    "title": title,
                    "package": v["PkgName"],
                    "installed": v["InstalledVersion"],
                    "fixed": v.get("FixedVersion"),
                })

        status = (
            "FAIL" if summary.get("CRITICAL", 0) > 0
            else "WARN" if summary.get("HIGH", 0) > 0
            else "PASS"
        )

        # 3️⃣ Update ImageScan with result
        scan.status = ScanStatus.PENDING if status == "PASS" else ScanStatus.FAIL
        scan.critical = summary.get("CRITICAL", 0)
        scan.high = summary.get("HIGH", 0)
        scan.medium = summary.get("MEDIUM", 0)
        scan.low = summary.get("LOW", 0)

        db.commit()
        db.refresh(scan)

        # 5️⃣ Final response
        return {
            "image_scan": {
                "id": scan.id,
                "image_current": scan.image_current,
                "status": scan.status,
                "summary": summary
            },
            "vulnerabilities": [
                {
                    "cve": d.cve_name,
                    "severity": d.severity,
                    "package": d.package_name,
                    "installed": d.package_version,
                    "fixed": d.fixed_version
                }
                for d in vulns
            ]
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Scan execution failed: {str(e)}"
        )


@router.post("/image-scans/{scan_id}/details")
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


@router.get("/scans/{scan_id}/details")
def list_scan_details(
    scan_id: int,
    db: Session = Depends(get_db)
):
    query = db.query(ImageScanDetail).filter(ImageScanDetail.image_scan_id == scan_id)
    details = query.all()
    return details if details else []