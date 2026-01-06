from pydantic import BaseModel, ConfigDict
from typing import Optional

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

    model_config = ConfigDict(from_attributes=True)