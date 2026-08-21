from datetime import datetime, timezone

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api.users import router
from app.core.dependencies import get_current_user
from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
)
from app.core.exceptions import AppException
from app.core.permissions import (
    require_admin,
    require_responder_or_admin,
)
from app.models.enums import UserRole

# Register all SQLAlchemy models before User instances are created.
from app.models.user import User
from app.models.incident import Incident
from app.models.incident_history import IncidentHistory
from app.models.notification import Notification


def create_app():
    app = FastAPI()

    app.add_exception_handler(
        AppException,
        app_exception_handler,
    )

    app.add_exception_handler(
        Exception,
        generic_exception_handler,
    )

    app.include_router(
        router,
        prefix="/api/v1",
    )

    return app


def make_user(
    user_id: int,
    role: UserRole,
    *,
    is_active: bool = True,
):
    return User(
        id=user_id,
        full_name=f"{role.value.title()} User",
        email=f"{role.value}{user_id}@example.com",
        password_hash="test-hash",
        role=role,
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def app():
    return create_app()


def test_citizen_can_access_own_profile(app):
    user = make_user(1, UserRole.CITIZEN)

    app.dependency_overrides[get_current_user] = lambda: user

    client = TestClient(app)

    response = client.get("/api/v1/users/me")

    assert response.status_code == 200
    assert response.json()["role"] == "citizen"


def test_responder_can_access_own_profile(app):
    user = make_user(2, UserRole.RESPONDER)

    app.dependency_overrides[get_current_user] = lambda: user

    client = TestClient(app)

    response = client.get("/api/v1/users/me")

    assert response.status_code == 200
    assert response.json()["role"] == "responder"


def test_admin_can_access_own_profile(app):
    user = make_user(3, UserRole.ADMIN)

    app.dependency_overrides[get_current_user] = lambda: user

    client = TestClient(app)

    response = client.get("/api/v1/users/me")

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_citizen_cannot_list_users(app):
    user = make_user(1, UserRole.CITIZEN)

    app.dependency_overrides[get_current_user] = lambda: user

    client = TestClient(app)

    response = client.get("/api/v1/users/")

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_responder_cannot_list_users(app):
    user = make_user(2, UserRole.RESPONDER)

    app.dependency_overrides[get_current_user] = lambda: user

    client = TestClient(app)

    response = client.get("/api/v1/users/")

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_can_list_users(app, monkeypatch):
    user = make_user(3, UserRole.ADMIN)

    app.dependency_overrides[get_current_user] = lambda: user

    # The endpoint's database repository isn't relevant
    # to this authorization test. Override it with a
    # harmless empty response.
    from app.api import users as users_api

    class FakeRepository:
        def __init__(self, db):
            self.db = db

        def get_all(self):
            return []

    monkeypatch.setattr(
        users_api,
        "UserRepository",
        FakeRepository,
    )

    app.dependency_overrides[users_api.get_db] = lambda: None

    client = TestClient(app)

    response = client.get("/api/v1/users/")

    assert response.status_code == 200
    assert response.json() == []


def test_require_responder_or_admin_rejects_citizen():
    user = make_user(1, UserRole.CITIZEN)

    with pytest.raises(HTTPException) as exc:
        require_responder_or_admin(current_user=user)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Responder or Admin access required"


def test_require_admin_rejects_responder():
    user = make_user(2, UserRole.RESPONDER)

    with pytest.raises(HTTPException) as exc:
        require_admin(current_user=user)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Admin access required"


def test_require_admin_accepts_admin():
    user = make_user(3, UserRole.ADMIN)

    result = require_admin(current_user=user)

    assert result is user