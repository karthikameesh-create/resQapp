from pydantic import BaseModel
from datetime import datetime

class DashboardResponse(BaseModel):
    total_incidents: int
    status_distribution: dict[str, int]
    severity_distribution: dict[str, int]
    category_distribution: dict[str, int]

class TrendPoint(BaseModel):
    date: str
    count: int


class TrendResponse(BaseModel):
    trends: list[TrendPoint]    

class HeatmapPoint(BaseModel):
    id: int
    latitude: float
    longitude: float
    severity: str
    category: str
    status: str
    created_at: datetime


class HeatmapResponse(BaseModel):
    incidents: list[HeatmapPoint]    