import logging

from fastapi import HTTPException

from app.models.notification import Notification
from app.models.user import User
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class NotificationService:

    def __init__(self, db):
        self.db = db

    @staticmethod
    def _all_cache_key(user_id: int) -> str:
        return f"notifications:user:{user_id}"

    @staticmethod
    def _unread_cache_key(user_id: int) -> str:
        return f"notifications:unread:{user_id}"

    @staticmethod
    def _count_cache_key(user_id: int) -> str:
        return f"notifications:unread-count:{user_id}"

    @classmethod
    def _invalidate_user_cache(cls, user_id: int) -> None:
        CacheService.delete(cls._all_cache_key(user_id))
        CacheService.delete(cls._unread_cache_key(user_id))
        CacheService.delete(cls._count_cache_key(user_id))

    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        priority: str = "medium",
        incident_id: int | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            incident_id=incident_id,
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        self._invalidate_user_cache(user_id)

        logger.info(
            "Notification created: id=%s user_id=%s incident_id=%s",
            notification.id,
            user_id,
            incident_id,
        )

        return notification

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
    ):
        if unread_only:
            cache_key = self._unread_cache_key(user_id)
        else:
            cache_key = self._all_cache_key(user_id)

        cached_data = CacheService.get(cache_key)

        if cached_data is not None:
            return cached_data

        query = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
        )

        if unread_only:
            query = query.filter(
                Notification.is_read.is_(False)
            )

        notifications = (
            query
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

        # Convert ORM objects to dictionaries so Redis
        # can safely serialize the cached response.
        result = [
            {
                "id": notification.id,
                "user_id": notification.user_id,
                "incident_id": notification.incident_id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority,
                "is_read": notification.is_read,
                "created_at": (
                    notification.created_at.isoformat()
                    if notification.created_at
                    else None
                ),
            }
            for notification in notifications
        ]

        CacheService.set(
            cache_key,
            result,
            expire=60,
        )

        return result

    def get_unread_count(self, user_id: int) -> int:
        cache_key = self._count_cache_key(user_id)

        cached_data = CacheService.get(cache_key)

        if cached_data is not None:
            return int(cached_data)

        count = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .count()
        )

        CacheService.set(
            cache_key,
            count,
            expire=60,
        )

        return count

    def mark_as_read(
        self,
        notification_id: int,
        user_id: int,
    ) -> Notification:
        notification = (
            self.db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .first()
        )

        if notification is None:
            raise HTTPException(
                status_code=404,
                detail="Notification not found",
            )

        notification.is_read = True

        self.db.commit()
        self.db.refresh(notification)

        self._invalidate_user_cache(user_id)

        logger.info(
            "Notification marked as read: id=%s user_id=%s",
            notification_id,
            user_id,
        )

        return notification

    def mark_all_as_read(self, user_id: int) -> int:
        notifications = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .all()
        )

        for notification in notifications:
            notification.is_read = True

        self.db.commit()

        self._invalidate_user_cache(user_id)

        logger.info(
            "Marked %s notifications as read for user_id=%s",
            len(notifications),
            user_id,
        )

        return len(notifications)

    def notification_exists(
        self,
        user_id: int,
        incident_id: int,
        notification_type: str,
    ) -> bool:
        return (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.incident_id == incident_id,
                Notification.type == notification_type,
            )
            .first()
            is not None
        )

    def notify_high_priority_incident(
        self,
        incident,
    ):
        if incident.priority not in {"high", "critical"}:
            return 0

        recipients = []

        # Incident reporter
        if incident.reporter_id:
            recipients.append(incident.reporter_id)

        # Administrators
        admin_users = (
            self.db.query(User)
            .filter(User.role == "admin")
            .all()
        )

        recipients.extend(
            user.id
            for user in admin_users
            if user.id != incident.reporter_id
        )

        notification_type = (
            "critical_incident"
            if incident.priority == "critical"
            else "high_priority_incident"
        )

        title = (
            "Critical Incident Alert"
            if incident.priority == "critical"
            else "High Priority Incident Alert"
        )

        message = (
            f"Incident #{incident.id} has been classified as "
            f"{incident.priority} priority. "
            f"Category: {incident.predicted_category or 'Unknown'}."
        )

        created = 0

        for user_id in recipients:
            if self.notification_exists(
                user_id=user_id,
                incident_id=incident.id,
                notification_type=notification_type,
            ):
                logger.info(
                    "Skipping duplicate notification: "
                    "user_id=%s incident_id=%s type=%s",
                    user_id,
                    incident.id,
                    notification_type,
                )
                continue

            self.create_notification(
                user_id=user_id,
                incident_id=incident.id,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=incident.priority,
            )

            created += 1

        return created