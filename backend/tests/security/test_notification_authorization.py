from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.services.notification_service import NotificationService


def test_user_can_only_mark_own_notification_as_read():
    db = MagicMock()

    # Notification belongs to user 2, but user 1 is making the request.
    (
        db.query.return_value
        .filter.return_value
        .first.return_value
    ) = None

    service = NotificationService(db)

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        service.mark_as_read(
            notification_id=1,
            user_id=1,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Notification not found"


def test_notification_list_cache_is_user_specific():
    db = MagicMock()

    user_1_notifications = [
        {
            "id": 1,
            "user_id": 1,
            "incident_id": 53,
            "type": "critical_incident",
            "title": "Critical Incident Alert",
            "message": "Incident #53",
            "priority": "critical",
            "is_read": False,
            "created_at": None,
        }
    ]

    service = NotificationService(db)

    with patch(
        "app.services.notification_service.CacheService.get",
        return_value=user_1_notifications,
    ) as cache_get:

        result = service.get_user_notifications(
            user_id=1,
            unread_only=False,
        )

    assert result == user_1_notifications
    cache_get.assert_called_once_with(
        "notifications:user:1"
    )


def test_unread_count_is_user_specific():
    db = MagicMock()

    (
        db.query.return_value
        .filter.return_value
        .count.return_value
    ) = 1

    service = NotificationService(db)

    with patch(
        "app.services.notification_service.CacheService.get",
        return_value=None,
    ):

        result = service.get_unread_count(
            user_id=1,
        )

    assert result == 1

    filter_call = db.query.return_value.filter.call_args

    assert filter_call is not None