
from app.auth.security import get_current_user
from app.database import SessionLocal
from app.services.git_service import GitService
from app.services.manifest_service import ManifestService
from app.config import settings

from app.models.deploy import Deployment

def run_deploy_job(
    deployment_id: int,
    service: str,
    environment: str,
    image_tag: str,
):
    db = SessionLocal()  # create NEW session

    try:
        git = GitService(
            repo_path=settings.MANIFEST_LOCAL_PATH  # LOCAL PATH ONLY
        )
        manifest = ManifestService()

        git.clone_or_pull()

        manifest.update_image_tag(
            git.repo_path,
            service,
            environment,
            image_tag
        )

        commit_id = git.commit_and_push(
            f"deploy({service}): {image_tag} to {environment}"
        )

        deployment = db.query(Deployment).get(deployment_id)
        deployment.status = "SUCCESS"
        deployment.commit_id = commit_id

        db.commit()

    except Exception as e:
        deployment = db.query(Deployment).get(deployment_id)
        deployment.status = "FAILED"
        deployment.error_message = str(e)
        db.commit()

    finally:
        db.close()
