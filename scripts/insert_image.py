from app.database import SessionLocal
from app.models.image import Image, ScanStatus
from app.auth.auth import get_password_hash

db = SessionLocal()

images_data = [
    # {
    #     "service_id": "product-service",
    #     "latest_version_scan": "v1.0.1",
    #     "environment_id": "UAT",
    #     "status": ScanStatus.SUCCESS,
    #     "critical": 0,
    #     "high": 2,
    #     "medium": 5,
    #     "low": 1,
    #     "namespace": "default",
    # },
    # {
    #     "service_id": "order-service",
    #     "latest_version_scan": "v2.3.0",
    #     "environment_id": "UAT",
    #     "status": ScanStatus.WARNING,
    #     "critical": 1,
    #     "high": 3,
    #     "medium": 7,
    #     "low": 4,
    #     "namespace": "default",
    # },
    # {
    #     "service_id": "sfa-admin-service",
    #     "latest_version_scan": "v1.0.1",
    #     "environment_id": "UAT",
    #     "status": "SUCCESS",
    #     "critical": 0,
    #     "high": 0,
    #     "medium": 0,
    #     "low": 0,
    #     "namespace": "sfa",
    # },
    # {
    #     "service_id": "sfa-salesperson-service",
    #     "latest_version_scan": "v1.0.1",
    #     "environment_id": "UAT",
    #     "status": "SUCCESS",
    #     "critical": 0,
    #     "high": 0,
    #     "medium": 0,
    #     "low": 0,
    #     "namespace": "sfa",
    # },
    # {
    #     "service_id": "sfa-dp-service",
    #     "latest_version_scan": "v1.0.1",
    #     "environment_id": "UAT",
    #     "status": "SUCCESS",
    #     "critical": 0,
    #     "high": 0,
    #     "medium": 0,
    #     "low": 0,
    #     "namespace": "sfa",
    # },
    {
        "service_id": "nuxt-app",
        "latest_version_scan": "v1.0.6",
        "environment_id": "UAT",
        "status": ScanStatus.SUCCESS,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "namespace": "default",
    },
]

try:
    # Convert dictionaries to model objects
    new_images = [Image(**data) for data in images_data]

    # Bulk insert
    db.add_all(new_images)
    db.commit()

    print(f"Successfully created {len(new_images)} images.")

except Exception as e:
    db.rollback()
    raise e
finally:
    db.close()