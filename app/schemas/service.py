from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional
from datetime import datetime

# Shared properties
class ServiceBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    manifest_path: Optional[str] = None
    gitlab_url: Optional[str] | None = None
    namespace: Optional[str] = None

# Properties to receive on service creation
class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    pass

# Properties to return to client (includes ID)
class Service(ServiceBase):
    id: int
    slug: str
    created_at: str | datetime | None
    created_by: str | int | None
    created_position: str | None = None
    updated_at: str | datetime | None = None

    image: dict | None = {}
    
    @field_serializer("created_at")
    def serialize_created_at(self, v: datetime) -> str:
        return v.strftime("%d %b, %Y")
    
    @field_serializer("updated_at")
    def serialize_updated_at(self, v: datetime) -> str:
        return v.strftime("%d %b, %Y")
    
    # This allows Pydantic to read data from SQLAlchemy models (ORM)
    model_config = ConfigDict(from_attributes=True)