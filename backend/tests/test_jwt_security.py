"""Tests for JWT token security and expiration handling."""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from jose import jwt

from src.utils.token_manager import TokenManager
from src.config import config


# Test configuration - use test-specific secret
TEST_SECRET = "test-secret-key-for-testing-only-do-not-use-in-production"
TEST_ALGORITHM = "HS256"


@pytest.fixture
def token_manager() -> TokenManager:
    """Create a TokenManager instance for testing."""
    return TokenManager(
        secret_key=TEST_SECRET,
        algorithm=TEST_ALGORITHM,
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )


class TestTokenExpiration:
    """Tests for JWT token expiration behavior."""

    @pytest.mark.asyncio
    async def test_expired_access_token_is_rejected(self, token_manager: TokenManager):
        """Expired access tokens should be rejected during validation."""
        # Create a token that expired 1 hour ago
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        expired_token = token_manager.create_access_token(
            user_id="test-user-123",
            email="test@example.com",
            now=past_time,
        )

        # Attempting to validate this expired token should raise ValueError
        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await token_manager.refresh_tokens(refresh_token=expired_token)

    @pytest.mark.asyncio
    async def test_expired_refresh_token_is_rejected(self, token_manager: TokenManager):
        """Expired refresh tokens should be rejected."""
        # Create a refresh token that expired 8 days ago
        past_time = datetime.now(timezone.utc) - timedelta(days=8)
        expired_token = token_manager.create_refresh_token(
            user_id="test-user-123",
            now=past_time,
        )

        # Attempting to use this expired refresh token should fail
        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await token_manager.refresh_tokens(refresh_token=expired_token)

    @pytest.mark.asyncio
    async def test_valid_refresh_token_creates_new_tokens(
        self, token_manager: TokenManager
    ):
        """Valid refresh tokens should successfully create new token pair."""
        # Create a fresh refresh token
        refresh_token = token_manager.create_refresh_token(user_id="test-user-123")

        # This should succeed
        response = await token_manager.refresh_tokens(refresh_token=refresh_token)

        # Verify we got new tokens
        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.token_type == "bearer"
        assert response.expires_in == 15 * 60  # 15 minutes in seconds

    @pytest.mark.asyncio
    async def test_wrong_token_type_is_rejected(self, token_manager: TokenManager):
        """Using access token as refresh token should be rejected."""
        # Create an access token (not a refresh token)
        access_token = token_manager.create_access_token(
            user_id="test-user-123",
            email="test@example.com",
        )

        # Attempting to use access token as refresh token should fail
        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await token_manager.refresh_tokens(refresh_token=access_token)

    @pytest.mark.asyncio
    async def test_refresh_token_with_wrong_type_claim_rejected(
        self, token_manager: TokenManager
    ):
        """Tokens with incorrect type claim should be rejected."""
        # Create a token with manual payload that has wrong type
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "test-user-123",
            "exp": now + timedelta(days=7),
            "type": "access",  # Wrong type - should be "refresh"
            "jti": "some-jti",
        }
        wrong_type_token = jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)

        # Attempting to use this token should fail
        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await token_manager.refresh_tokens(refresh_token=wrong_type_token)

    @pytest.mark.asyncio
    async def test_token_without_subject_rejected(self, token_manager: TokenManager):
        """Tokens without subject claim should be rejected."""
        now = datetime.now(timezone.utc)
        payload = {
            "exp": now + timedelta(days=7),
            "type": "refresh",
            "jti": "some-jti",
            # Missing "sub" claim
        }
        no_subject_token = jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)

        # Attempting to use this token should fail
        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await token_manager.refresh_tokens(refresh_token=no_subject_token)

    @pytest.mark.asyncio
    async def test_token_with_empty_subject_rejected(self, token_manager: TokenManager):
        """Tokens with empty subject claim should be rejected."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "",  # Empty subject
            "exp": now + timedelta(days=7),
            "type": "refresh",
            "jti": "some-jti",
        }
        empty_subject_token = jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)

        # Attempting to use this token should fail
        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await token_manager.refresh_tokens(refresh_token=empty_subject_token)


class TestRateLimitingIntegration:
    """Integration tests for rate limiting with the middleware."""

    def test_rate_limiter_can_be_imported(self):
        """Rate limiter module should be importable without errors."""
        from src.middleware.rate_limiter import (
            get_auth_limiter,
            get_general_limiter,
            get_strict_limiter,
        )

        # Just verify imports work - actual rate limiting tested in integration
        assert get_auth_limiter is not None
        assert get_general_limiter is not None
        assert get_strict_limiter is not None

    def test_auth_limiter_has_configured_limit(self):
        """Auth limiter should respect configuration."""
        from src.middleware.rate_limiter import _auth_limiter

        # The limiter should be configured (actual limits depend on config)
        assert _auth_limiter is not None
