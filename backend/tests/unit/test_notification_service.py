"""Unit tests for notification service."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from src.services.notification_service import NotificationService


@pytest.fixture
def notification_service() -> NotificationService:
    """Provide a notification service with mocked dependencies."""
    mock_email = MagicMock()
    mock_email.send_email = AsyncMock(return_value=True)
    mock_push = MagicMock()
    return NotificationService(email_service=mock_email, push_service=mock_push)


@pytest.mark.asyncio
async def test_send_follow_up_reminder_success(
    notification_service: NotificationService,
) -> None:
    """Sending follow-up reminder should call email service."""
    result = await notification_service.send_follow_up_reminder(
        user_id="user-123",
        job_title="Software Engineer",
        company="TechCorp",
        application_date="2026-01-01",
        user_email="test@example.com",
        user_name="Test User",
    )

    assert result is True
    notification_service.email_service.send_email.assert_called_once()


@pytest.mark.asyncio
async def test_send_status_check_reminder_success(
    notification_service: NotificationService,
) -> None:
    """Sending status check reminder should call email service."""
    result = await notification_service.send_status_check_reminder(
        user_id="user-456",
        job_title="Product Manager",
        company="StartupXYZ",
        last_update="2026-01-15",
        user_email="pm@example.com",
        user_name="PM User",
    )

    assert result is True
    notification_service.email_service.send_email.assert_called_once()


@pytest.mark.asyncio
async def test_send_interview_prep_reminder_success(
    notification_service: NotificationService,
) -> None:
    """Sending interview prep reminder should call email service."""
    result = await notification_service.send_interview_prep_reminder(
        user_id="user-789",
        job_title="Backend Developer",
        company="BigCo",
        interview_date="2026-02-01T10:00:00",
        user_email="dev@example.com",
        user_name="Dev User",
    )

    assert result is True
    notification_service.email_service.send_email.assert_called_once()


@pytest.mark.asyncio
async def test_initialize_sets_initialized(
    notification_service: NotificationService,
) -> None:
    """Initializing should set _initialized to True."""
    assert notification_service._initialized is False

    result = await notification_service.initialize()

    assert result is True
    assert notification_service._initialized is True


@pytest.mark.asyncio
async def test_health_check_returns_status(
    notification_service: NotificationService,
) -> None:
    """Health check should return healthy status."""
    notification_service._initialized = True

    health = await notification_service.health_check()

    assert health["status"] == "healthy"
    assert health["initialized"] is True
