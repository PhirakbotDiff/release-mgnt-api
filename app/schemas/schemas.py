from pydantic import BaseModel, Field, constr

class LoginRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=3)
    password: constr(strip_whitespace=True, min_length=6)