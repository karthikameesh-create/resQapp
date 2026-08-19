from datetime import datetime, timezone

from app.models.user import User
from app.models.incident import Incident
from app.models.incident_history import IncidentHistory
from app.models.notification import Notification
from app.schemas.user import UserResponse

def test_user_response_does_not_expose_password_hash():
    user = User(
        id=1,
        full_name="Test User",
        email="test@example.com",
        password_hash="super-secret-hash",
        role="citizen",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    response = UserResponse.model_validate(user)

    data = response.model_dump()

    assert "password_hash" not in data
    assert "password" not in data
    assert data["email"] == "test@example.com"
    assert data["role"] == "citizen"