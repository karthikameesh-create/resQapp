from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.rate_limiter import limiter
from app.db.dependencies import get_db
from app.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Bad Request / Email already exists"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("5/minute")
def register(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    try:
        return service.register_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"description": "Invalid credentials"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("10/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    credentials = LoginRequest(
        email=form_data.username,
        password=form_data.password,
    )

    token = service.login_user(credentials)

    return TokenResponse(
        access_token=token,
    )