from sqlalchemy import Column, Integer, String, Text
from app.database import Base  # Assuming Base is defined in your database module

class Service(Base):
    __tablename__ = "rl_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    manifest_path = Column(String)
    gitlab_url = Column(String)