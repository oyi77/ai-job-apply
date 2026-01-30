"""Rate limit repository for database operations."""

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from src.database.models import DBRateLimit
from src.utils.logger import get_logger


class RateLimitRepository:
    """Repository for rate limit database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
        self.logger = get_logger(__name__)

    async def create(self, rate_limit: DBRateLimit) -> DBRateLimit:
        """Create a new rate limit record.

        Args:
            rate_limit: DBRateLimit instance to create

        Returns:
            Created DBRateLimit instance

        Raises:
            Exception: If creation fails
        """
        try:
            self.session.add(rate_limit)
            await self.session.commit()
            await self.session.refresh(rate_limit)

            self.logger.info(
                f"Created rate limit for user {rate_limit.user_id} "
                f"on platform {rate_limit.platform}"
            )
            return rate_limit

        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating rate limit: {e}", exc_info=True)
            raise

    async def get_by_user_platform(
        self, user_id: str, platform: str
    ) -> Optional[DBRateLimit]:
        """Get rate limit by user ID and platform.

        Args:
            user_id: User ID
            platform: Platform name (e.g., "linkedin", "indeed", "glassdoor")

        Returns:
            DBRateLimit if found, None otherwise
        """
        try:
            stmt = select(DBRateLimit).where(
                DBRateLimit.user_id == user_id,
                DBRateLimit.platform == platform,
            )
            result = await self.session.execute(stmt)
            rate_limit = result.scalar_one_or_none()

            if rate_limit:
                self.logger.debug(f"Found rate limit for user {user_id} on {platform}")
            else:
                self.logger.debug(
                    f"No rate limit found for user {user_id} on {platform}"
                )

            return rate_limit

        except Exception as e:
            self.logger.error(
                f"Error getting rate limit for user {user_id} on {platform}: {e}",
                exc_info=True,
            )
            return None

    async def get_or_create(
        self,
        user_id: str,
        platform: str,
        hourly_limit: int,
        daily_limit: int,
    ) -> DBRateLimit:
        """Get existing rate limit or create new one.

        Args:
            user_id: User ID
            platform: Platform name
            hourly_limit: Maximum applications per hour
            daily_limit: Maximum applications per day

        Returns:
            Existing or newly created DBRateLimit instance
        """
        try:
            # Try to get existing record
            existing = await self.get_by_user_platform(user_id, platform)

            if existing:
                # Update limits if they've changed
                if (
                    existing.hourly_limit != hourly_limit
                    or existing.daily_limit != daily_limit
                ):
                    stmt = (
                        update(DBRateLimit)
                        .where(
                            DBRateLimit.user_id == user_id,
                            DBRateLimit.platform == platform,
                        )
                        .values(
                            hourly_limit=hourly_limit,
                            daily_limit=daily_limit,
                            updated_at=datetime.now(timezone.utc),
                        )
                    )
                    await self.session.execute(stmt)
                    await self.session.commit()
                    await self.session.refresh(existing)

                    self.logger.info(
                        f"Updated rate limits for user {user_id} on {platform}: "
                        f"{hourly_limit}/hr, {daily_limit}/day"
                    )

                return existing
            else:
                # Create new record
                new_limit = DBRateLimit(
                    user_id=user_id,
                    platform=platform,
                    applications_count=0,
                    hourly_limit=hourly_limit,
                    daily_limit=daily_limit,
                    last_reset=datetime.now(timezone.utc),
                )
                created = await self.create(new_limit)
                return created

        except Exception as e:
            self.logger.error(
                f"Error in get_or_create for user {user_id} on {platform}: {e}",
                exc_info=True,
            )
            raise

    async def update_count(self, user_id: str, platform: str) -> bool:
        """Increment application count for a rate limit record.

        Args:
            user_id: User ID
            platform: Platform name

        Returns:
            True if update was successful, False if record not found
        """
        try:
            stmt = (
                update(DBRateLimit)
                .where(
                    DBRateLimit.user_id == user_id,
                    DBRateLimit.platform == platform,
                )
                .values(
                    applications_count=DBRateLimit.applications_count + 1,
                    updated_at=datetime.now(timezone.utc),
                )
            )
            result = await self.session.execute(stmt)
            await self.session.commit()

            if result.rowcount > 0:
                self.logger.info(
                    f"Incremented application count for user {user_id} on {platform}"
                )
                return True
            else:
                self.logger.warning(
                    f"No rate limit found to update for user {user_id} on {platform}"
                )
                return False

        except Exception as e:
            await self.session.rollback()
            self.logger.error(
                f"Error updating count for user {user_id} on {platform}: {e}",
                exc_info=True,
            )
            return False

    async def reset_daily_limits(self, user_id: str, platform: str) -> bool:
        """Reset daily application count to zero.

        Args:
            user_id: User ID
            platform: Platform name

        Returns:
            True if reset was successful, False if record not found
        """
        try:
            stmt = (
                update(DBRateLimit)
                .where(
                    DBRateLimit.user_id == user_id,
                    DBRateLimit.platform == platform,
                )
                .values(
                    applications_count=0,
                    last_reset=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            )
            result = await self.session.execute(stmt)
            await self.session.commit()

            if result.rowcount > 0:
                self.logger.info(f"Reset daily limit for user {user_id} on {platform}")
                return True
            else:
                self.logger.warning(
                    f"No rate limit found to reset for user {user_id} on {platform}"
                )
                return False

        except Exception as e:
            await self.session.rollback()
            self.logger.error(
                f"Error resetting daily limit for user {user_id} on {platform}: {e}",
                exc_info=True,
            )
            return False

    async def get_all_by_user(self, user_id: str) -> list[DBRateLimit]:
        """Get all rate limit records for a user.

        Args:
            user_id: User ID

        Returns:
            List of DBRateLimit instances
        """
        try:
            stmt = select(DBRateLimit).where(DBRateLimit.user_id == user_id)
            result = await self.session.execute(stmt)
            rate_limits = result.scalars().all()

            self.logger.debug(
                f"Found {len(rate_limits)} rate limits for user {user_id}"
            )
            return rate_limits

        except Exception as e:
            self.logger.error(
                f"Error getting rate limits for user {user_id}: {e}",
                exc_info=True,
            )
            return []
