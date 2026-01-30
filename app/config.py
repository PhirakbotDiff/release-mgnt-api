from pydantic_settings import BaseSettings # type: ignore

class Settings(BaseSettings):
    MANIFEST_REPO_URL: str
    MANIFEST_REPO_BRANCH: str = "main"
    # MANIFEST_LOCAL_PATH: str = "../repos/manifest_repo"
    MANIFEST_LOCAL_PATH: str = "https://gitscm-uat.vattanacbrewery.com/devops/manifest_repo"
    GIT_TOKEN: str
    GIT_USERNAME: str
    GIT_AUTHOR_NAME: str = "phirakbot"
    GIT_AUTHOR_EMAIL: str = "phirakbot.chhoeun@vattanacbrewery.com"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    IMAGE_REGISTRY_URL: str = "10.20.10.117:5000"
    IMAGE_REGISTRY_USERNAME: str
    IMAGE_REGISTRY_PASSWORD: str
    SEVERITIES: list[str] = ["CRITICAL", "HIGH", "MEDIUM"]
    
    DB_HOST: str = "localhost"

    class Config:
        env_file = ".env"

settings = Settings()
