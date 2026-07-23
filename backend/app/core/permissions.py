from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.models.enums import UserRole
from app.models.user import User


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow only administrators.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


def require_responder_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow responders and administrators.
    """
    if current_user.role not in (
        UserRole.RESPONDER,
        UserRole.ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Responder or Admin access required",
        )

    return current_user


def require_authenticated_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Any authenticated user.
    """
    return current_user