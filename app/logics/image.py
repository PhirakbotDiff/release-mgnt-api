

from fastapi import HTTPException
from app.models.image import Image, ImageScan, ImageScanDetail, ScanStatus
from app.utils.trivy import run_trivy
from app.config import settings

from datetime import datetime
import logging

logger = logging.getLogger("api")


def run_scan_task(
    scan_id, 
    payload, 
    db_session_factory
):

    db = db_session_factory()

    try:

        now = datetime.utcnow()

        scan = db.query(ImageScan).filter(ImageScan.id == scan_id).first()

        scan.status = ScanStatus.RUNNING
        scan.progress = 10
        scan.message = "Starting scan"
        db.commit()

        # Run Trivy
        scan.progress = 30
        scan.message = "Pulling image"
        db.commit()

        # convert current image_current to this format
        # 10.20.10.117:5000/product-service-mul:latest
        # Query to get slug-name of service
        image_obj = db.query(Image).filter(Image.id == payload.image_id).first()
        if not image_obj:
            raise HTTPException(status_code=404, detail="Image not found")
        
        service_slug = image_obj.service_id
        image_full_path = f"{settings.IMAGE_REGISTRY_URL}/{service_slug}:{payload.image_current}"

        result = run_trivy(image_full_path)

        scan.progress = 70
        scan.message = "Analyzing vulnerabilities"
        db.commit()

        summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for r in result.get("Results", []):

            for v in r.get("Vulnerabilities", []):
                sev = v["Severity"]
                summary[sev] += 1

                db.add(ImageScanDetail(
                    image_scan_id=scan.id,
                    cve_name=v["VulnerabilityID"],
                    severity=v["Severity"],
                    status=v["Status"],
                    package_name=v["PkgName"],
                    package_version=v["InstalledVersion"],
                    fixed_version=v.get("FixedVersion"),
                ))

        scan.progress = 90
        scan.message = "Finalizing results"

        status = (
            ScanStatus.FAILED if summary["CRITICAL"] > 0
            else ScanStatus.WARNING if summary["HIGH"] > 0
            else ScanStatus.SUCCESS
        )

        scan.status = status
        scan.progress = 100
        scan.critical = summary["CRITICAL"]
        scan.high = summary["HIGH"]
        scan.medium = summary["MEDIUM"]
        scan.low = summary["LOW"]
        scan.message = "Scan completed"
        scan.updated_at = now

        # update current image_current to table Image
        db.query(Image)\
            .filter(Image.id == payload.image_id)\
            .update({
                Image.latest_version_scan: payload.image_current,
                Image.status: status,
                Image.updated_at: now,
            })

        db.commit()

        logger.info(f"run background scan task successfully.")

    except Exception as e:
        logger.exception(f"run background scan task failed {str(e)}")

        # update current image_current to table Image
        db.query(Image)\
            .filter(Image.id == payload.image_id)\
            .update({
                Image.latest_version_scan: payload.image_current,
                Image.status: ScanStatus.FAILED,
                Image.updated_at: now,
            })
        
        scan.status = ScanStatus.FAILED
        scan.progress = 100
        scan.message = str(e)
        scan.updated_at = now
        db.commit()

    finally:
        db.close()
