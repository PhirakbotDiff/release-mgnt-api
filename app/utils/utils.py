from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"])

def hash_password(pwd: str):
    return pwd_ctx.hash(pwd)

def verify_password(pwd, hashed):
    return pwd_ctx.verify(pwd, hashed)