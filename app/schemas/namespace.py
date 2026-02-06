from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional
from datetime import datetime


class NamespaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class NamespaceCreate(NamespaceBase):
    pass

class NamespaceUpdate(NamespaceBase):
    name: Optional[str] = None
    description: Optional[str] = None

class Namespace(NamespaceBase):
    id: int

    created_at: str | datetime | None
    created_by: str | int | None
    created_position: str | None = None
    updated_at: str | datetime | None = None

    @field_serializer("created_at", check_fields=False)
    def serialize_created_at(self, v: datetime) -> str:
        return v.strftime("%d %b, %Y")
    
    @field_serializer("updated_at", check_fields=False)
    def serialize_updated_at(self, v: datetime) -> str:
        return v.strftime("%d %b, %Y")

    model_config = ConfigDict(from_attributes=True)

class NamespaceLOV(NamespaceBase):
    id: int
    slug: str
    
    # This allows Pydantic to read data from SQLAlchemy models (ORM)
    model_config = ConfigDict(from_attributes=True)