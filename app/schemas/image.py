from pydantic import BaseModel, validator, field_serializer
from typing import Optional, List
from datetime import datetime
from app.models.image import ScanStatus, SeverityLevel


class ImageCreate(BaseModel):
    service_id: str
    latest_version_scan: str
    environment_id: str
    status: ScanStatus
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    namespace: str


class ImageResponse(BaseModel):
    id: int
    service_id: str
    latest_version_scan: str
    environment_id: str
    status: ScanStatus
    critical: int
    high: int
    medium: int
    low: int
    short_name: Optional[str] = None
    namespace: str
    created_at: str | datetime | None
    created_by: str | int | None
    created_position: str | None = None

    class Config:
        orm_mode = True

    @validator("short_name", pre=True, always=True)
    def set_short_name(cls, v, values):
        service_id = values.get("service_id")
        if service_id:
            parts = service_id.split("-")
            letters = [p[0].upper() for p in parts if p]
            return "".join(letters)[:3]
        return v
    
    @field_serializer("created_at")
    def serialize_created_at(self, v: datetime) -> str:
        return v.strftime("%d %b, %Y")

    @field_serializer("created_by")
    def serialize_created_by(self, v: str) -> str:
        return v if v else "N/A"

class ImageScanCreate(BaseModel):
    image_id: int
    image_current: str
    image_previous: Optional[str]
    environment_id: str
    status: ScanStatus
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class ImageScanRequest(BaseModel):
    image_id: int
    image_current: str
    image_previous: Optional[str]
    environment_id: str


class ImageScanDetailCreate(BaseModel):
    cve_name: str
    severity: SeverityLevel
    package_name: str
    status: str
    package_version: str
    fixed_version: Optional[str]
