from datetime import datetime, timezone

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.incidents import router
from app.core.dependencies import get_current_user
from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
)
from app.core.exceptions import AppException
from app.db.base import Base
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.incident import Incident
from app.models.incident_history import IncidentHistory
from app.models.notification import Notification
from app.models.user import User


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def create_app(current_user):
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

    db = TestingSessionLocal()

    def override_get_db():
        yield db

    def override_current_user():
        return current_user

    app.dependency_overrides[get_db] = (
        override_get_db
    )
    app.dependency_overrides[get_current_user] = (
        override_current_user
    )

    return app, db


@pytest.fixture
def database():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    reporter = User(
        id=1,
        full_name="Reporter",
        email="reporter@example.com",
        password_hash="test-hash",
        role=UserRole.CITIZEN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    other_user = User(
        id=2,
        full_name="Other User",
        email="other@example.com",
        password_hash="test-hash",
        role=UserRole.CITIZEN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    admin = User(
        id=3,
        full_name="Admin",
        email="admin@example.com",
        password_hash="test-hash",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    incident = Incident(
        id=1,
        title="Road Accident",
        description="A serious accident occurred.",
        incident_type="Traffic Accident",
        status="reported",
        severity="medium",
        priority="low",
        ai_status="pending",
        latitude=12.9141,
        longitude=74.8560,
        reporter_id=1,
        created_at=datetime.now(timezone.utc),
    )

    db.add_all(
        [
            reporter,
            other_user,
            admin,
            incident,
        ]
    )
    db.commit()

    yield db, reporter, other_user, admin

    db.close()
    Base.metadata.drop_all(bind=engine)


def test_update_creates_field_level_history(
    database,
):
    db, reporter, _, _ = database

    app, session = create_app(reporter)

    # Use the same session as the test database.
    session.close()

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as client:
        response = client.put(
            "/api/v1/incidents/1",
            json={
                "title": "Updated Road Accident",
            },
        )

    assert response.status_code == 200

    history = (
        db.query(IncidentHistory)
        .filter(
            IncidentHistory.incident_id == 1,
        )
        .all()
    )

    assert len(history) == 1

    event = history[0]

    assert event.action == "updated"
    assert event.field == "title"
    assert event.old_value == "Road Accident"
    assert event.new_value == "Updated Road Accident"
    assert event.changed_by == reporter.id


def test_multiple_updates_create_multiple_history_events(
    database,
):
    db, reporter, _, _ = database

    app, _ = create_app(reporter)

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as client:
        first = client.put(
            "/api/v1/incidents/1",
            json={
                "title": "Updated Title",
            },
        )

        second = client.put(
            "/api/v1/incidents/1",
            json={
                "description": "Updated description.",
            },
        )

    assert first.status_code == 200
    assert second.status_code == 200

    history = (
        db.query(IncidentHistory)
        .filter(
            IncidentHistory.incident_id == 1,
        )
        .order_by(
            IncidentHistory.created_at.asc()
        )
        .all()
    )

    assert len(history) == 2

    assert history[0].action == "updated"
    assert history[0].field == "title"

    assert history[1].action == "updated"
    assert history[1].field == "description"


def test_unauthorized_user_cannot_create_update_history(
    database,
):
    db, _, other_user, _ = database

    app, _ = create_app(other_user)

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as client:
        response = client.put(
            "/api/v1/incidents/1",
            json={
                "title": "Unauthorized Update",
            },
        )

    assert response.status_code == 403

    history = (
        db.query(IncidentHistory)
        .filter(
            IncidentHistory.incident_id == 1,
        )
        .all()
    )

    assert history == []


def test_admin_can_update_and_history_records_admin(
    database,
):
    db, _, _, admin = database

    app, _ = create_app(admin)

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as client:
        response = client.put(
            "/api/v1/incidents/1",
            json={
                "status": "resolved",
            },
        )

    assert response.status_code == 200

    history = (
        db.query(IncidentHistory)
        .filter(
            IncidentHistory.incident_id == 1,
        )
        .all()
    )

    assert len(history) == 1
    assert history[0].field == "status"
    assert history[0].old_value == "reported"
    assert history[0].new_value == "resolved"
    assert history[0].changed_by == admin.id