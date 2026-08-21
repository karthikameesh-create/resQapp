from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.enums import UserRole
from app.models.incident import Incident
from app.models.incident_history import IncidentHistory
from app.models.notification import Notification
from app.models.user import User
from app.tasks import incident_tasks


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
def use_test_database(monkeypatch):
    monkeypatch.setattr(
        incident_tasks,
        "SessionLocal",
        TestingSessionLocal,
    )


def create_database():
    Base.metadata.create_all(bind=engine)


def cleanup_database():
    Base.metadata.drop_all(bind=engine)


def create_test_incident(
    db,
    *,
    incident_id=1,
    ai_status="pending",
):
    user = User(
        id=1,
        full_name="AI Test User",
        email="ai-test@example.com",
        password_hash="test-hash",
        role=UserRole.CITIZEN,
        is_active=True,
    )

    incident = Incident(
        id=incident_id,
        title="AI Workflow Test",
        description="A serious road accident requires emergency response.",
        incident_type="Traffic Accident",
        latitude=12.9141,
        longitude=74.8560,
        reporter_id=1,
        ai_status=ai_status,
        severity="medium",
        priority="low",
    )

    db.add(user)
    db.add(incident)
    db.commit()

    return incident


def fake_analysis():
    return SimpleNamespace(
        predicted_severity="Critical",
        severity_confidence=0.98,
        predicted_category="Traffic Accident",
        category_confidence=0.96,
        summary="Critical traffic accident requiring immediate response.",
        recommended_response=[
            "Dispatch emergency medical services.",
            "Secure the accident scene.",
        ],
    )


def test_ai_analysis_success(
    monkeypatch,
    use_test_database,
):
    create_database()
    db = TestingSessionLocal()

    try:
        create_test_incident(db)

        monkeypatch.setattr(
            incident_tasks.AIService,
            "analyze",
            lambda description: fake_analysis(),
        )

        monkeypatch.setattr(
            incident_tasks.CacheService,
            "delete",
            lambda key: None,
        )

        monkeypatch.setattr(
            incident_tasks.NotificationService,
            "notify_high_priority_incident",
            lambda self, incident: 0,
        )

        incident_tasks.analyze_incident_background(1)

        incident = (
            db.query(Incident)
            .filter(Incident.id == 1)
            .first()
        )

        assert incident is not None
        assert incident.ai_status == "completed"
        assert incident.predicted_severity == "Critical"
        assert incident.predicted_category == "Traffic Accident"
        assert incident.severity_confidence == 0.98
        assert incident.category_confidence == 0.96
        assert incident.ai_summary is not None
        assert incident.recommended_response is not None
        assert incident.priority in {
            "low",
            "medium",
            "high",
            "critical",
        }

    finally:
        db.close()
        cleanup_database()


def test_ai_analysis_failure_retries_three_times(
    monkeypatch,
    use_test_database,
):
    create_database()
    db = TestingSessionLocal()

    try:
        create_test_incident(db)

        attempts = []

        def failing_analysis(description):
            attempts.append(description)
            raise RuntimeError("TEST AI FAILURE")

        monkeypatch.setattr(
            incident_tasks.AIService,
            "analyze",
            failing_analysis,
        )

        monkeypatch.setattr(
            incident_tasks.time,
            "sleep",
            lambda seconds: None,
        )

        incident_tasks.analyze_incident_background(1)

        incident = (
            db.query(Incident)
            .filter(Incident.id == 1)
            .first()
        )

        assert len(attempts) == 3
        assert incident is not None
        assert incident.ai_status == "failed"

    finally:
        db.close()
        cleanup_database()


def test_processing_incident_is_not_processed_again(
    monkeypatch,
    use_test_database,
):
    create_database()
    db = TestingSessionLocal()

    try:
        create_test_incident(
            db,
            ai_status="processing",
        )

        calls = []

        monkeypatch.setattr(
            incident_tasks.AIService,
            "analyze",
            lambda description: calls.append(description),
        )

        incident_tasks.analyze_incident_background(1)

        assert calls == []

        incident = (
            db.query(Incident)
            .filter(Incident.id == 1)
            .first()
        )

        assert incident.ai_status == "processing"

    finally:
        db.close()
        cleanup_database()