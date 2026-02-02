from fastapi import Depends, APIRouter, HTTPException, BackgroundTasks # type: ignore
from app.schemas.deploy import DeployRequest, Deploy, ListDeploy, DeployResponse
from app.schemas.paginaiton import PaginatedResponse
from app.auth.security import get_current_user, get_db
from sqlalchemy.orm import Session, joinedload # type: ignore
from app.models.deploy import Deployment as DeploymentModel
from app.models.service import Service as ServiceModel
from app.models.user import User
from app.utils.bgtask import run_deploy_job

# from app.services.git_service import GitService
# from app.services.manifest_service import ManifestService

router = APIRouter(prefix="/deploy", tags=["Deploy"])


@router.post("/create", response_model=DeployResponse)
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

        # query to get service info
        service_obj = db.query(ServiceModel) \
            .filter(ServiceModel.slug == str(req.service)) \
            .first()

        print("service_obj", service_obj)
        # 2️⃣ Run deployment in background
        background_tasks.add_task(
            run_deploy_job,
            deployment.id,
            req.service,
            req.environment,
            req.image_tag,
            service_obj.manifest_path,
        )

        # 3️⃣ Return immediately
        return DeployResponse(
            status="accepted",
            message="Deployment started",
            deployment_id=deployment.id,
            id=deployment.id
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", 
    response_model=PaginatedResponse[ListDeploy], 
    summary="List all deployment"
)
async def get_deploy(
    page: int = 1,
    size: int = 10,
    search: str | None = None,
    status: str | None = None,
    env: str | None = None,
    db: Session = Depends(get_db),
    user= Depends(get_current_user)
):
    
    list_data = []

    q = db.query(DeploymentModel, User).join(User, DeploymentModel.created_by == User.id)

    if search:
        q = q.filter(
            DeploymentModel.service.ilike(f"%{search}%") |
            DeploymentModel.env.ilike(f"%{search}%")
        )

    if status:
        q = q.filter(DeploymentModel.status == status)

    if env:
        q = q.filter(DeploymentModel.env == env)

    total = q.count()

    data = (
        q.order_by(DeploymentModel.created_at.desc())
         .offset((page - 1) * size)
         .limit(size)
         .all()
    )

    for deployment, user in data:
        dict_data = {
            "id": deployment.id,
            "service": deployment.service,
            "environment": deployment.environment,
            "image_tag": deployment.image_tag, 
            "git_tag": deployment.git_tag,
            "description": deployment.description,
            "status": deployment.status,
            "created_by": user.username
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


@router.get(
    "/get/{deploy_id}",
    response_model=Deploy,
    summary="Get deployment by ID"
)
def get_deployment_by_id(
    deploy_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deployment = (
        db.query(DeploymentModel, User)
        .join(User, DeploymentModel.created_by == User.id)
        .filter(DeploymentModel.id == int(deploy_id))
        .first()
    )

    if not deployment:
        raise HTTPException(
            status_code=404,
            detail="Deployment not found"
        )
    
    # for deploy, user in deployment:
    dict_data = {
        "id": deployment[0].id,
        "service": deployment[0].service,
        "environment": deployment[0].environment,
        "image_tag": deployment[0].image_tag, 
        "git_tag": deployment[0].git_tag,
        "description": deployment[0].description,
        "status": deployment[0].status,
        "created_by": "%s %s" % (deployment[1].firstname, deployment[1].lastname),
        "created_at": deployment[1].created_at,
        "created_position": deployment[1].role,
        "git_commit": deployment[0].commit_id if deployment[0].commit_id else "N/A",
        "git_short_commit": deployment[0].commit_id[:6] if deployment[0].commit_id else "N/A",
    }
    return dict_data
