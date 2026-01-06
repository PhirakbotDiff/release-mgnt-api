from pydantic import BaseModel, Field, constr

class DeployRequest(BaseModel):
    service: str # order-service
    environment: str # uat
    image_tag: str # v1.0.1
    git_tag: str

class DeployResponse(BaseModel):
    status: str
    message: str
    commit_id: str | None = None