"""Tests for auth token refresh behavior.

This is intentionally written against the new TokenManager utility.
"""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from src.utils.token_manager import TokenManager
from src.validators.auth_validators import ensure_timezone_aware, validate_non_empty_str


@pytest.mark.asyncio
async def test_refresh_access_token_rotates_refresh_token() -> None:
    """Refreshing should:
    - validate the refresh token
    - return a new access token
    - rotate (change) the refresh token
    """

    secret_key = "test-secret"
    algorithm = "HS256"
    now = ensure_timezone_aware(datetime.now(timezone.utc))

    manager = TokenManager(
        secret_key=secret_key,
        algorithm=algorithm,
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )

    user_id = validate_non_empty_str("user-123", field_name="user_id")
    refresh_token = manager.create_refresh_token(user_id=user_id, now=now)

    response = await manager.refresh_tokens(refresh_token=refresh_token, now=now)

    # exercise TokenManager's optional email claim path
    _ = manager.create_access_token(user_id=user_id, email="user@example.com", now=now)

    assert response.access_token
    assert response.refresh_token
    assert response.refresh_token != refresh_token
    assert response.token_type == "bearer"
    assert response.expires_in == 15 * 60

    access_payload = jwt.decode(
        response.access_token, secret_key, algorithms=[algorithm]
    )
    assert access_payload["sub"] == "user-123"
    assert access_payload["type"] == "access"

    refresh_payload = jwt.decode(
        response.refresh_token, secret_key, algorithms=[algorithm]
    )
    assert refresh_payload["sub"] == "user-123"
    assert refresh_payload["type"] == "refresh"
    assert refresh_payload["jti"]


@pytest.mark.asyncio
async def test_refresh_access_token_rejects_expired_refresh_token() -> None:
    """Expired refresh tokens should raise a ValueError."""

    secret_key = "test-secret"
    algorithm = "HS256"

    manager = TokenManager(
        secret_key=secret_key,
        algorithm=algorithm,
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )

    expired_now = ensure_timezone_aware(datetime.now(timezone.utc))
    exp = expired_now - timedelta(seconds=1)
    payload = {
        "sub": "user-123",
        "type": "refresh",
        "jti": "jti-123",
        "exp": exp,
    }
    expired_refresh_token = jwt.encode(payload, secret_key, algorithm=algorithm)

    with pytest.raises(ValueError, match="Invalid or expired refresh token"):
        await manager.refresh_tokens(
            refresh_token=expired_refresh_token, now=expired_now
        )


@pytest.mark.asyncio
async def test_refresh_rejects_wrong_token_type_and_missing_subject() -> None:
    """Non-refresh tokens should be rejected, as should missing subjects."""

    secret_key = "test-secret"
    algorithm = "HS256"
    now = ensure_timezone_aware(datetime.now(timezone.utc))

    manager = TokenManager(
        secret_key=secret_key,
        algorithm=algorithm,
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )

    access_token = manager.create_access_token(user_id="user-123", now=now)
    with pytest.raises(ValueError, match="Invalid or expired refresh token"):
        await manager.refresh_tokens(refresh_token=access_token, now=now)

    token = jwt.encode(
        {
            "sub": "",
            "type": "refresh",
            "jti": "jti-123",
            "exp": now + timedelta(days=1),
        },
        secret_key,
        algorithm=algorithm,
    )
    with pytest.raises(ValueError, match="Invalid or expired refresh token"):
        await manager.refresh_tokens(refresh_token=token, now=now)


@pytest.mark.asyncio
async def test_token_manager_normalizes_naive_datetime() -> None:
    """Naive datetimes should be treated as UTC."""

    secret_key = "test-secret"
    algorithm = "HS256"

    manager = TokenManager(
        secret_key=secret_key,
        algorithm=algorithm,
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )

    naive_now = datetime.utcnow()  # intentionally naive
    _ = ensure_timezone_aware(naive_now)
    refresh_token = manager.create_refresh_token(user_id="user-123", now=naive_now)
    response = await manager.refresh_tokens(refresh_token=refresh_token, now=naive_now)
    assert response.access_token
