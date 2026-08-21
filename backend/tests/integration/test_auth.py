import pytest
from fastapi import HTTPException

# Register all SQLAlchemy models before model instances are created.
from app.models.user import User
from app.models.incident import Incident
from app.models.incident_history import IncidentHistory
from app.models.notification import Notification

from app.models.enums import UserRole
from app.schemas.user import LoginRequest, UserCreate
from app.services.auth_service import AuthService
from app.core.security import decode_access_token


class FakeUserRepository:
    users: dict[str, User] = {}

    def __init__(self, db):
        self.db = db

    def get_by_email(self, email: str):
        return self.users.get(email)

    def create(self, user: User):
        user.id = len(self.users) + 1
        self.users[user.email] = user
        return user


@pytest.fixture(autouse=True)
def reset_users(monkeypatch):
    FakeUserRepository.users = {}

    monkeypatch.setattr(
        "app.services.auth_service.UserRepository",
        FakeUserRepository,
    )


def test_register_creates_citizen_user():
    service = AuthService(db=None)

    result = service.register_user(
        UserCreate(
            full_name="Integration User",
            email="integration@example.com",
            password="StrongPass@123",
        )
    )

    assert result.id == 1
    assert result.email == "integration@example.com"
    assert result.full_name == "Integration User"
    assert result.role == UserRole.CITIZEN
    assert result.is_active is True
    assert result.password_hash != "StrongPass@123"


def test_duplicate_registration_is_rejected():
    service = AuthService(db=None)

    data = UserCreate(
        full_name="Integration User",
        email="integration@example.com",
        password="StrongPass@123",
    )

    service.register_user(data)

    with pytest.raises(ValueError, match="Email already registered"):
        service.register_user(data)


def test_login_returns_valid_access_token():
    service = AuthService(db=None)

    service.register_user(
        UserCreate(
            full_name="Integration User",
            email="integration@example.com",
            password="StrongPass@123",
        )
    )

    token = service.login_user(
        LoginRequest(
            email="integration@example.com",
            password="StrongPass@123",
        )
    )

    assert token
    assert (
        decode_access_token(token)
        == "integration@example.com"
    )


def test_login_with_wrong_password_is_rejected():
    service = AuthService(db=None)

    service.register_user(
        UserCreate(
            full_name="Integration User",
            email="integration@example.com",
            password="StrongPass@123",
        )
    )

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        service.login_user(
            LoginRequest(
                email="integration@example.com",
                password="WrongPassword@123",
            )
        )

    assert exc_info.value.status_code == 401
    assert (
        exc_info.value.detail
        == "Invalid email or password"
    )


def test_login_with_unknown_email_is_rejected():
    service = AuthService(db=None)

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        service.login_user(
            LoginRequest(
                email="missing@example.com",
                password="StrongPass@123",
            )
        )

    assert exc_info.value.status_code == 401
    assert (
        exc_info.value.detail
        == "Invalid email or password"
    )