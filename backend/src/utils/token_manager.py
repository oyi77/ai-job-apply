"""JWT token creation and refresh utilities.

This module provides a small, testable surface area for JWT handling that can be
used by service-layer authentication code.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Final
from uuid import uuid4

from jose import JWTError, jwt

from src.models.user import TokenResponse
from src.validators.auth_validators import ensure_timezone_aware, validate_non_empty_str


@dataclass(frozen=True, slots=True)
class TokenManager:
    """Create and refresh JWT access/refresh tokens."""

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    ACCESS_TOKEN_TYPE: Final[str] = "access"
    REFRESH_TOKEN_TYPE: Final[str] = "refresh"

    def create_access_token(
        self,
        *,
        user_id: str,
        email: str | None = None,
        now: datetime | None = None,
    ) -> str:
        token_now = ensure_timezone_aware(self._now(now))
        expire = token_now + timedelta(minutes=self.access_token_expire_minutes)

        payload: dict[str, object] = {
            "sub": user_id,
            "exp": expire,
            "type": self.ACCESS_TOKEN_TYPE,
        }
        if email is not None:
            payload["email"] = email

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, *, user_id: str, now: datetime | None = None) -> str:
        token_now = ensure_timezone_aware(self._now(now))
        expire = token_now + timedelta(days=self.refresh_token_expire_days)
        payload: dict[str, object] = {
            "sub": user_id,
            "exp": expire,
            "type": self.REFRESH_TOKEN_TYPE,
            "jti": str(uuid4()),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    async def refresh_tokens(
        self, *, refresh_token: str, now: datetime | None = None
    ) -> TokenResponse:
        """Refresh access+refresh tokens (refresh token rotation).

        This is pure JWT validation/rotation. Persistent session validation
        (e.g. checking a DB session table) is responsibility of the caller.
        """

        token_now = ensure_timezone_aware(self._now(now))
        user_id = self._get_valid_refresh_subject(refresh_token, now=token_now)

        access_token = self.create_access_token(user_id=user_id, now=token_now)
        new_refresh_token = self.create_refresh_token(user_id=user_id, now=token_now)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
        )

    def _get_valid_refresh_subject(self, token: str, *, now: datetime) -> str:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "require_exp": True,
                },
            )
        except JWTError as exc:
            raise ValueError("Invalid or expired refresh token") from exc

        if payload.get("type") != self.REFRESH_TOKEN_TYPE:
            raise ValueError("Invalid or expired refresh token")

        try:
            user_id = validate_non_empty_str(payload.get("sub"), field_name="subject")
        except ValueError as exc:
            raise ValueError("Invalid or expired refresh token") from exc

        # `jwt.decode` already verified exp, but we keep this strict check as a
        # guardrail if decode options change in future.
        exp = payload.get("exp")
        if isinstance(exp, (int, float)):
            exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc)
            if exp_dt < now:
                raise ValueError("Invalid or expired refresh token")

        return user_id

    @staticmethod
    def _now(now: datetime | None) -> datetime:
        if now is None:
            return datetime.now(timezone.utc)
        if now.tzinfo is None:
            return now.replace(tzinfo=timezone.utc)
        return now
