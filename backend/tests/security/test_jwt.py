from datetime import timedelta

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
)


def test_access_token_round_trip():
    token = create_access_token("test@example.com")

    assert decode_access_token(token) == "test@example.com"


def test_token_contains_security_claims():
    token = create_access_token("test@example.com")

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["sub"] == "test@example.com"
    assert payload["type"] == "access"
    assert "iat" in payload
    assert "exp" in payload


def test_wrong_token_type_is_rejected():
    token = jwt.encode(
        {
            "sub": "test@example.com",
            "type": "refresh",
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(Exception):
        decode_access_token(token)


def test_missing_subject_is_rejected():
    token = jwt.encode(
        {
            "type": "access",
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(Exception):
        decode_access_token(token)


def test_expired_token_is_rejected():
    token = create_access_token(
        "test@example.com",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(Exception):
        decode_access_token(token)


def test_invalid_signature_is_rejected():
    token = jwt.encode(
        {
            "sub": "test@example.com",
            "type": "access",
        },
        "wrong-secret",
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(Exception):
        decode_access_token(token)


def test_wrong_algorithm_is_rejected():
    token = jwt.encode(
        {
            "sub": "test@example.com",
            "type": "access",
        },
        settings.SECRET_KEY,
        algorithm="HS512",
    )

    with pytest.raises(Exception):
        decode_access_token(token)