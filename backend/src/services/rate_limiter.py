"""Multi-layered Rate Limiter Service.

Implements per-platform rate limiting with:
- Hourly limits (LinkedIn: 5/hr, Indeed: 10/hr, Glassdoor: 3/hr)
- Daily limits (LinkedIn: 50/day, Indeed: 100/day, Glassdoor: 30/day)
- In-memory cache for fast limit checks
- Automatic day reset at midnight
- Retry time calculation
"""

from typing import Optional, Dict
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.utils.logger import get_logger


class RateLimitResult:
    """Result of a rate limit check."""

    allowed: bool
    retry_after: Optional[datetime] = None

    def __init__(self, allowed: bool, retry_after: Optional[datetime] = None):
        self.allowed = allowed
        self.retry_after = retry_after

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "allowed": self.allowed,
            "retry_after": self.retry_after.isoformat() if self.retry_after else None,
        }


class RateLimiter:
    """Multi-layered rate limiter with per-platform quotas.

    Implements:
    - Per-platform hourly limits (LinkedIn: 5/hr, Indeed: 10/hr, Glassdoor: 3/hr)
    - Per-platform daily limits (LinkedIn: 50/day, Indeed: 100/day, Glassdoor: 30/day)
    - In-memory cache for fast limit checks
    - Automatic day reset at midnight
    - Minimum thresholds to prevent spammy automation
    """

    # Platform-specific rate limits
    PLATFORM_LIMITS = {
        "linkedin": {
            "hourly_limit": 5,
            "daily_limit": 50,
            "minimum_threshold": 1,  # Minimum: 1 application per hour
        },
        "indeed": {
            "hourly_limit": 10,
            "daily_limit": 100,
            "minimum_threshold": 2,  # Minimum: 2 applications per hour
        },
        "glassdoor": {
            "hourly_limit": 3,
            "daily_limit": 30,
            "minimum_threshold": 1,  # Minimum: 1 application per hour
        },
        "email": {
            "hourly_limit": 5,
            "daily_limit": 20,
            "minimum_threshold": 2,  # Minimum: 2 emails per hour
        },
    }

    def __init__(self, session: AsyncSession, user_id: str):
        """Initialize rate limiter."""
        self.session = session
        self.user_id = user_id
        self.logger = get_logger(__name__)
        self.cache: Dict[str, Dict] = {}  # In-memory cache: {platform: rate_data}
        self.current_date = datetime.now(timezone.utc)

        # Track rate data: {platform: {hourly_count, daily_count, last_reset}}
        self.rate_data = {
            "linkedin": {"hourly_count": 0, "daily_count": 0, "last_reset": None},
            "indeed": {"hourly_count": 0, "daily_count": 0, "last_reset": None},
            "glassdoor": {"hourly_count": 0, "daily_count": 0, "last_reset": None},
            "email": {"hourly_count": 0, "daily_count": 0, "last_reset": None},
        }

    async def can_apply(self, platform: str) -> RateLimitResult:
        """Check if user can apply to a job on given platform.

        Args:
            platform: Platform name (e.g., "linkedin", "indeed", "glassdoor")

        Returns:
            RateLimitResult with allowed status and retry_after timestamp if blocked
        """
        try:
            # Check day reset (midnight)
            if self._should_reset_day(platform):
                await self._reset_day(platform)

            # Get platform limits
            limits = self.PLATFORM_LIMITS.get(platform)
            if not limits:
                self.logger.warning(f"No rate limits defined for platform: {platform}")
                return RateLimitResult(allowed=True)

            # Get cached rate data
            cached = self.cache.get(platform)
            if cached:
                current_date = datetime.now(timezone.utc)
                # Check if cached data is from today
                if (
                    cached["last_reset"]
                    and cached["last_reset"].date() < self.current_date.date()
                ):
                    # Cached data is from yesterday, check if day changed
                    if cached["last_reset"].date() < self.current_date.date():
                        # Day changed, reset counters
                        cached["hourly_count"] = 0
                        cached["daily_count"] = 0
                        cached["last_reset"] = self.current_date
                    rate_data = cached
                else:
                    # Cached data is from today, use as-is
                    rate_data = cached
            else:
                # No cached data, use rate_data from self.rate_data as fallback
                rate_data = self.rate_data.get(
                    platform, {"hourly_count": 0, "daily_count": 0, "last_reset": None}
                )

            # Check hourly limit
            if rate_data["hourly_count"] >= limits["hourly_limit"]:
                self.logger.info(
                    f"Hourly limit reached for {platform}: "
                    f"{rate_data['hourly_count']}/{limits['hourly_limit']}"
                )
                # Calculate retry time (next hour)
                retry_after = (datetime.now(timezone.utc) + timedelta(hours=1)).replace(
                    minute=0, second=0, microsecond=0
                )
                return RateLimitResult(allowed=False, retry_after=retry_after)

            # Check daily limit
            if rate_data["daily_count"] >= limits["daily_limit"]:
                self.logger.info(
                    f"Daily limit reached for {platform}: "
                    f"{rate_data['daily_count']}/{limits['daily_limit']}"
                )
                # Calculate retry time (tomorrow midnight)
                retry_after = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                return RateLimitResult(allowed=False, retry_after=retry_after)

            # Check minimum threshold
            if rate_data["hourly_count"] < limits["minimum_threshold"]:
                self.logger.warning(
                    f"Below minimum threshold for {platform}: "
                    f"{rate_data['hourly_count']}/{limits['minimum_threshold']}"
                )
                # Wait until minimum threshold
                # Calculate time until next slot
                remaining_slots = (
                    limits["minimum_threshold"] - rate_data["hourly_count"]
                )
                seconds_per_slot = (
                    3600 / limits["minimum_threshold"]
                )  # 1 hour in seconds
                retry_after = datetime.now(timezone.utc) + timedelta(
                    seconds=seconds_per_slot * remaining_slots
                )
                return RateLimitResult(allowed=False, retry_after=retry_after)

            # All checks passed, allow application
            self.logger.debug(
                f"Application allowed for {platform}: "
                f"{rate_data['hourly_count']}/{limits['hourly_limit']} "
                f"(hourly), {rate_data['daily_count']}/{limits['daily_limit']} (daily)"
            )
            return RateLimitResult(allowed=True)

        except Exception as e:
            self.logger.error(f"Error checking rate limits for {platform}: {e}")
            # Allow application if rate limiter fails (fail-safe)
            return RateLimitResult(allowed=True)

    async def record_application(self, platform: str) -> None:
        """Record a job application against rate limits.

        Args:
            platform: Platform name (e.g., "linkedin", "indeed", "glassdoor")
        """
        try:
            # Update in-memory cache
            if platform in self.cache:
                cached = self.cache[platform]
                # Check if day reset needed
                if (
                    cached["last_reset"]
                    and cached["last_reset"].date() < self.current_date.date()
                ):
                    # Day changed, reset counters
                    cached["hourly_count"] = 0
                    cached["daily_count"] = 0
                    cached["last_reset"] = self.current_date

                # Increment counters
                cached["hourly_count"] += 1
                cached["daily_count"] += 1

                # Update cache
                self.cache[platform] = cached

                self.logger.debug(
                    f"Recorded application for {platform}: "
                    f"Hourly: {cached['hourly_count']}, Daily: {cached['daily_count']}"
                )

            # Persist to database (will need DBRateLimit model in future task)
            # await self._persist_to_database(platform, cached)

        except Exception as e:
            self.logger.error(f"Error recording application for {platform}: {e}")

    def _should_reset_day(self, platform: str) -> bool:
        """Check if day reset is needed (midnight).

        Args:
            platform: Platform name to check

        Returns:
            True if day should be reset, False otherwise
        """
        current = datetime.now(timezone.utc)

        # Get last reset time
        if platform in self.rate_data:
            last_reset = self.rate_data[platform]["last_reset"]
            if last_reset:
                # Check if last reset was yesterday
                if last_reset.date() < current.date():
                    # Reset at midnight (new day)
                    return True
                else:
                    # Last reset was today, no reset needed
                    return False
            else:
                # No previous reset, need first reset
                return True

        return False

    async def _reset_day(self, platform: str) -> None:
        """Reset daily counters for a platform.

        Args:
            platform: Platform name to reset
        """
        try:
            # Reset cached data
            cached = self.cache.get(
                platform, {"hourly_count": 0, "daily_count": 0, "last_reset": None}
            )
            if cached:
                # Update cache
                self.cache[platform] = {
                    "hourly_count": 0,
                    "daily_count": 0,
                    "last_reset": self.current_date,
                }

                # Update in-memory rate data
                self.rate_data[platform]["hourly_count"] = 0
                self.rate_data[platform]["daily_count"] = 0
                self.rate_data[platform]["last_reset"] = self.current_date

                self.logger.info(f"Reset day for {platform}")

            # Persist to database (will need DBRateLimit model in future task)
            # await self._persist_to_database(platform, cached)

        except Exception as e:
            self.logger.error(f"Error resetting day for {platform}: {e}")

    def _persist_to_database(self, platform: str, rate_data: dict) -> None:
        """Persist rate data to database.

        Args:
            platform: Platform name
            rate_data: Rate data to persist

        Note:
            This is a placeholder. In Task 1.6, we will create
            DBRateLimit model and implement full database persistence.
        """
        # Placeholder: Will implement in Task 1.6
        pass

    def get_rate_status(self, platform: str) -> Dict:
        """Get current rate status for a platform.

        Args:
            platform: Platform name (e.g., "linkedin", "indeed")

        Returns:
            Dictionary with rate status for API responses
        """
        cached = self.cache.get(platform)
        if cached:
            limits = self.PLATFORM_LIMITS.get(platform)
            remaining_hourly = max(0, limits["hourly_limit"] - cached["hourly_count"])
            remaining_daily = max(0, limits["daily_limit"] - cached["daily_count"])
            remaining_hourly_pct = (
                int((remaining_hourly / limits["hourly_limit"]) * 100)
                if limits["hourly_limit"] > 0
                else 0
            )

            return {
                "platform": platform,
                "hourly_limit": limits["hourly_limit"],
                "daily_limit": limits["daily_limit"],
                "hourly_used": cached["hourly_count"],
                "daily_used": cached["daily_count"],
                "remaining_hourly": remaining_hourly,
                "remaining_daily": remaining_daily,
                "remaining_hourly_pct": remaining_hourly_pct,
                "reset_time": cached["last_reset"].isoformat()
                if cached["last_reset"]
                else None,
                "status": "active"
                if cached["hourly_count"] < limits["hourly_limit"]
                and cached["daily_count"] < limits["daily_limit"]
                else "blocked",
            }
        else:
            # No cached data, return default status
            limits = self.PLATFORM_LIMITS.get(platform)
            return {
                "platform": platform,
                "hourly_limit": limits["hourly_limit"],
                "daily_limit": limits["daily_limit"],
                "hourly_used": 0,
                "daily_used": 0,
                "remaining_hourly": limits["hourly_limit"],
                "remaining_daily": limits["daily_limit"],
                "remaining_hourly_pct": 100,
                "reset_time": None,
                "status": "active",
            }

    def clear_cache(self) -> None:
        """Clear in-memory cache for a user."""
        self.cache.clear()
        self.logger.info("Cleared rate limiter cache")
