from sqlalchemy import (
    Column, Integer, String, Enum, ForeignKey, TIMESTAMP, DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base
import enum


class ScanStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    FAILED = "FAILED"
    PENDING = "PENDING"
    QUEUE = "QUEUE"
    RUNNING = "RUNNING"
    INIT = "INIT"

class SeverityLevel(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Image(Base):
    __tablename__ = "rl_images"

    id = Column(Integer, primary_key=True)
    service_id = Column(String)
    latest_version_scan = Column(String)
    environment_id = Column(String)
    status = Column(
        Enum(ScanStatus, name="scan_status"),
        nullable=False
    )
    critical = Column(Integer, default=0)
    high = Column(Integer, default=0)
    medium = Column(Integer, default=0)
    low = Column(Integer, default=0)
    namespace = Column(String, nullable=True)
    
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scans = relationship("ImageScan", back_populates="image")


class ImageScan(Base):
    __tablename__ = "rl_image_scans"

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("rl_images.id"))
    image_current = Column(String)
    image_previous = Column(String)
    environment_id = Column(String)
    status = Column(
        Enum(ScanStatus, name="scan_status"),
        nullable=False
    )

    progress = Column(Integer, default=0)
    message = Column(String, default="")
    critical = Column(Integer, default=0)
    high = Column(Integer, default=0)
    medium = Column(Integer, default=0)
    low = Column(Integer, default=0)
    
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    image = relationship("Image", back_populates="scans")
    details = relationship("ImageScanDetail", back_populates="scan")


class ImageScanDetail(Base):
    __tablename__ = "rl_image_scan_details"

    id = Column(Integer, primary_key=True)
    image_scan_id = Column(Integer, ForeignKey("rl_image_scans.id"))
    cve_name = Column(String)
    severity = Column(
        Enum(SeverityLevel, name="severity_level"),
        nullable=False
    )
    package_name = Column(String)
    status = Column(String)
    package_version = Column(String)
    fixed_version = Column(String)
    
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scan = relationship("ImageScan", back_populates="details")
