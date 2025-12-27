from fastapi import Depends, APIRouter, HTTPException
from app.schemas import DeployRequest, DeployResponse
from app.auth.security import get_current_user
from app.services.git_service import GitService
from app.services.manifest_service import ManifestService

router = APIRouter(prefix="/deploy", tags=["Deploy"])

@router.post("/")
def deploy(
    req: DeployRequest,
    user=Depends(get_current_user)
):
    try:
        git = GitService()
        manifest = ManifestService()
        
        git.clone_or_pull()
        manifest.update_image_tag(
            req.service,
            req.environment,
            req.image_tag
        )

        commit_id = git.commit_and_push(
            f"deploy({req.service}): {req.image_tag} to {req.environment}"
        )

        return DeployResponse(
            status="success",
            message="Deployment triggered",
            commit_id=commit_id
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
