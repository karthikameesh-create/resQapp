from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.notification_service import NotificationService


def test_get_user_notifications_cache_miss():
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
        created_at=None,
    )

    (
        db.query.return_value
        .filter.return_value
        .order_by.return_value
        .limit.return_value
        .all.return_value
    ) = [notification]

    service = NotificationService(db)

    with patch(
        "app.services.notification_service.CacheService.get",
        return_value=None,
    ) as cache_get, patch(
        "app.services.notification_service.CacheService.set"
    ) as cache_set:

        result = service.get_user_notifications(
            user_id=1,
            unread_only=False,
            limit=50,
        )

    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["priority"] == "critical"

    cache_get.assert_called_once_with(
        "notifications:user:1"
    )

    cache_set.assert_called_once()
    assert cache_set.call_args.args[0] == "notifications:user:1"
    assert cache_set.call_args.kwargs["expire"] == 60


def test_get_user_notifications_cache_hit():
    db = MagicMock()

    cached_notifications = [
        {
            "id": 1,
            "user_id": 1,
            "incident_id": 53,
            "type": "critical_incident",
            "title": "Critical Incident Alert",
            "message": "Critical incident detected.",
            "priority": "critical",
            "is_read": False,
            "created_at": None,
        }
    ]

    service = NotificationService(db)

    with patch(
        "app.services.notification_service.CacheService.get",
        return_value=cached_notifications,
    ) as cache_get, patch(
        "app.services.notification_service.CacheService.set"
    ) as cache_set:

        result = service.get_user_notifications(
            user_id=1,
            unread_only=False,
            limit=50,
        )

    assert result == cached_notifications

    cache_get.assert_called_once_with(
        "notifications:user:1"
    )

    cache_set.assert_not_called()
    db.query.assert_not_called()


def test_unread_count_cache_miss():
    db = MagicMock()

    (
        db.query.return_value
        .filter.return_value
        .count.return_value
    ) = 2

    service = NotificationService(db)

    with patch(
        "app.services.notification_service.CacheService.get",
        return_value=None,
    ) as cache_get, patch(
        "app.services.notification_service.CacheService.set"
    ) as cache_set:

        result = service.get_unread_count(user_id=1)

    assert result == 2

    cache_get.assert_called_once_with(
        "notifications:unread-count:1"
    )

    cache_set.assert_called_once_with(
        "notifications:unread-count:1",
        2,
        expire=60,
    )


def test_unread_count_cache_hit():
    db = MagicMock()

    service = NotificationService(db)

    with patch(
        "app.services.notification_service.CacheService.get",
        return_value=3,
    ) as cache_get:

        result = service.get_unread_count(user_id=1)

    assert result == 3

    cache_get.assert_called_once_with(
        "notifications:unread-count:1"
    )

    db.query.assert_not_called()


def test_create_notification_invalidates_user_cache():
    db = MagicMock()

    notification = SimpleNamespace(
        id=5,
        user_id=1,
        incident_id=53,
        type="test_notification",
        title="Test",
        message="Testing cache invalidation.",
        priority="medium",
        is_read=False,
        created_at=None,
    )

    db.refresh.side_effect = lambda obj: None

    with patch(
        "app.services.notification_service.Notification",
        return_value=notification,
    ), patch(
        "app.services.notification_service.CacheService.delete"
    ) as cache_delete:

        service = NotificationService(db)

        result = service.create_notification(
            user_id=1,
            notification_type="test_notification",
            title="Test",
            message="Testing cache invalidation.",
            priority="medium",
            incident_id=53,
        )

    assert result.id == 5

    expected_keys = {
        "notifications:user:1",
        "notifications:unread:1",
        "notifications:unread-count:1",
    }

    actual_keys = {
        call.args[0]
        for call in cache_delete.call_args_list
    }

    assert actual_keys == expected_keys


def test_mark_as_read_invalidates_user_cache():
    db = MagicMock()

    notification = SimpleNamespace(
        id=1,
        user_id=1,
        is_read=False,
    )

    (
        db.query.return_value
        .filter.return_value
        .first.return_value
    ) = notification

    with patch(
        "app.services.notification_service.CacheService.delete"
    ) as cache_delete:

        service = NotificationService(db)

        result = service.mark_as_read(
            notification_id=1,
            user_id=1,
        )

    assert result.is_read is True

    expected_keys = {
        "notifications:user:1",
        "notifications:unread:1",
        "notifications:unread-count:1",
    }

    actual_keys = {
        call.args[0]
        for call in cache_delete.call_args_list
    }

    assert actual_keys == expected_keys


def test_mark_all_as_read_invalidates_user_cache():
    db = MagicMock()

    notification_1 = SimpleNamespace(
        id=1,
        user_id=1,
        is_read=False,
    )

    notification_2 = SimpleNamespace(
        id=2,
        user_id=1,
        is_read=False,
    )

    (
        db.query.return_value
        .filter.return_value
        .all.return_value
    ) = [notification_1, notification_2]

    with patch(
        "app.services.notification_service.CacheService.delete"
    ) as cache_delete:

        service = NotificationService(db)

        result = service.mark_all_as_read(
            user_id=1,
        )

    assert result == 2
    assert notification_1.is_read is True
    assert notification_2.is_read is True

    expected_keys = {
        "notifications:user:1",
        "notifications:unread:1",
        "notifications:unread-count:1",
    }

    actual_keys = {
        call.args[0]
        for call in cache_delete.call_args_list
    }

    assert actual_keys == expected_keys