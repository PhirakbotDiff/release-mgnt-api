from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserProfile(BaseModel):
    id: int
    username: str
    role: str
    firstname: str | None = None
    lastname: str | None = None
    created_at: datetime
    email: str | None = None
    bio: str | None = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None