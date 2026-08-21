from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentHistoryResponse(BaseModel):
    id: int
    incident_id: int | None
    action: str
    field: str | None
    old_value: str | None
    new_value: str | None
    changed_by: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )