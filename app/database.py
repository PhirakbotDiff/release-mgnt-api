from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker, declarative_base # type: ignore
from app.config import settings
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{settings.DB_USER}:{settings.DB_PWD}@{settings.DB_HOST}:5432/release_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
