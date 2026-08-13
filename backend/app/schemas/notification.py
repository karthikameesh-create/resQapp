from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    incident_id: int | None
    type: str
    title: str
    message: str
    priority: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class NotificationCountResponse(BaseModel):
    unread_count: int