from pydantic import BaseModel, ConfigDict
from typing import Optional

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

    model_config = ConfigDict(from_attributes=True)

class NamespaceLOV(NamespaceBase):
    id: int
    slug: str
    
    # This allows Pydantic to read data from SQLAlchemy models (ORM)
    model_config = ConfigDict(from_attributes=True)