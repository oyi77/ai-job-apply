"""Session manager for handling platform session cookies with caching."""

import json
from datetime import datetime, timezone, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DBSessionCookie
from src.database.repositories.session_cookie_repository import SessionCookieRepository
from src.database.config import database_config
from src.utils.logger import get_logger


class SessionManager:
    """Manages session cookies with in-memory cache and database persistence.

    Features:
    - In-memory cache for fast access
    - Database persistence via SessionCookieRepository
    - Automatic expiry checking
    - 7-day default session expiry
    """

    def __init__(self) -> None:
        """Initialize session manager with empty cache."""
        self.logger = get_logger(__name__)
        # Cache structure: {(user_id, platform): {"cookies": dict, "expires_at": datetime}}
        self._cache: dict[tuple[str, str], dict[str, object]] = {}
        self._repository_class = SessionCookieRepository

    @asynccontextmanager
    async def _get_session_repo(self):  # type: ignore[no-untyped-def]
        """Context manager for database session and repository."""
        async with database_config.get_session() as session:
            yield session, self._repository_class(session)

    def _get_cache_key(self, user_id: str, platform: str) -> tuple[str, str]:
        """Generate cache key from user_id and platform."""
        return (user_id, platform)  # type: ignore[return-value]

    def _is_expired(self, expires_at: datetime) -> bool:
        """Check if a session has expired."""
        now = datetime.now(timezone.utc)
        # Ensure expires_at is timezone-aware
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at <= now

    async def load_session(self, user_id: str, platform: str) -> Optional[dict]:
        """Load session cookies for a user on a specific platform.

        Strategy:
        1. Check in-memory cache first
        2. If not in cache or expired, query database
        3. If found in database and not expired, update cache and return
        4. Return None if not found or expired

        Args:
            user_id: User ID
            platform: Platform name (e.g., "linkedin", "indeed", "glassdoor")

        Returns:
            Dictionary of cookies if found and not expired, None otherwise
        """
        cache_key = self._get_cache_key(user_id, platform)

        # Check cache first
        if cache_key in self._cache:
            cached_data = self._cache[cache_key]
            if not self._is_expired(cached_data["expires_at"]):
                self.logger.debug(f"Session cache hit for user {user_id} on {platform}")
                return cached_data["cookies"]
            else:
                # Remove expired entry from cache
                del self._cache[cache_key]
                self.logger.debug(
                    f"Session cache expired for user {user_id} on {platform}"
                )

        # Query database
        async with self._get_session_repo() as (session, repository):
            db_session = await repository.get_by_user_platform(user_id, platform)

            if not db_session:
                self.logger.debug(
                    f"No session found in database for user {user_id} on {platform}"
                )
                return None

            # Check if expired
            if self._is_expired(db_session.expires_at):
                self.logger.debug(
                    f"Session expired in database for user {user_id} on {platform}"
                )
                return None

            # Parse cookies from JSON string
            try:
                cookies = json.loads(db_session.cookies)
            except (json.JSONDecodeError, TypeError):
                self.logger.warning(
                    f"Failed to parse cookies for user {user_id} on {platform}"
                )
                return None

            # Update cache
            self._cache[cache_key] = {
                "cookies": cookies,
                "expires_at": db_session.expires_at,
            }

            self.logger.debug(
                f"Session loaded from database for user {user_id} on {platform}"
            )
            return cookies  # type: ignore[return-value]

    async def save_session(self, user_id: str, platform: str, cookies: dict) -> bool:
        """Save session cookies for a user on a specific platform.

        Strategy:
        1. Update in-memory cache
        2. Persist to database (create or update)
        3. Use 7-day expiry

        Args:
            user_id: User ID
            platform: Platform name
            cookies: Dictionary of cookies to save

        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Calculate expiry (7 days from now)
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)

            # Update cache
            cache_key = self._get_cache_key(user_id, platform)
            self._cache[cache_key] = {
                "cookies": cookies,
                "expires_at": expires_at,
            }

            # Persist to database
            async with self._get_session_repo() as (session, repository):
                # Check if session already exists
                existing = await repository.get_by_user_platform(user_id, platform)

                if existing:
                    # Update existing session
                    cookies_json = json.dumps(cookies)
                    success = await repository.update_cookies(
                        user_id, platform, cookies_json
                    )
                    if success:
                        self.logger.info(
                            f"Updated session for user {user_id} on {platform}"
                        )
                    else:
                        self.logger.warning(
                            f"Failed to update session for user {user_id} on {platform}"
                        )
                    return success  # type: ignore[return-value]
                else:
                    # Create new session
                    cookies_json = json.dumps(cookies)
                    db_session = DBSessionCookie(
                        user_id=user_id,
                        platform=platform,
                        cookies=cookies_json,
                        expires_at=expires_at,
                    )

                    created = await repository.create(db_session)
                    if created:
                        self.logger.info(
                            f"Created session for user {user_id} on {platform}"
                        )
                        return True
                    else:
                        self.logger.warning(
                            f"Failed to create session for user {user_id} on {platform}"
                        )
                        return False

        except Exception as e:
            self.logger.error(
                f"Error saving session for user {user_id} on {platform}: {e}",
                exc_info=True,
            )
            return False

    async def delete_session(self, user_id: str, platform: str) -> bool:
        """Delete session cookies for a user on a specific platform.

        Args:
            user_id: User ID
            platform: Platform name

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Remove from cache
            cache_key = self._get_cache_key(user_id, platform)
            if cache_key in self._cache:
                del self._cache[cache_key]

            # Delete from database
            async with self._get_session_repo() as (session, repository):
                success = await repository.delete_by_user_platform(user_id, platform)
                if success:
                    self.logger.info(
                        f"Deleted session for user {user_id} on {platform}"
                    )
                return success  # type: ignore[return-value]

        except Exception as e:
            self.logger.error(
                f"Error deleting session for user {user_id} on {platform}: {e}",
                exc_info=True,
            )
            return False

    async def clear_cache(self) -> None:
        """Clear all in-memory cache entries."""
        self._cache.clear()
        self.logger.info("Session cache cleared")

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from the database.

        Returns:
            Number of deleted session records
        """
        try:
            async with self._get_session_repo() as (session, repository):
                deleted_count = await repository.delete_expired_sessions()
                self.logger.info(f"Cleaned up {deleted_count} expired sessions")
                return deleted_count  # type: ignore[return-value]

        except Exception as e:
            self.logger.error(f"Error cleaning up expired sessions: {e}", exc_info=True)
            return 0  # type: ignore[return-value]
