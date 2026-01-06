from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base
from datetime import datetime

class Deployment(Base):
    __tablename__ = "rl_deployments"

    id = Column(Integer, primary_key=True, index=True)

    service = Column(String, nullable=False)
    environment = Column(String, nullable=False)
    image_tag = Column(String, nullable=False)
    git_tag = Column(String, nullable=False)
    
    status = Column(String, default="PENDING")
    commit_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    description = Column(Text, nullable=True)
    # namespace = Column(Text, nullable=True)
    # cluster = Column(Text, nullable=True)

    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)