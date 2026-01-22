from app.database import SessionLocal
from app.models.service import Service
from app.auth.auth import get_password_hash

db = SessionLocal()

services_data = [
    # {
    #     "name": "SFA Admin Portal",
    #     "slug": "sfa-admin-service",
    #     "description": "Administrative interface for Sales Force Automation management.",
    #     "manifest_path": "charts/sfa-admin-service",
    #     "gitlab_url": "https://gitscm.vattanacbrewery.com/devops/manifest_repo.git",
    #     "namespace": "sfa"
    # },
    # {
    #     "name": "SFA Salesperson App",
    #     "slug": "sfa-salesperson-service",
    #     "description": "Backend services for the salesperson mobile application.",
    #     "manifest_path": "charts/sfa-salesperson-service",
    #     "gitlab_url": "https://gitscm.vattanacbrewery.com/devops/manifest_repo.git",
    #     "namespace": "sfa"
    # },
    # {
    #     "name": "SFA DP Service",
    #     "slug": "sfa-dp-service",
    #     "description": "Data Processing and distribution services for SFA modules.",
    #     "manifest_path": "charts/sfa-dp-service",
    #     "gitlab_url": "https://gitscm.vattanacbrewery.com/devops/manifest_repo.git",
    #     "namespace": "sfa"
    # },
    # {
    #     "name": "Telegram Notification Service",
    #     "slug": "telegram-service",
    #     "description": "Internal bot service for automated alerts and notifications via Telegram.",
    #     "manifest_path": "charts/telegram-service",
    #     "gitlab_url": "https://gitscm.vattanacbrewery.com/devops/manifest_repo.git",
    #     "namespace": "internal"
    # },
    # {
    #     "name": "Order Service",
    #     "slug": "order-service",
    #     "description": "Internal bot service for automated alerts and notifications via Telegram.",
    #     "manifest_path": "charts/order-service",
    #     "gitlab_url": "https://gitscm.vattanacbrewery.com/devops/manifest_repo.git",
    #     "namespace": "default"
    # },
    {
        "name": "Nuxt App Service",
        "slug": "nuxt-app",
        "description": "Internal bot service for automated alerts and notifications via Telegram.",
        "manifest_path": "charts/nuxt-app",
        "gitlab_url": "https://gitscm.vattanacbrewery.com/devops/manifest_repo.git",
        "namespace": "default"
    }
]
try:
    # Convert dictionaries to model objects
    new_services = [Service(**data) for data in services_data]

    # Use add_all for efficient bulk insertion
    db.add_all(new_services)
    db.commit()
    print(f"Successfully created {len(new_services)} services.")

except Exception as e:
    db.rollback()
    print(f"Error during bulk insert: {e}")
finally:
    db.close()