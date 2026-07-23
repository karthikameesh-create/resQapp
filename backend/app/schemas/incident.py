from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentCreate(BaseModel):
    title: str
    description: str
    incident_type: str
    latitude: float
    longitude: float


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    incident_type: str
    status: str
    severity: str

    predicted_severity: str | None = None
    predicted_category: str | None = None
    ai_summary: str | None = None
    recommended_response: list[str] | None = None

    latitude: float
    longitude: float
    reporter_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    incident_type: str | None = None
    status: str | None = None
    severity: str | None = None
    latitude: float | None = None
    longitude: float | None = None