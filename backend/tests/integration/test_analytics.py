from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.analytics import router
from app.db.base import Base
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.incident import Incident
from app.models.incident_history import IncidentHistory
from app.models.notification import Notification
from app.models.user import User
from app.services import analytics_service


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


@pytest.fixture
def client(monkeypatch):
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    users = [
        User(
            id=1,
            full_name="Citizen",
            email="citizen@example.com",
            password_hash="test-hash",
            role=UserRole.CITIZEN,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        ),
        User(
            id=2,
            full_name="Admin",
            email="admin@example.com",
            password_hash="test-hash",
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        ),
    ]

    incidents = [
        Incident(
            id=1,
            title="Road Accident",
            description="Serious road accident.",
            incident_type="Traffic Accident",
            status="reported",
            severity="High",
            priority="high",
            predicted_severity="High",
            severity_confidence=0.90,
            predicted_category="Traffic Accident",
            category_confidence=0.95,
            ai_summary="High severity traffic accident.",
            recommended_response=["Dispatch EMS"],
            ai_status="completed",
            latitude=12.9141,
            longitude=74.8560,
            reporter_id=1,
            created_at=datetime(
                2026, 8, 1, tzinfo=timezone.utc
            ),
        ),
        Incident(
            id=2,
            title="Factory Fire",
            description="Large industrial fire.",
            incident_type="Structure Fire",
            status="reported",
            severity="Critical",
            priority="critical",
            predicted_severity="Critical",
            severity_confidence=1.0,
            predicted_category="Structure Fire",
            category_confidence=0.98,
            ai_summary="Critical structure fire.",
            recommended_response=["Dispatch fire services"],
            ai_status="completed",
            latitude=12.9200,
            longitude=74.8400,
            reporter_id=2,
            created_at=datetime(
                2026, 8, 2, tzinfo=timezone.utc
            ),
        ),
        Incident(
            id=3,
            title="Flood Alert",
            description="Flooding reported.",
            incident_type="Flood",
            status="processing",
            severity="Low",
            priority="low",
            predicted_severity=None,
            severity_confidence=None,
            predicted_category=None,
            category_confidence=None,
            ai_summary=None,
            recommended_response=None,
            ai_status="pending",
            latitude=12.9300,
            longitude=74.8300,
            reporter_id=1,
            created_at=datetime(
                2026, 8, 3, tzinfo=timezone.utc
            ),
        ),
    ]

    db.add_all(users)
    db.add_all(incidents)
    db.commit()

    app = FastAPI()
    app.include_router(
        router,
        prefix="/api/v1",
    )

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    # Isolate cache so tests never reuse previous values.
    monkeypatch.setattr(
        analytics_service.CacheService,
        "get",
        lambda key: None,
    )

    monkeypatch.setattr(
        analytics_service.CacheService,
        "set",
        lambda key, value, expire=300: None,
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_dashboard_returns_correct_aggregate_data(client):
    response = client.get(
        "/api/v1/analytics/dashboard"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_incidents"] == 3

    assert data["status_distribution"] == {
        "reported": 2,
        "processing": 1,
    }

    assert data["priority_distribution"] == {
        "high": 1,
        "critical": 1,
        "low": 1,
    }

    assert data["ai_status_distribution"] == {
        "completed": 2,
        "pending": 1,
    }

    assert data["severity_distribution"] == {
        "High": 1,
        "Critical": 1,
        "Unknown": 1,
    }


def test_dashboard_returns_average_ai_confidence(client):
    response = client.get(
        "/api/v1/analytics/dashboard"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["average_severity_confidence"] == pytest.approx(
        0.95
    )

    assert data["average_category_confidence"] == pytest.approx(
        0.965
    )


def test_trends_returns_daily_incident_counts(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.analytics_service.AnalyticsRepository.incident_trends",
        lambda self: [
            {
                "date": "2026-08-01",
                "count": 1,
                "critical_count": 0,
                "high_count": 1,
                "medium_count": 0,
                "low_count": 0,
            },
            {
                "date": "2026-08-02",
                "count": 1,
                "critical_count": 1,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
            },
            {
                "date": "2026-08-03",
                "count": 1,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 1,
            },
        ],
    )

    response = client.get(
        "/api/v1/analytics/trends"
    )

    assert response.status_code == 200

    trends = response.json()["trends"]

    assert len(trends) == 3

    assert {
        item["date"]
        for item in trends
    } == {
        "2026-08-01",
        "2026-08-02",
        "2026-08-03",
    }

    assert all(
        item["count"] == 1
        for item in trends
    )


def test_heatmap_returns_incident_locations(client):
    response = client.get(
        "/api/v1/analytics/heatmap"
    )

    assert response.status_code == 200

    incidents = response.json()["incidents"]

    assert len(incidents) == 3

    coordinates = {
        (
            incident["latitude"],
            incident["longitude"],
        )
        for incident in incidents
    }

    assert coordinates == {
        (12.9141, 74.856),
        (12.9200, 74.8400),
        (12.9300, 74.8300),
    }


def test_empty_analytics_database_returns_zero_totals(
    monkeypatch,
):
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        app = FastAPI()
        app.include_router(
            router,
            prefix="/api/v1",
        )

        def override_get_db():
            yield db

        app.dependency_overrides[
            get_db
        ] = override_get_db

        monkeypatch.setattr(
            analytics_service.CacheService,
            "get",
            lambda key: None,
        )

        monkeypatch.setattr(
            analytics_service.CacheService,
            "set",
            lambda key, value, expire=300: None,
        )

        with TestClient(app) as client:
            response = client.get(
                "/api/v1/analytics/dashboard"
            )

        assert response.status_code == 200

        data = response.json()

        assert data["total_incidents"] == 0
        assert data["average_severity_confidence"] is None
        assert data["average_category_confidence"] is None

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)