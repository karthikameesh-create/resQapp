from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.enums import UserRole
from app.models.incident import Incident
from app.models.incident_history import IncidentHistory
from app.models.notification import Notification
from app.models.user import User
from app.services.notification_service import NotificationService


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


def setup_database():
    Base.metadata.create_all(bind=engine)


def teardown_database():
    Base.metadata.drop_all(bind=engine)


def create_users(db):
    reporter = User(
        id=1,
        full_name="Reporter",
        email="reporter@example.com",
        password_hash="test-hash",
        role=UserRole.CITIZEN,
        is_active=True,
    )

    admin = User(
        id=2,
        full_name="Admin",
        email="admin@example.com",
        password_hash="test-hash",
        role=UserRole.ADMIN,
        is_active=True,
    )

    db.add_all([reporter, admin])
    db.commit()

    return reporter, admin


def create_incident(
    db,
    reporter_id=1,
    priority="high",
):
    incident = Incident(
        id=1,
        title="Emergency",
        description="Serious emergency requiring response.",
        incident_type="Traffic Accident",
        latitude=12.9141,
        longitude=74.8560,
        reporter_id=reporter_id,
        severity="medium",
        priority=priority,
        ai_status="completed",
        predicted_category="Traffic Accident",
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


def test_high_priority_incident_notifies_reporter_and_admin():
    setup_database()
    db = TestingSessionLocal()

    try:
        create_users(db)
        incident = create_incident(db, priority="high")

        service = NotificationService(db)

        created = service.notify_high_priority_incident(
            incident
        )

        assert created == 2

        notifications = (
            db.query(Notification)
            .order_by(Notification.user_id)
            .all()
        )

        assert len(notifications) == 2

        assert notifications[0].user_id == 1
        assert notifications[1].user_id == 2

        assert all(
            notification.priority == "high"
            for notification in notifications
        )

        assert all(
            notification.incident_id == incident.id
            for notification in notifications
        )

        assert all(
            notification.type
            == "high_priority_incident"
            for notification in notifications
        )

    finally:
        db.close()
        teardown_database()


def test_critical_incident_creates_critical_notifications():
    setup_database()
    db = TestingSessionLocal()

    try:
        create_users(db)
        incident = create_incident(
            db,
            priority="critical",
        )

        service = NotificationService(db)

        created = service.notify_high_priority_incident(
            incident
        )

        assert created == 2

        notifications = (
            db.query(Notification)
            .all()
        )

        assert all(
            notification.priority == "critical"
            for notification in notifications
        )

        assert all(
            notification.type
            == "critical_incident"
            for notification in notifications
        )

        assert all(
            notification.title
            == "Critical Incident Alert"
            for notification in notifications
        )

    finally:
        db.close()
        teardown_database()


def test_low_priority_incident_creates_no_notifications():
    setup_database()
    db = TestingSessionLocal()

    try:
        create_users(db)
        incident = create_incident(
            db,
            priority="low",
        )

        service = NotificationService(db)

        created = service.notify_high_priority_incident(
            incident
        )

        assert created == 0

        assert (
            db.query(Notification).count()
            == 0
        )

    finally:
        db.close()
        teardown_database()


def test_duplicate_notification_is_not_created():
    setup_database()
    db = TestingSessionLocal()

    try:
        create_users(db)
        incident = create_incident(
            db,
            priority="high",
        )

        service = NotificationService(db)

        first = (
            service.notify_high_priority_incident(
                incident
            )
        )

        second = (
            service.notify_high_priority_incident(
                incident
            )
        )

        assert first == 2
        assert second == 0

        assert (
            db.query(Notification).count()
            == 2
        )

    finally:
        db.close()
        teardown_database()