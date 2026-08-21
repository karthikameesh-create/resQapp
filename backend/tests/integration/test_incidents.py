import pytest
from fastapi import FastAPI
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
from app.models.user import User

# Import all mapped models so SQLAlchemy relationships are registered.
from app.models.incident import Incident
from app.models.incident_history import IncidentHistory
from app.models.notification import Notification


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def test_user():
    return User(
        id=1,
        full_name="Integration User",
        email="integration@example.com",
        password_hash="test-hash",
        role=UserRole.CITIZEN,
        is_active=True,
    )


@pytest.fixture
def client(test_user, monkeypatch):
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

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

    def override_get_db():
        yield db

    def override_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_current_user
    )

    # Prevent the real Gemini background task from running.
    monkeypatch.setattr(
        "app.api.incidents.analyze_incident_background",
        lambda incident_id: None,
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def incident_payload():
    return {
        "title": "Road Accident",
        "description": "A collision occurred near Mangalore.",
        "incident_type": "Traffic Accident",
        "latitude": 12.9141,
        "longitude": 74.8560,
    }


def test_create_incident_returns_201(client):
    response = client.post(
        "/api/v1/incidents",
        json=incident_payload(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Road Accident"
    assert data["incident_type"] == "Traffic Accident"
    assert data["reporter_id"] == 1
    assert data["latitude"] == pytest.approx(12.9141)
    assert data["longitude"] == pytest.approx(74.8560)


def test_create_incident_rejects_invalid_coordinates(client):
    payload = incident_payload()
    payload["latitude"] = 120

    response = client.post(
        "/api/v1/incidents",
        json=payload,
    )

    assert response.status_code == 422


def test_incident_list_returns_created_incident(client):
    create_response = client.post(
        "/api/v1/incidents",
        json=incident_payload(),
    )

    assert create_response.status_code == 201

    response = client.get("/api/v1/incidents")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Road Accident"


def test_get_incident_returns_created_incident(client):
    create_response = client.post(
        "/api/v1/incidents",
        json=incident_payload(),
    )

    incident_id = create_response.json()["id"]

    response = client.get(f"/api/v1/incidents/{incident_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == incident_id
    assert data["title"] == "Road Accident"


def test_get_missing_incident_returns_404(client):
    response = client.get("/api/v1/incidents/999999")

    assert response.status_code == 404


def test_create_incident_records_history(client):
    create_response = client.post(
        "/api/v1/incidents",
        json=incident_payload(),
    )

    incident_id = create_response.json()["id"]

    response = client.get(f"/api/v1/incidents/{incident_id}/history")

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 1
    assert history[0]["action"] == "created"
    assert history[0]["changed_by"] == 1
    assert history[0]["incident_id"] == incident_id