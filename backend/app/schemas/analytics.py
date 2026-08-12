from datetime import datetime

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_incidents: int
    status_distribution: dict[str, int]
    severity_distribution: dict[str, int]
    category_distribution: dict[str, int]
    priority_distribution: dict[str, int]
    ai_status_distribution: dict[str, int]
    average_severity_confidence: float | None = None
    average_category_confidence: float | None = None


class TrendPoint(BaseModel):
    date: str
    count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class TrendResponse(BaseModel):
    trends: list[TrendPoint]


class HeatmapPoint(BaseModel):
    id: int
    latitude: float
    longitude: float
    severity: str
    category: str
    priority: str
    status: str
    created_at: datetime


class HeatmapResponse(BaseModel):
    incidents: list[HeatmapPoint]