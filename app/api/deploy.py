from fastapi import Depends, APIRouter, HTTPException, BackgroundTasks # type: ignore
from app.schemas.deploy import DeployRequest, DeployResponse
from app.auth.security import get_current_user, get_db
from sqlalchemy.orm import Session
from app.models.deploy import Deployment
from app.utils.bgtask import run_deploy_job

# from app.services.git_service import GitService
# from app.services.manifest_service import ManifestService

router = APIRouter(prefix="/deploy", tags=["Deploy"])

@router.post("/")
async def deploy(
    req: DeployRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user= Depends(get_current_user)
):
    try:
        

        # git = GitService(repo_path=manifest_repo_path)
        # manifest = ManifestService()
        
        # git.clone_or_pull()
        # manifest.update_image_tag(
        #     manifest_repo_path,
        #     req.service,
        #     req.environment,
        #     req.image_tag
        # )

        # commit_id = git.commit_and_push(
        #     f"deploy({req.service}): {req.image_tag} to {req.environment}"
        # )

        # 1️⃣ Insert deployment record
        deployment = Deployment(
            service=req.service,
            environment=req.environment,
            image_tag=req.image_tag,
            git_tag=req.git_tag,
            status="PENDING",
            created_by=user.id
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
        )

        # 3️⃣ Return immediately
        return DeployResponse(
            status="accepted",
            message="Deployment started",
            deployment_id=deployment.id
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
