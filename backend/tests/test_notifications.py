from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.models.notification import Notification
from app.services.notification_service import NotificationService


def test_create_notification():
    db = MagicMock()

    notification = SimpleNamespace(
        id=1,
        user_id=1,
        incident_id=53,
        type="critical_incident",
        title="Critical Incident Alert",
        message="Critical incident detected.",
        priority="critical",
        is_read=False,
    )

    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.side_effect = lambda obj: None

    with patch(
        "app.services.notification_service.Notification",
        return_value=notification,
    ):
        service = NotificationService(db)

        result = service.create_notification(
            user_id=1,
            notification_type="critical_incident",
            title="Critical Incident Alert",
            message="Critical incident detected.",
            priority="critical",
            incident_id=53,
        )

    assert result.user_id == 1
    assert result.incident_id == 53
    assert result.priority == "critical"
    assert result.is_read is False

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


def test_notification_exists_true():
    db = MagicMock()

    query = db.query.return_value
    query.filter.return_value.first.return_value = object()

    service = NotificationService(db)

    result = service.notification_exists(
        user_id=1,
        incident_id=53,
        notification_type="critical_incident",
    )

    assert result is True


def test_notification_exists_false():
    db = MagicMock()

    query = db.query.return_value
    query.filter.return_value.first.return_value = None

    service = NotificationService(db)

    result = service.notification_exists(
        user_id=1,
        incident_id=53,
        notification_type="critical_incident",
    )

    assert result is False


def test_high_priority_incident_creates_notification():
    db = MagicMock()

    reporter = SimpleNamespace(id=1)
    db.query.return_value.filter.return_value.all.return_value = []

    incident = SimpleNamespace(
        id=53,
        reporter_id=1,
        priority="critical",
        predicted_category="Traffic Accident",
    )

    service = NotificationService(db)

    with patch.object(
        service,
        "notification_exists",
        return_value=False,
    ), patch.object(
        service,
        "create_notification",
    ) as create_notification:

        result = service.notify_high_priority_incident(
            incident
        )

    assert result == 1

    create_notification.assert_called_once_with(
        user_id=1,
        incident_id=53,
        notification_type="critical_incident",
        title="Critical Incident Alert",
        message=(
            "Incident #53 has been classified as "
            "critical priority. Category: Traffic Accident."
        ),
        priority="critical",
    )


def test_low_priority_incident_creates_no_notification():
    db = MagicMock()

    incident = SimpleNamespace(
        id=46,
        reporter_id=1,
        priority="low",
        predicted_category="System Testing",
    )

    service = NotificationService(db)

    with patch.object(
        service,
        "create_notification",
    ) as create_notification:

        result = service.notify_high_priority_incident(
            incident
        )

    assert result == 0
    create_notification.assert_not_called()