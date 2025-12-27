from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MANIFEST_REPO_URL: str
    MANIFEST_REPO_BRANCH: str = "main"
    MANIFEST_LOCAL_PATH: str = "./repos/manifest-repo"
    GIT_AUTHOR_NAME: str = "release-bot"
    GIT_AUTHOR_EMAIL: str = "release-bot@company.com"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"

settings = Settings()
