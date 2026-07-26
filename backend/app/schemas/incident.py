from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentCreate(BaseModel):
    title: str
    description: str
    incident_type: str
    latitude: float
    longitude: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Road Accident",
                "description": "A bus collided with a truck near Mangalore. Five passengers are injured and one is unconscious.",
                "incident_type": "Traffic Accident",
                "latitude": 12.9141,
                "longitude": 74.8560,
            }
        }
    )


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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 7,
                "title": "Road Accident",
                "description": "A bus collided with a truck near Mangalore. Five passengers are injured and one is unconscious.",
                "incident_type": "Traffic Accident",
                "status": "reported",
                "severity": "medium",
                "predicted_severity": "High",
                "predicted_category": "Traffic Accident",
                "ai_summary": "A collision between a bus and a truck near Mangalore has resulted in five injuries and one unconscious individual.",
                "recommended_response": [
                    "Dispatch emergency medical services immediately.",
                    "Notify local police.",
                    "Alert nearby hospitals.",
                ],
                "latitude": 12.9141,
                "longitude": 74.8560,
                "reporter_id": 1,
                "created_at": "2026-07-25T12:51:25.609453Z",
            }
        },
    )


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    incident_type: str | None = None
    status: str | None = None
    severity: str | None = None
    latitude: float | None = None
    longitude: float | None = None