"""Unit tests for scheduler API endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from src.api.v1 import scheduler as scheduler_api
from src.models.user import UserProfile


@pytest.mark.asyncio
async def test_schedule_follow_up_accepts_user_profile() -> None:
    """Scheduler follow-up should accept UserProfile objects."""
    request = scheduler_api.FollowUpReminderRequest(
        application_id="app-123",
        job_title="Backend Engineer",
        company="Acme Co",
        application_date=datetime.now(timezone.utc),
        days_until_followup=0,
    )
    current_user = UserProfile(
        id="user-123",
        email="user@example.com",
        name="Test User",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    scheduler_service = AsyncMock()
    scheduler_service.schedule_follow_up = AsyncMock(return_value="reminder-123")

    with patch("src.services.service_registry.service_registry") as registry:
        registry.get_scheduler_service = AsyncMock(return_value=scheduler_service)
        response = await scheduler_api.schedule_follow_up_reminder(
            request, current_user=current_user
        )

    assert response.success is True
    assert response.reminder_id == "reminder-123"
    scheduler_service.schedule_follow_up.assert_called_once()
    call_kwargs = scheduler_service.schedule_follow_up.call_args.kwargs
    assert call_kwargs["user_id"] == "user-123"
