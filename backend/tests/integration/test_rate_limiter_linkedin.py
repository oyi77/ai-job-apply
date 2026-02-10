"""Integration test for LinkedIn hourly rate limiting."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

import pytest

from src.database.config import Base, database_config
from src.services.rate_limiter import RateLimiter


@pytest.fixture(scope="module", autouse=True)
async def setup_test_db():
    await database_config.initialize(test_mode=True)
    engine = database_config.engine
    assert engine is not None
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    engine = database_config.engine
    assert engine is not None
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await database_config.close()


@pytest.fixture
async def rate_limiter():
    user_id = f"test-user-{uuid.uuid4()}"
    async with database_config.get_session() as session:
        yield RateLimiter(session=session, user_id=user_id)


@pytest.mark.asyncio
async def test_linkedin_hourly_limit_blocks_sixth_application(rate_limiter):
    now = datetime.now(timezone.utc)
    rate_limiter.cache = {
        "linkedin": {
            "hourly_count": 0,
            "daily_count": 0,
            "last_reset": now,
        }
    }

    for _ in range(5):
        await rate_limiter.record_application("linkedin")

    result = await rate_limiter.can_apply("linkedin")

    assert result.allowed is False
    assert result.retry_after is not None
    assert result.retry_after > now
    assert result.retry_after <= now + timedelta(hours=1)
    assert result.retry_after.minute == 0
    assert result.retry_after.second == 0


@pytest.mark.asyncio
async def test_linkedin_daily_limit_blocks_fifty_first_application(rate_limiter):
    before_check = datetime.now(timezone.utc)
    rate_limiter.cache = {
        "linkedin": {
            "hourly_count": 4,
            "daily_count": 50,
            "last_reset": before_check,
        }
    }

    result = await rate_limiter.can_apply("linkedin")
    after_check = datetime.now(timezone.utc)

    expected_before = (before_check + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    expected_after = (after_check + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    assert result.allowed is False
    assert result.retry_after is not None
    assert result.retry_after > before_check
    assert result.retry_after in {expected_before, expected_after}
    assert result.retry_after.hour == 0
    assert result.retry_after.minute == 0
    assert result.retry_after.second == 0
    assert result.retry_after.microsecond == 0
