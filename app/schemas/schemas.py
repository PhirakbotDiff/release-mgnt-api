from pydantic import BaseModel, Field, constr

class DeployRequest(BaseModel):
    service: constr(strip_whitespace=True, min_length=2)
    environment: constr(strip_whitespace=True, min_length=2)
    image_tag: constr(strip_whitespace=True, min_length=1)

class DeployResponse(BaseModel):
    status: str
    message: str
    commit_id: str | None = None

class LoginRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=3)
    password: constr(strip_whitespace=True, min_length=6)