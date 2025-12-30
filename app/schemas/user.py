from pydantic import BaseModel
from datetime import datetime

class UserProfile(BaseModel):
    id: int
    username: str
    role: str
    firstname: str | None = None
    lastname: str | None = None
    created_at: datetime
    email: str | None = None

    class Config:
        from_attributes = True
