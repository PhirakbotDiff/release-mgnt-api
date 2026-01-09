from pydantic import BaseModel, ConfigDict
from typing import Optional

# Shared properties
class ServiceBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    manifest_path: Optional[str] = None
    gitlab_url: Optional[str] = None

# Properties to receive on service creation
class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    pass

# Properties to return to client (includes ID)
class Service(ServiceBase):
    id: int
    slug: str
    
    # This allows Pydantic to read data from SQLAlchemy models (ORM)
    model_config = ConfigDict(from_attributes=True)