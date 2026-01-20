"""Unit tests for scheduler service."""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

# Ensure `src` package is importable when running tests without installing the
# project into the current environment.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from src.services.scheduler_service import (
    SchedulerService,
    ReminderType,
    ReminderConfig,
    ReminderJob,
)
from src.services.notification_service import NotificationService


class TestSchedulerService:
    """Test cases for SchedulerService class."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing."""
        config = MagicMock()
        config.SCHEDULER_ENABLED = True
        config.TIMEZONE = "UTC"
        config.CHECK_INTERVAL = 60
        return config

    @pytest.fixture
    def mock_notification_service(self):
        """Create mock notification service."""
        service = MagicMock(spec=NotificationService)
        service.send_reminder = AsyncMock(return_value=True)
        service.send_bulk_reminders = AsyncMock(return_value={"sent": 5, "failed": 0})
        return service

    @pytest.fixture
    def scheduler_service(self, mock_config, mock_notification_service):
        """Create SchedulerService with mocked dependencies."""
        with patch("src.services.scheduler_service.config", mock_config):
            service = SchedulerService(notification_service=mock_notification_service)
            return service

    def test_service_initialization(self, scheduler_service):
        """Test service initializes with correct settings."""
        assert scheduler_service is not None
        assert scheduler_service.scheduler is not None
        assert scheduler_service._reminders == {}
        assert scheduler_service._running is False

    @pytest.mark.asyncio
    async def test_start_scheduler(self, scheduler_service):
        """Test starting the scheduler."""
        with patch.object(scheduler_service.scheduler, "start", new_callable=AsyncMock):
            await scheduler_service.start()

            assert scheduler_service._running is True

    @pytest.mark.asyncio
    async def test_stop_scheduler(self, scheduler_service):
        """Test stopping the scheduler."""
        scheduler_service._running = True

        with patch.object(
            scheduler_service.scheduler, "shutdown", new_callable=AsyncMock
        ):
            await scheduler_service.stop()

            assert scheduler_service._running is False

    @pytest.mark.asyncio
    async def test_schedule_reminder(self, scheduler_service):
        """Test scheduling a reminder."""
        scheduler_service._running = True

        config = ReminderConfig(
            reminder_type=ReminderType.FOLLOW_UP,
            application_id="app_123",
            user_id="user_456",
            scheduled_time=datetime.utcnow() + timedelta(days=7),
            metadata={"job_title": "Software Engineer"},
        )

        job_id = await scheduler_service.schedule_reminder(config)

        assert job_id is not None
        assert job_id in scheduler_service._reminders

    @pytest.mark.asyncio
    async def test_cancel_reminder(self, scheduler_service):
        """Test canceling a scheduled reminder."""
        # First schedule a reminder
        config = ReminderConfig(
            reminder_type=ReminderType.FOLLOW_UP,
            application_id="app_123",
            user_id="user_456",
            scheduled_time=datetime.utcnow() + timedelta(days=7),
        )

        job_id = await scheduler_service.schedule_reminder(config)

        # Now cancel it
        with patch.object(
            scheduler_service.scheduler, "remove_job", new_callable=AsyncMock
        ):
            result = await scheduler_service.cancel_reminder(job_id)

            assert result is True
            assert job_id not in scheduler_service._reminders

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_reminder(self, scheduler_service):
        """Test canceling a non-existent reminder."""
        result = await scheduler_service.cancel_reminder("nonexistent_id")

        assert result is False

    @pytest.mark.asyncio
    async def test_get_pending_reminders(self, scheduler_service):
        """Test getting pending reminders."""
        # Schedule multiple reminders
        for i in range(3):
            config = ReminderConfig(
                reminder_type=ReminderType.FOLLOW_UP,
                application_id=f"app_{i}",
                user_id="user_456",
                scheduled_time=datetime.utcnow() + timedelta(days=7),
            )
            await scheduler_service.schedule_reminder(config)

        pending = scheduler_service.get_pending_reminders()

        assert len(pending) == 3

    @pytest.mark.asyncio
    async def test_get_reminder_by_id(self, scheduler_service):
        """Test getting a specific reminder by ID."""
        config = ReminderConfig(
            reminder_type=ReminderType.STATUS_CHECK,
            application_id="app_123",
            user_id="user_456",
            scheduled_time=datetime.utcnow() + timedelta(days=14),
        )

        job_id = await scheduler_service.schedule_reminder(config)

        reminder = scheduler_service.get_reminder(job_id)

        assert reminder is not None
        assert reminder.application_id == "app_123"

    @pytest.mark.asyncio
    async def test_update_reminder(self, scheduler_service):
        """Test updating a scheduled reminder."""
        config = ReminderConfig(
            reminder_type=ReminderType.FOLLOW_UP,
            application_id="app_123",
            user_id="user_456",
            scheduled_time=datetime.utcnow() + timedelta(days=7),
        )

        job_id = await scheduler_service.schedule_reminder(config)

        # Update the reminder
        new_config = ReminderConfig(
            reminder_type=ReminderType.INTERVIEW_PREP,
            application_id="app_123",
            user_id="user_456",
            scheduled_time=datetime.utcnow() + timedelta(days=1),
        )

        result = await scheduler_service.update_reminder(job_id, new_config)

        assert result is True

    @pytest.mark.asyncio
    async def test_schedule_follow_up_reminder(self, scheduler_service):
        """Test scheduling a follow-up reminder."""
        scheduler_service._running = True

        job_id = await scheduler_service.schedule_follow_up_reminder(
            application_id="app_123",
            user_id="user_456",
            days_until_reminder=7,
            metadata={"company_name": "TechCorp"},
        )

        assert job_id is not None
        reminder = scheduler_service.get_reminder(job_id)
        assert reminder.reminder_type == ReminderType.FOLLOW_UP

    @pytest.mark.asyncio
    async def test_schedule_status_check_reminder(self, scheduler_service):
        """Test scheduling a status check reminder."""
        scheduler_service._running = True

        job_id = await scheduler_service.schedule_status_check_reminder(
            application_id="app_123", user_id="user_456", days_until_reminder=14
        )

        assert job_id is not None
        reminder = scheduler_service.get_reminder(job_id)
        assert reminder.reminder_type == ReminderType.STATUS_CHECK

    @pytest.mark.asyncio
    async def test_schedule_interview_prep_reminder(self, scheduler_service):
        """Test scheduling an interview preparation reminder."""
        scheduler_service._running = True

        interview_time = datetime.utcnow() + timedelta(days=2)

        job_id = await scheduler_service.schedule_interview_prep_reminder(
            application_id="app_123",
            user_id="user_456",
            interview_time=interview_time,
            days_before_interview=2,
        )

        assert job_id is not None
        reminder = scheduler_service.get_reminder(job_id)
        assert reminder.reminder_type == ReminderType.INTERVIEW_PREP

    @pytest.mark.asyncio
    async def test_process_reminders(
        self, scheduler_service, mock_notification_service
    ):
        """Test processing due reminders."""
        # Schedule a reminder that's due now
        config = ReminderConfig(
            reminder_type=ReminderType.FOLLOW_UP,
            application_id="app_123",
            user_id="user_456",
            scheduled_time=datetime.utcnow(),  # Due immediately
        )

        job_id = await scheduler_service.schedule_reminder(config)

        # Process the reminder
        with patch.object(scheduler_service.scheduler, "get_jobs", return_value=[]):
            processed = await scheduler_service.process_due_reminders()

            # Should have processed the reminder
            mock_notification_service.send_reminder.assert_called()

    @pytest.mark.asyncio
    async def test_get_reminder_stats(self, scheduler_service):
        """Test getting reminder statistics."""
        # Schedule various reminders
        for i in range(3):
            config = ReminderConfig(
                reminder_type=ReminderType.FOLLOW_UP,
                application_id=f"app_{i}",
                user_id="user_456",
                scheduled_time=datetime.utcnow() + timedelta(days=7),
            )
            await scheduler_service.schedule_reminder(config)

        stats = scheduler_service.get_stats()

        assert stats["total_pending"] == 3
        assert stats["running"] is False
        assert "by_type" in stats

    @pytest.mark.asyncio
    async def test_cleanup_old_reminders(self, scheduler_service):
        """Test cleaning up old reminders."""
        # Add some old reminders
        old_reminder = ReminderJob(
            id="old_reminder",
            config=ReminderConfig(
                reminder_type=ReminderType.FOLLOW_UP,
                application_id="app_old",
                user_id="user_456",
                scheduled_time=datetime.utcnow() - timedelta(days=30),
            ),
            created_at=datetime.utcnow() - timedelta(days=30),
        )

        scheduler_service._reminders["old_reminder"] = old_reminder

        # Add a recent reminder
        recent_reminder = ReminderJob(
            id="recent_reminder",
            config=ReminderConfig(
                reminder_type=ReminderType.FOLLOW_UP,
                application_id="app_recent",
                user_id="user_456",
                scheduled_time=datetime.utcnow() + timedelta(days=7),
            ),
            created_at=datetime.utcnow(),
        )

        scheduler_service._reminders["recent_reminder"] = recent_reminder

        with patch.object(
            scheduler_service.scheduler, "remove_job", new_callable=AsyncMock
        ):
            cleaned = await scheduler_service.cleanup_old_reminders(days_old=7)

            assert cleaned == 1  # Only old reminder should be cleaned
            assert "recent_reminder" in scheduler_service._reminders
            assert "old_reminder" not in scheduler_service._reminders


class TestReminderConfig:
    """Test cases for ReminderConfig class."""

    def test_follow_up_reminder_config(self):
        """Test creating follow-up reminder configuration."""
        config = ReminderConfig(
            reminder_type=ReminderType.FOLLOW_UP,
            application_id="app_123",
            user_id="user_456",
            scheduled_time=datetime.utcnow() + timedelta(days=7),
        )

        assert config.reminder_type == ReminderType.FOLLOW_UP
        assert config.application_id == "app_123"

    def test_interview_prep_reminder_config(self):
        """Test creating interview preparation reminder configuration."""
        config = ReminderConfig(
            reminder_type=ReminderType.INTERVIEW_PREP,
            application_id="app_123",
            user_id="user_456",
            scheduled_time=datetime.utcnow() + timedelta(days=2),
            metadata={"interview_type": "technical"},
        )

        assert config.reminder_type == ReminderType.INTERVIEW_PREP
        assert config.metadata["interview_type"] == "technical"


class TestReminderJob:
    """Test cases for ReminderJob class."""

    def test_reminder_job_creation(self):
        """Test creating a reminder job."""
        config = ReminderConfig(
            reminder_type=ReminderType.FOLLOW_UP,
            application_id="app_123",
            user_id="user_456",
            scheduled_time=datetime.utcnow() + timedelta(days=7),
        )

        job = ReminderJob(id="job_123", config=config, created_at=datetime.utcnow())

        assert job.id == "job_123"
        assert job.config == config
        assert job.created_at is not None
        assert job.status == "pending"

    def test_reminder_job_status_transition(self):
        """Test reminder job status transitions."""
        config = ReminderConfig(
            reminder_type=ReminderType.FOLLOW_UP,
            application_id="app_123",
            user_id="user_456",
            scheduled_time=datetime.utcnow() + timedelta(days=7),
        )

        job = ReminderJob(id="job_123", config=config, created_at=datetime.utcnow())

        # Initial status
        assert job.status == "pending"

        # Mark as sent
        job.mark_sent()
        assert job.status == "sent"
        assert job.sent_at is not None

        # Mark as failed
        job.mark_failed(error="Test error")
        assert job.status == "failed"
        assert job.error == "Test error"


class TestReminderType:
    """Test cases for ReminderType enum."""

    def test_reminder_types(self):
        """Test all reminder types are defined."""
        assert ReminderType.FOLLOW_UP.value == "follow_up"
        assert ReminderType.STATUS_CHECK.value == "status_check"
        assert ReminderType.INTERVIEW_PREP.value == "interview_prep"
