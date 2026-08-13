from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import require_admin
from app.core.rate_limiter import limiter
from app.db.dependencies import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
@limiter.limit("60/minute")
def get_me(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get(
    "/",
    response_model=list[UserResponse],
)
@limiter.limit("30/minute")
def get_all_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    repo = UserRepository(db)
    return repo.get_all()