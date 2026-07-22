from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.oauth2 import oauth2_scheme
from app.core.security import decode_access_token
from app.db.dependencies import get_db
from app.repositories.user_repository import UserRepository


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        email = decode_access_token(token)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    repo = UserRepository(db)

    user = repo.get_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user