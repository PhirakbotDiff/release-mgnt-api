from pydantic_settings import BaseSettings # type: ignore

class Settings(BaseSettings):
    MANIFEST_REPO_URL: str
    MANIFEST_REPO_BRANCH: str = "main"
    MANIFEST_LOCAL_PATH: str = "./repos/manifest_repo"
    GIT_TOKEN: str
    GIT_USERNAME: str
    GIT_AUTHOR_NAME: str = "phirakbot"
    GIT_AUTHOR_EMAIL: str = "phirakbot.chhoeun@vattanacbrewery.com"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"

settings = Settings()
