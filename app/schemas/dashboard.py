from pydantic import BaseModel # type: ignore
from typing import List, Literal

class Metric(BaseModel):
    total: int
    percentage: float
    type: Literal["up", "down"]


class DashboardStats(BaseModel):
    services: Metric
    deployments: Metric
    monthlyData: List[int]
