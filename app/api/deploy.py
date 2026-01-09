from fastapi import Depends, APIRouter, HTTPException, BackgroundTasks # type: ignore
from app.schemas.deploy import DeployRequest, Deploy, DeployResponse
from app.auth.security import get_current_user, get_db
from sqlalchemy.orm import Session # type: ignore
from app.models.deploy import Deployment as DeploymentModel
from app.models.user import User
from app.utils.bgtask import run_deploy_job

# from app.services.git_service import GitService
# from app.services.manifest_service import ManifestService

router = APIRouter(prefix="/deploy", tags=["Deploy"])

@router.post("/", response_model=Deploy)
async def deploy(
    req: DeployRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:

        # 1️⃣ Insert deployment record
        deployment = DeploymentModel(
            service=req.service,
            environment=req.environment,
            image_tag=req.image_tag,
            git_tag=req.git_tag,
            status="PENDING",
            created_by=user.id,
            description=req.description
        )

        db.add(deployment)
        db.commit()
        db.refresh(deployment)

        # 2️⃣ Run deployment in background
        background_tasks.add_task(
            run_deploy_job,
            deployment.id,
            req.service,
            req.environment,
            req.image_tag,
            git_tag=req.git_tag,
            description=req.description
        )

        # 3️⃣ Return immediately
        return DeployResponse(
            status="accepted",
            message="Deployment started",
            deployment_id=deployment.id
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[Deploy], summary="List all deployment")
async def get_deploy(
    db: Session = Depends(get_db),
    user= Depends(get_current_user)
):
    
    data = [
        {
            "id": 101,
            "service": "order-service",
            "environment": "UAT",
            "image_tag": "v1.0.1", 
            "git_tag": "v1.0.1",
            "description": "Deploy order-service v1.0.1 to UAT",
            "status": "SUCCESS",
            "created_by": "release-bot"
        },
        {
            "id": 102,
            "service": "payment-service",
            "environment": "PROD",
            "image_tag": "v2.3.0", 
            "git_tag": "v2.3.0",
            "description": "Hotfix deploy payment-service v2.3.0",
            "status": "RUNNING",
            "created_by": "devops-user"
        },
        {
            "id": 103,
            "service": "inventory-service",
            "environment": "PROD",
            "image_tag": "v1.2.5", 
            "git_tag": "v1.2.5",
            "description": "Production release inventory-service v1.2.5",
            "status": "FAILED",
            "created_by": "release-bot"
        },
        {
            "id": 104,
            "service": "user-service",
            "environment": "STAGING",
            "image_tag": "v3.1.2", 
            "git_tag": "v3.1.2",
            "description": "Feature rollout user-service v3.1.2 to staging",
            "status": "SUCCESS",
            "created_by": "ci-cd-pipeline"
        },
        {
            "id": 105,
            "service": "notification-service",
            "environment": "PROD",
            "image_tag": "v4.0.0", 
            "git_tag": "v4.0.0",
            "description": "Major release notification-service v4.0.0",
            "status": "SUCCESS",
            "created_by": "release-bot"
        },
        {
            "id": 106,
            "service": "cart-service",
            "environment": "UAT",
            "image_tag": "v1.5.3", 
            "git_tag": "v1.5.3",
            "description": "Deploy cart-service v1.5.3 for testing",
            "status": "RUNNING",
            "created_by": "qa-engineer"
        },
        {
            "id": 107,
            "service": "auth-service",
            "environment": "PROD",
            "image_tag": "v2.8.1", 
            "git_tag": "v2.8.1",
            "description": "Security patch auth-service v2.8.1",
            "status": "SUCCESS",
            "created_by": "security-team"
        },
        {
            "id": 108,
            "service": "search-service",
            "environment": "DEV",
            "image_tag": "v0.9.0", 
            "git_tag": "feature/search-v2",
            "description": "Deploy experimental search-service to dev",
            "status": "FAILED",
            "created_by": "developer-john"
        },
        {
            "id": 109,
            "service": "analytics-service",
            "environment": "PROD",
            "image_tag": "v5.2.4", 
            "git_tag": "v5.2.4",
            "description": "Monthly rollout analytics-service v5.2.4",
            "status": "SUCCESS",
            "created_by": "release-bot"
        },
        {
            "id": 110,
            "service": "shipping-service",
            "environment": "UAT",
            "image_tag": "v2.0.0", 
            "git_tag": "v2.0.0",
            "description": "New major version shipping-service to UAT",
            "status": "SUCCESS",
            "created_by": "ci-cd-pipeline"
        },
        {
            "id": 111,
            "service": "review-service",
            "environment": "PROD",
            "image_tag": "v1.3.7", 
            "git_tag": "v1.3.7",
            "description": "Bugfix deploy review-service v1.3.7",
            "status": "RUNNING",
            "created_by": "devops-user"
        },
        {
            "id": 112,
            "service": "recommendation-service",
            "environment": "STAGING",
            "image_tag": "v3.4.1", 
            "git_tag": "v3.4.1",
            "description": "Deploy recommendation-service for QA validation",
            "status": "SUCCESS",
            "created_by": "release-bot"
        },
        {
            "id": 113,
            "service": "catalog-service",
            "environment": "PROD",
            "image_tag": "v6.1.0", 
            "git_tag": "v6.1.0",
            "description": "Feature release catalog-service v6.1.0",
            "status": "FAILED",
            "created_by": "ci-cd-pipeline"
        },
        {
            "id": 114,
            "service": "fraud-service",
            "environment": "PROD",
            "image_tag": "v1.9.9", 
            "git_tag": "hotfix/fraud-detection",
            "description": "Emergency hotfix fraud-service",
            "status": "SUCCESS",
            "created_by": "oncall-engineer"
        },
        {
            "id": 115,
            "service": "billing-service",
            "environment": "UAT",
            "image_tag": "v2.2.2", 
            "git_tag": "v2.2.2",
            "description": "Testing billing-service v2.2.2 in UAT",
            "status": "RUNNING",
            "created_by": "qa-engineer"
        },
        {
            "id": 116,
            "service": "api-gateway",
            "environment": "PROD",
            "image_tag": "v4.5.6", 
            "git_tag": "v4.5.6",
            "description": "Routine update api-gateway v4.5.6",
            "status": "SUCCESS",
            "created_by": "release-bot"
        },
        {
            "id": 117,
            "service": "checkout-service",
            "environment": "PROD",
            "image_tag": "v3.0.1", 
            "git_tag": "v3.0.1",
            "description": "Post-holiday patch checkout-service",
            "status": "SUCCESS",
            "created_by": "devops-user"
        },
        {
            "id": 118,
            "service": "email-service",
            "environment": "STAGING",
            "image_tag": "v1.7.0", 
            "git_tag": "v1.7.0",
            "description": "Deploy email-service to staging",
            "status": "FAILED",
            "created_by": "ci-cd-pipeline"
        },
        {
            "id": 119,
            "service": "logging-service",
            "environment": "PROD",
            "image_tag": "v2.4.8", 
            "git_tag": "v2.4.8",
            "description": "Performance improvement logging-service",
            "status": "SUCCESS",
            "created_by": "release-bot"
        },
        {
            "id": 120,
            "service": "promotion-service",
            "environment": "UAT",
            "image_tag": "v1.1.0", 
            "git_tag": "v1.1.0",
            "description": "New promotion engine testing in UAT",
            "status": "RUNNING",
            "created_by": "product-team"
        }
        ]

    return data # db.query(DeploymentModel).all()


