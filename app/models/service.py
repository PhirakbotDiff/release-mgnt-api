from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base  # Assuming Base is defined in your database module
from datetime import datetime

class Service(Base):
    __tablename__ = "rl_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    manifest_path = Column(String)
    gitlab_url = Column(String)

    namespace = Column(String, nullable=True)

    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)