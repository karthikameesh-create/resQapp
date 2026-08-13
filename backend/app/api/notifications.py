from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.rate_limiter import limiter
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationCountResponse,
    NotificationResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
@limiter.limit("100/minute")
def get_notifications(
    request: Request,
    unread_only: bool = False,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    return service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
    )


@router.get(
    "/unread",
    response_model=list[NotificationResponse],
)
@limiter.limit("100/minute")
def get_unread_notifications(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    return service.get_user_notifications(
        user_id=current_user.id,
        unread_only=True,
    )


@router.get(
    "/unread-count",
    response_model=NotificationCountResponse,
)
@limiter.limit("100/minute")
def get_unread_count(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    return {
        "unread_count": service.get_unread_count(
            current_user.id
        )
    }


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
@limiter.limit("30/minute")
def mark_notification_as_read(
    request: Request,
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    return service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )


@router.put(
    "/read-all",
    response_model=NotificationCountResponse,
)
@limiter.limit("30/minute")
def mark_all_notifications_as_read(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)

    count = service.mark_all_as_read(
        user_id=current_user.id,
    )

    return {
        "unread_count": count,
    }