"""Session cookie repository for database operations."""

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from src.database.models import DBSessionCookie
from src.utils.logger import get_logger


class SessionCookieRepository:
    """Repository for session cookie database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
        self.logger = get_logger(__name__)

    async def create(self, session_cookie: DBSessionCookie) -> DBSessionCookie:
        """Create a new session cookie record.
        
        Args:
            session_cookie: DBSessionCookie instance to create
            
        Returns:
            Created DBSessionCookie instance
            
        Raises:
            Exception: If creation fails
        """
        try:
            self.session.add(session_cookie)
            await self.session.commit()
            await self.session.refresh(session_cookie)

            self.logger.info(
                f"Created session cookie for user {session_cookie.user_id} "
                f"on platform {session_cookie.platform}"
            )
            return session_cookie

        except Exception as e:
            await self.session.rollback()
            self.logger.error(
                f"Error creating session cookie: {e}", exc_info=True
            )
            raise

    async def get_by_user_platform(
        self, user_id: str, platform: str
    ) -> Optional[DBSessionCookie]:
        """Get session cookie by user ID and platform.
        
        Args:
            user_id: User ID
            platform: Platform name (e.g., "linkedin", "indeed", "glassdoor")
            
        Returns:
            DBSessionCookie if found, None otherwise
        """
        try:
            stmt = select(DBSessionCookie).where(
                DBSessionCookie.user_id == user_id,
                DBSessionCookie.platform == platform,
            )
            result = await self.session.execute(stmt)
            session_cookie = result.scalar_one_or_none()

            if session_cookie:
                self.logger.debug(
                    f"Found session cookie for user {user_id} on {platform}"
                )
            else:
                self.logger.debug(
                    f"No session cookie found for user {user_id} on {platform}"
                )

            return session_cookie

        except Exception as e:
            self.logger.error(
                f"Error getting session cookie for user {user_id} "
                f"on {platform}: {e}",
                exc_info=True,
            )
            return None

    async def delete_expired_sessions(self) -> int:
        """Delete all expired session cookies.
        
        Returns:
            Number of deleted session records
        """
        try:
            now = datetime.now(timezone.utc)
            stmt = delete(DBSessionCookie).where(
                DBSessionCookie.expires_at <= now
            )
            result = await self.session.execute(stmt)
            await self.session.commit()

            deleted_count = result.rowcount
            self.logger.info(f"Deleted {deleted_count} expired session cookies")
            return deleted_count

        except Exception as e:
            await self.session.rollback()
            self.logger.error(
                f"Error deleting expired sessions: {e}", exc_info=True
            )
            raise

    async def update_cookies(
        self, user_id: str, platform: str, cookies: str
    ) -> bool:
        """Update cookies for an existing session.
        
        Args:
            user_id: User ID
            platform: Platform name
            cookies: JSON string of cookies
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            stmt = (
                update(DBSessionCookie)
                .where(
                    DBSessionCookie.user_id == user_id,
                    DBSessionCookie.platform == platform,
                )
                .values(cookies=cookies)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()

            if result.rowcount > 0:
                self.logger.info(
                    f"Updated cookies for user {user_id} on {platform}"
                )
                return True
            else:
                self.logger.warning(
                    f"No session cookie found to update for user {user_id} "
                    f"on {platform}"
                )
                return False

        except Exception as e:
            await self.session.rollback()
            self.logger.error(
                f"Error updating cookies for user {user_id} on {platform}: {e}",
                exc_info=True,
            )
            return False

    async def delete_by_user_platform(
        self, user_id: str, platform: str
    ) -> bool:
        """Delete session cookie for a specific user and platform.
        
        Args:
            user_id: User ID
            platform: Platform name
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            stmt = delete(DBSessionCookie).where(
                DBSessionCookie.user_id == user_id,
                DBSessionCookie.platform == platform,
            )
            result = await self.session.execute(stmt)
            await self.session.commit()

            if result.rowcount > 0:
                self.logger.info(
                    f"Deleted session cookie for user {user_id} on {platform}"
                )
                return True
            else:
                self.logger.warning(
                    f"No session cookie found to delete for user {user_id} "
                    f"on {platform}"
                )
                return False

        except Exception as e:
            await self.session.rollback()
            self.logger.error(
                f"Error deleting session cookie for user {user_id} "
                f"on {platform}: {e}",
                exc_info=True,
            )
            return False

    async def get_all_by_user(self, user_id: str) -> list[DBSessionCookie]:
        """Get all session cookies for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of DBSessionCookie instances
        """
        try:
            stmt = select(DBSessionCookie).where(
                DBSessionCookie.user_id == user_id
            )
            result = await self.session.execute(stmt)
            session_cookies = result.scalars().all()

            self.logger.debug(
                f"Found {len(session_cookies)} session cookies for user {user_id}"
            )
            return session_cookies

        except Exception as e:
            self.logger.error(
                f"Error getting session cookies for user {user_id}: {e}",
                exc_info=True,
            )
            return []
