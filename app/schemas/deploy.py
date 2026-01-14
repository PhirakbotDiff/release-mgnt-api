from pydantic import BaseModel, Field, constr, ConfigDict, model_serializer # type: ignore
from typing import Literal, Dict
from datetime import datetime

class DeployRequest(BaseModel):
    service: str # order-service
    environment: str # uat
    image_tag: str # v1.0.1
    git_tag: str
    description: str | None

class DeployResponse(BaseModel):
    id: int | str
    status: str
    message: str
    commit_id: str | None = None

# Properties to return to client (includes ID)
class Deploy(DeployRequest):
    id: int
    status: Literal["SUCCESS", "FAILED", "RUNNING", "PENDING"]
    created_by: str | None = ""
    created_position: str | None = ""
    git_short_commit: str | None = ""
    git_commit: str | None = ""
    created_at: str | datetime | None

    @model_serializer
    def serialize(self):
        return {
            "id": self.id,
            "service": self.service,
            "env": self.environment.upper(),
            "tag": {"images": self.image_tag, "git": self.git_tag},
            "description": self.description,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.strftime("%d %b, %Y"),
            "created_position": self.created_position.upper(),
            "git_short_commit": self.git_short_commit,
            "git_commit": self.git_commit,
        }

    # This allows Pydantic to read data from SQLAlchemy models (ORM)
    model_config = ConfigDict(from_attributes=True)


class ListDeploy(DeployRequest):
    id: int
    status: Literal["SUCCESS", "FAILED", "RUNNING", "PENDING"]
    created_by: str | None = ""

    @model_serializer
    def serialize(self):
        return {
            "id": self.id,
            "service": self.service,
            "env": self.environment,
            "tag": {"images": self.image_tag, "git": self.git_tag},
            "description": self.description,
            "status": self.status,
            "created_by": self.created_by,
        }

    # This allows Pydantic to read data from SQLAlchemy models (ORM)
    model_config = ConfigDict(from_attributes=True)