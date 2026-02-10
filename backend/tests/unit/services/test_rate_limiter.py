"""
Unit tests for RateLimiter service.

Tests cover:
- Hourly rate limit checks
- Daily rate limit checks
- Minimum threshold enforcement
- Retry time calculation
- Day reset at midnight
- Application recording and counter increments
- Cache management
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys
from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.services.rate_limiter import RateLimiter, RateLimitResult


class MockAsyncSession:
    """Mock AsyncSession for testing."""

    def __init__(self):
        self.execute = AsyncMock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        self.close = AsyncMock()


class TestRateLimiter:
    """Test cases for RateLimiter service."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return MockAsyncSession()

    @pytest.fixture
    def rate_limiter(self, mock_session):
        """Create RateLimiter instance for testing."""
        return RateLimiter(session=mock_session, user_id="test_user_123")

    @pytest.fixture
    def rate_limiter_with_cache(self, mock_session):
        """Create RateLimiter with pre-filled cache."""
        limiter = RateLimiter(session=mock_session, user_id="test_user_123")
        # Pre-fill cache with some data
        limiter.cache = {
            "linkedin": {
                "hourly_count": 3,
                "daily_count": 20,
                "last_reset": datetime.now(timezone.utc),
            },
            "indeed": {
                "hourly_count": 5,
                "daily_count": 50,
                "last_reset": datetime.now(timezone.utc),
            },
        }
        return limiter

    def test_rate_limiter_initialization(self, rate_limiter):
        """Test RateLimiter initialization."""
        assert rate_limiter.session is not None
        assert rate_limiter.user_id == "test_user_123"
        assert rate_limiter.logger is not None
        assert rate_limiter.cache == {}
        assert rate_limiter.rate_data is not None
        assert len(rate_limiter.rate_data) == 4  # 4 platforms

    def test_platform_limits_defined(self, rate_limiter):
        """Test that all platform limits are defined."""
        limits = rate_limiter.PLATFORM_LIMITS

        assert "linkedin" in limits
        assert "indeed" in limits
        assert "glassdoor" in limits
        assert "email" in limits

        # Check LinkedIn limits
        assert limits["linkedin"]["hourly_limit"] == 5
        assert limits["linkedin"]["daily_limit"] == 50
        assert limits["linkedin"]["minimum_threshold"] == 1

        # Check Indeed limits
        assert limits["indeed"]["hourly_limit"] == 10
        assert limits["indeed"]["daily_limit"] == 100
        assert limits["indeed"]["minimum_threshold"] == 2

        # Check Glassdoor limits
        assert limits["glassdoor"]["hourly_limit"] == 3
        assert limits["glassdoor"]["daily_limit"] == 30
        assert limits["glassdoor"]["minimum_threshold"] == 1

        # Check Email limits
        assert limits["email"]["hourly_limit"] == 5
        assert limits["email"]["daily_limit"] == 20
        assert limits["email"]["minimum_threshold"] == 2

    def test_rate_limit_result_creation(self):
        """Test RateLimitResult dataclass."""
        # Test allowed result
        result = RateLimitResult(allowed=True)
        assert result.allowed is True
        assert result.retry_after is None

        # Test blocked result with retry time
        retry_time = datetime.now(timezone.utc) + timedelta(hours=1)
        result = RateLimitResult(allowed=False, retry_after=retry_time)
        assert result.allowed is False
        assert result.retry_after == retry_time

    def test_rate_limit_result_to_dict(self):
        """Test RateLimitResult.to_dict() method."""
        # Test with no retry time
        result = RateLimitResult(allowed=True)
        dict_result = result.to_dict()
        assert dict_result["allowed"] is True
        assert dict_result["retry_after"] is None

        # Test with retry time
        retry_time = datetime.now(timezone.utc) + timedelta(hours=1)
        result = RateLimitResult(allowed=False, retry_after=retry_time)
        dict_result = result.to_dict()
        assert dict_result["allowed"] is False
        assert dict_result["retry_after"] == retry_time.isoformat()

    @pytest.mark.asyncio
    async def test_can_apply_within_limits(self, rate_limiter):
        """Test can_apply when within limits."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 2,
                "daily_count": 20,
                "last_reset": datetime.now(timezone.utc),
            }
        }

        result = await rate_limiter.can_apply("linkedin")

        assert result.allowed is True
        assert result.retry_after is None

    @pytest.mark.asyncio
    async def test_can_apply_hourly_limit_reached(self, rate_limiter):
        """Test can_apply when hourly limit is reached."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 5,  # At hourly limit
                "daily_count": 20,
                "last_reset": datetime.now(timezone.utc),
            }
        }

        result = await rate_limiter.can_apply("linkedin")

        assert result.allowed is False
        assert result.retry_after is not None
        # Retry should be at the next hour
        assert result.retry_after.minute == 0
        assert result.retry_after.second == 0

    @pytest.mark.asyncio
    async def test_can_apply_daily_limit_reached(self, rate_limiter):
        """Test can_apply when daily limit is reached."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 4,
                "daily_count": 50,  # At daily limit
                "last_reset": datetime.now(timezone.utc),
            }
        }

        result = await rate_limiter.can_apply("linkedin")

        assert result.allowed is False
        assert result.retry_after is not None
        # Retry should be at midnight tomorrow
        assert result.retry_after.hour == 0
        assert result.retry_after.minute == 0
        assert result.retry_after.second == 0

    @pytest.mark.asyncio
    async def test_can_apply_unsupported_platform(self, rate_limiter):
        """Test can_apply with unsupported platform."""
        result = await rate_limiter.can_apply("unsupported_platform")

        # Should allow by default for unknown platforms
        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_can_apply_empty_cache(self, rate_limiter):
        """Test can_apply with empty cache (first application)."""
        rate_limiter.cache = {}

        result = await rate_limiter.can_apply("linkedin")

        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_record_application_increments_counters(self, rate_limiter):
        """Test that record_application increments counters."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 3,
                "daily_count": 20,
                "last_reset": datetime.now(timezone.utc),
            }
        }

        await rate_limiter.record_application("linkedin")

        # Counters should be incremented
        assert rate_limiter.cache["linkedin"]["hourly_count"] == 4
        assert rate_limiter.cache["linkedin"]["daily_count"] == 21

    @pytest.mark.asyncio
    async def test_record_application_new_platform(self, rate_limiter):
        """Test record_application for new platform (no existing cache)."""
        rate_limiter.cache = {}

        await rate_limiter.record_application("glassdoor")

        # Should create new entry with count 1
        assert "glassdoor" in rate_limiter.cache
        assert rate_limiter.cache["glassdoor"]["hourly_count"] == 1
        assert rate_limiter.cache["glassdoor"]["daily_count"] == 1

    @pytest.mark.asyncio
    async def test_record_application_multiple_platforms(self, rate_limiter):
        """Test recording applications on multiple platforms."""
        rate_limiter.cache = {}

        # Record applications on different platforms
        await rate_limiter.record_application("linkedin")
        await rate_limiter.record_application("indeed")
        await rate_limiter.record_application("glassdoor")

        assert rate_limiter.cache["linkedin"]["hourly_count"] == 1
        assert rate_limiter.cache["indeed"]["hourly_count"] == 1
        assert rate_limiter.cache["glassdoor"]["hourly_count"] == 1

    @pytest.mark.asyncio
    async def test_get_rate_status_with_cache(self, rate_limiter_with_cache):
        """Test get_rate_status with cached data."""
        status = rate_limiter_with_cache.get_rate_status("linkedin")

        assert status["platform"] == "linkedin"
        assert status["hourly_limit"] == 5
        assert status["daily_limit"] == 50
        assert status["hourly_used"] == 3
        assert status["daily_used"] == 20
        assert status["remaining_hourly"] == 2
        assert status["remaining_daily"] == 30
        assert status["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_rate_status_no_cache(self, rate_limiter):
        """Test get_rate_status with no cache data."""
        rate_limiter.cache = {}

        status = rate_limiter.get_rate_status("linkedin")

        assert status["platform"] == "linkedin"
        assert status["hourly_used"] == 0
        assert status["daily_used"] == 0
        assert status["remaining_hourly"] == 5
        assert status["remaining_daily"] == 50
        assert status["remaining_hourly_pct"] == 100
        assert status["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_rate_status_blocked(self, rate_limiter):
        """Test get_rate_status when blocked."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 5,
                "daily_count": 50,
                "last_reset": datetime.now(timezone.utc),
            }
        }

        status = rate_limiter.get_rate_status("linkedin")

        assert status["hourly_used"] == 5
        assert status["daily_used"] == 50
        assert status["remaining_hourly"] == 0
        assert status["remaining_daily"] == 0
        assert status["status"] == "blocked"

    def test_clear_cache(self, rate_limiter_with_cache):
        """Test cache clearing."""
        assert len(rate_limiter_with_cache.cache) == 2

        rate_limiter_with_cache.clear_cache()

        assert rate_limiter_with_cache.cache == {}

    def test_should_reset_day_same_day(self, rate_limiter):
        """Test _should_reset_day returns False for same day."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 3,
                "daily_count": 20,
                "last_reset": datetime.now(timezone.utc),
            }
        }

        result = rate_limiter._should_reset_day("linkedin")

        assert result is False

    def test_should_reset_day_different_day(self, rate_limiter):
        """Test _should_reset_day returns True for different day."""
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        rate_limiter.cache = {
            "linkedin": {"hourly_count": 3, "daily_count": 20, "last_reset": yesterday}
        }

        result = rate_limiter._should_reset_day("linkedin")

        assert result is True

    @pytest.mark.asyncio
    async def test_reset_day(self, rate_limiter):
        """Test _reset_day method."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 5,
                "daily_count": 50,
                "last_reset": datetime.now(timezone.utc) - timedelta(hours=5),
            }
        }

        await rate_limiter._reset_day("linkedin")

        # Counters should be reset
        assert rate_limiter.cache["linkedin"]["hourly_count"] == 0
        assert rate_limiter.cache["linkedin"]["daily_count"] == 0
        assert rate_limiter.cache["linkedin"]["last_reset"] == rate_limiter.current_date

    @pytest.mark.asyncio
    async def test_error_handling_can_apply(self, rate_limiter):
        """Test error handling in can_apply."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 3,
                "daily_count": 20,
                "last_reset": "invalid_date",  # This will cause an error
            }
        }

        # Should not raise, should return allowed=True (fail-safe)
        result = await rate_limiter.can_apply("linkedin")
        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_error_handling_record_application(self, rate_limiter):
        """Test error handling in record_application."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 3,
                "daily_count": 20,
                "last_reset": "invalid_date",  # This will cause an error
            }
        }

        # Should not raise
        await rate_limiter.record_application("linkedin")

    @pytest.mark.asyncio
    async def test_retry_time_calculation_hourly(self, rate_limiter):
        """Test retry time calculation when hourly limit reached."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 5,  # At limit
                "daily_count": 20,
                "last_reset": datetime.now(timezone.utc),
            }
        }

        result = await rate_limiter.can_apply("linkedin")

        assert result.allowed is False
        assert result.retry_after is not None
        # Should be in the future
        assert result.retry_after > datetime.now(timezone.utc)

    @pytest.mark.asyncio
    async def test_retry_time_calculation_daily(self, rate_limiter):
        """Test retry time calculation when daily limit reached."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 4,
                "daily_count": 50,  # At limit
                "last_reset": datetime.now(timezone.utc),
            }
        }

        result = await rate_limiter.can_apply("linkedin")

        assert result.allowed is False
        assert result.retry_after is not None
        # Should be tomorrow
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        assert result.retry_after.date() == tomorrow.date()


class TestRateLimiterEdgeCases:
    """Edge case tests for RateLimiter service."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return MockAsyncSession()

    @pytest.fixture
    def rate_limiter(self, mock_session):
        """Create RateLimiter instance."""
        return RateLimiter(session=mock_session, user_id="test_user")

    @pytest.mark.asyncio
    async def test_consecutive_applications(self, rate_limiter):
        """Test multiple consecutive applications."""
        rate_limiter.cache = {}

        # Apply 5 times (LinkedIn hourly limit)
        for i in range(5):
            result = await rate_limiter.can_apply("linkedin")
            assert result.allowed is True
            await rate_limiter.record_application("linkedin")

        # 6th should be blocked
        result = await rate_limiter.can_apply("linkedin")
        assert result.allowed is False

    @pytest.mark.asyncio
    async def test_minimum_threshold_check(self, rate_limiter):
        """Test minimum threshold enforcement."""
        # Set very low count to test minimum threshold
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 0,
                "daily_count": 0,
                "last_reset": datetime.now(timezone.utc),
            }
        }

        # LinkedIn minimum_threshold is 1, so hourly_count=0 should trigger warning
        # but still allow application (threshold is for preventing too-sparse applications)
        result = await rate_limiter.can_apply("linkedin")
        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_all_platforms_status(self, rate_limiter):
        """Test getting status for all platforms."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 1,
                "daily_count": 10,
                "last_reset": datetime.now(timezone.utc),
            },
            "indeed": {
                "hourly_count": 2,
                "daily_count": 20,
                "last_reset": datetime.now(timezone.utc),
            },
            "glassdoor": {
                "hourly_count": 1,
                "daily_count": 5,
                "last_reset": datetime.now(timezone.utc),
            },
            "email": {
                "hourly_count": 3,
                "daily_count": 15,
                "last_reset": datetime.now(timezone.utc),
            },
        }

        platforms = ["linkedin", "indeed", "glassdoor", "email"]
        for platform in platforms:
            status = rate_limiter.get_rate_status(platform)
            assert status["platform"] == platform
            assert status["hourly_used"] > 0
            assert status["daily_used"] > 0

    @pytest.mark.asyncio
    async def test_rate_data_initialization(self, rate_limiter):
        """Test that rate_data is properly initialized."""
        assert rate_limiter.rate_data["linkedin"]["hourly_count"] == 0
        assert rate_limiter.rate_data["linkedin"]["daily_count"] == 0
        assert rate_limiter.rate_data["indeed"]["hourly_count"] == 0
        assert rate_limiter.rate_data["glassdoor"]["hourly_count"] == 0
        assert rate_limiter.rate_data["email"]["hourly_count"] == 0

    @pytest.mark.asyncio
    async def test_persist_to_database_placeholder(self, rate_limiter):
        """Test that _persist_to_database is a no-op placeholder."""
        # This is a placeholder method, should not raise
        rate_limiter._persist_to_database(
            "linkedin", {"hourly_count": 1, "daily_count": 10}
        )

    @pytest.mark.asyncio
    async def test_day_change_handling(self, rate_limiter):
        """Test that day change is properly handled."""
        # Cache from yesterday
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        rate_limiter.cache = {
            "linkedin": {"hourly_count": 5, "daily_count": 50, "last_reset": yesterday}
        }

        # Check if day should be reset
        should_reset = rate_limiter._should_reset_day("linkedin")
        assert should_reset is True

        # Reset the day
        await rate_limiter._reset_day("linkedin")

        # Counters should be reset
        assert rate_limiter.cache["linkedin"]["hourly_count"] == 0
        assert rate_limiter.cache["linkedin"]["daily_count"] == 0

    @pytest.mark.asyncio
    async def test_large_counter_values(self, rate_limiter):
        """Test handling of large counter values."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 999999,
                "daily_count": 999999,
                "last_reset": datetime.now(timezone.utc),
            }
        }

        result = await rate_limiter.can_apply("linkedin")

        assert result.allowed is False
        assert result.retry_after is not None

    @pytest.mark.asyncio
    async def test_zero_limit_edge_case(self, rate_limiter):
        """Test edge case with zero limit (if ever configured)."""
        # Temporarily modify platform limits for testing
        original_limit = rate_limiter.PLATFORM_LIMITS["linkedin"]["hourly_limit"]
        rate_limiter.PLATFORM_LIMITS["linkedin"]["hourly_limit"] = 0

        try:
            rate_limiter.cache = {
                "linkedin": {
                    "hourly_count": 0,
                    "daily_count": 0,
                    "last_reset": datetime.now(timezone.utc),
                }
            }

            result = await rate_limiter.can_apply("linkedin")

            # Should be blocked (0 limit)
            assert result.allowed is False
        finally:
            # Restore original limit
            rate_limiter.PLATFORM_LIMITS["linkedin"]["hourly_limit"] = original_limit


class TestRateLimiterIntegration:
    """Integration-style tests for RateLimiter with realistic scenarios."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        return MockAsyncSession()

    @pytest.fixture
    def rate_limiter(self, mock_session):
        """Create RateLimiter instance."""
        return RateLimiter(session=mock_session, user_id="test_user")

    @pytest.mark.asyncio
    async def test_daily_limit_scenario(self, rate_limiter):
        """Test realistic daily limit scenario."""
        rate_limiter.cache = {}

        # Simulate a full day's applications (limited by hourly limit)
        # LinkedIn: 5/hr limit, 50/day limit
        # With 5 per hour, need 10 hours to reach 50
        for i in range(50):
            # Check if we hit hourly limit
            hourly_count = rate_limiter.cache.get("linkedin", {}).get("hourly_count", 0)
            if hourly_count >= 5:
                # Simulate hour passing by resetting hourly counter only
                if "linkedin" in rate_limiter.cache:
                    rate_limiter.cache["linkedin"]["hourly_count"] = 0

            result = await rate_limiter.can_apply("linkedin")
            assert result.allowed is True
            await rate_limiter.record_application("linkedin")

        # Verify counters
        assert rate_limiter.cache["linkedin"]["daily_count"] == 50

        # Next application should be blocked
        result = await rate_limiter.can_apply("linkedin")
        assert result.allowed is False

        # Status should show blocked
        status = rate_limiter.get_rate_status("linkedin")
        assert status["status"] == "blocked"
        assert status["remaining_daily"] == 0

    @pytest.mark.asyncio
    async def test_multi_platform_scenario(self, rate_limiter):
        """Test rate limiting across multiple platforms."""
        rate_limiter.cache = {}

        # Apply to multiple platforms
        platforms = ["linkedin", "indeed", "glassdoor"]

        for platform in platforms:
            # Apply up to hourly limit
            limits = rate_limiter.PLATFORM_LIMITS[platform]
            for _ in range(limits["hourly_limit"]):
                result = await rate_limiter.can_apply(platform)
                assert result.allowed is True
                await rate_limiter.record_application(platform)

            # Next should be blocked
            result = await rate_limiter.can_apply(platform)
            assert result.allowed is False

        # Each platform should be at its limit
        for platform in platforms:
            assert (
                rate_limiter.cache[platform]["hourly_count"]
                == rate_limiter.PLATFORM_LIMITS[platform]["hourly_limit"]
            )

    @pytest.mark.asyncio
    async def test_rate_status_percentage_calculation(self, rate_limiter):
        """Test remaining percentage calculation."""
        rate_limiter.cache = {
            "linkedin": {
                "hourly_count": 2,  # 40% used of 5
                "daily_count": 25,  # 50% used of 50
                "last_reset": datetime.now(timezone.utc),
            }
        }

        status = rate_limiter.get_rate_status("linkedin")

        assert status["remaining_hourly_pct"] == 60  # (5-2)/5 * 100 = 60%
        assert status["remaining_hourly"] == 3
        assert status["remaining_daily"] == 25

    @pytest.mark.asyncio
    async def test_concurrent_session_isolation(self, rate_limiter, mock_session):
        """Test that each RateLimiter instance has isolated cache."""
        # Create two rate limiters for different users
        limiter1 = RateLimiter(session=mock_session, user_id="user1")
        limiter2 = RateLimiter(session=mock_session, user_id="user2")

        # Record application for user1
        await limiter1.record_application("linkedin")

        # User1 should have count=1
        assert limiter1.cache["linkedin"]["hourly_count"] == 1

        # User2 should have empty cache (isolated)
        assert (
            "linkedin" not in limiter2.cache
            or limiter2.cache["linkedin"]["hourly_count"] == 0
        )


@pytest.mark.asyncio
async def test_can_apply_resets_cached_day():
    mock_session = cast(AsyncSession, MockAsyncSession())
    rate_limiter = RateLimiter(session=mock_session, user_id="test_user_123")
    now = datetime.now(timezone.utc)
    rate_limiter.current_date = now + timedelta(days=1)
    rate_limiter.cache = {
        "linkedin": {
            "hourly_count": 2,
            "daily_count": 10,
            "last_reset": now,
        }
    }

    result = await rate_limiter.can_apply("linkedin")

    assert result.allowed is True
    assert rate_limiter.cache["linkedin"]["hourly_count"] == 0
    assert rate_limiter.cache["linkedin"]["daily_count"] == 0
    assert (
        rate_limiter.cache["linkedin"]["last_reset"].date()
        == rate_limiter.current_date.date()
    )


@pytest.mark.asyncio
async def test_can_apply_uses_rate_data_when_no_cache():
    mock_session = cast(AsyncSession, MockAsyncSession())
    rate_limiter = RateLimiter(session=mock_session, user_id="test_user_123")
    rate_limiter.cache = {}
    rate_limiter.rate_data["linkedin"] = {
        "hourly_count": 1,
        "daily_count": 2,
        "last_reset": datetime.now(timezone.utc),
    }

    result = await rate_limiter.can_apply("linkedin")

    assert result.allowed is True


@pytest.mark.asyncio
async def test_record_application_resets_day_in_cache():
    mock_session = cast(AsyncSession, MockAsyncSession())
    rate_limiter = RateLimiter(session=mock_session, user_id="test_user_123")
    rate_limiter.current_date = datetime.now(timezone.utc)
    rate_limiter.cache = {
        "linkedin": {
            "hourly_count": 4,
            "daily_count": 20,
            "last_reset": rate_limiter.current_date - timedelta(days=1),
        }
    }

    await rate_limiter.record_application("linkedin")

    assert rate_limiter.cache["linkedin"]["hourly_count"] == 1
    assert rate_limiter.cache["linkedin"]["daily_count"] == 1


def test_should_reset_day_cache_no_last_reset():
    mock_session = cast(AsyncSession, MockAsyncSession())
    rate_limiter = RateLimiter(session=mock_session, user_id="test_user_123")
    rate_limiter.cache = {
        "linkedin": {"hourly_count": 0, "daily_count": 0, "last_reset": None}
    }

    assert rate_limiter._should_reset_day("linkedin") is True


def test_should_reset_day_rate_data_today():
    mock_session = cast(AsyncSession, MockAsyncSession())
    rate_limiter = RateLimiter(session=mock_session, user_id="test_user_123")
    rate_limiter.cache = {}
    rate_limiter.rate_data["linkedin"]["last_reset"] = datetime.now(timezone.utc)

    assert rate_limiter._should_reset_day("linkedin") is False


def test_should_reset_day_rate_data_yesterday():
    mock_session = cast(AsyncSession, MockAsyncSession())
    rate_limiter = RateLimiter(session=mock_session, user_id="test_user_123")
    rate_limiter.cache = {}
    rate_limiter.rate_data["linkedin"]["last_reset"] = datetime.now(
        timezone.utc
    ) - timedelta(days=1)

    assert rate_limiter._should_reset_day("linkedin") is True


@pytest.mark.asyncio
async def test_reset_day_handles_exception():
    mock_session = cast(AsyncSession, MockAsyncSession())
    rate_limiter = RateLimiter(session=mock_session, user_id="test_user_123")
    rate_limiter.logger = AsyncMock()

    class BrokenCache(dict):
        def get(self, *args, **kwargs):
            raise RuntimeError("boom")

    rate_limiter.cache = BrokenCache()
    await rate_limiter._reset_day("linkedin")

    rate_limiter.logger.error.assert_called_once()


def test_get_rate_status_unknown_platform_with_last_reset():
    mock_session = cast(AsyncSession, MockAsyncSession())
    rate_limiter = RateLimiter(session=mock_session, user_id="test_user_123")
    last_reset = datetime.now(timezone.utc)
    rate_limiter.cache["unknown"] = {
        "hourly_count": 1,
        "daily_count": 2,
        "last_reset": last_reset,
    }

    status = rate_limiter.get_rate_status("unknown")

    assert status["status"] == "unknown"
    assert status["reset_time"] == last_reset.isoformat()
