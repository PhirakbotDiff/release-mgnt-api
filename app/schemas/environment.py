from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional
from datetime import datetime


class EnvironmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class EnvironmentCreate(EnvironmentBase):
    pass

class EnvironmentUpdate(EnvironmentBase):
    name: Optional[str] = None
    description: Optional[str] = None

class Environment(EnvironmentBase):
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