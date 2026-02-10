"""Scheduler service for automated job application reminders using APScheduler."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from src.utils.logger import get_logger


@dataclass
class ReminderConfig:
    """Configuration for job application reminders."""

    enabled: bool = True
    check_interval_hours: int = 24  # How often to check for reminders
    follow_up_days: int = 7  # Days after application to send follow-up reminder
    stale_application_days: int = 14  # Days without update to send check reminder
    max_reminders_per_application: int = 3  # Max reminder emails per application


@dataclass
class ReminderJob:
    """Scheduled reminder job."""

    id: str
    application_id: str
    user_id: str
    reminder_type: str  # 'follow_up', 'check_status', 'interview_prep'
    scheduled_time: datetime
    sent: bool = False
    sent_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class SchedulerService:
    """Main scheduler service for managing job application reminders."""

    def __init__(self, config: Optional[ReminderConfig] = None):
        """Initialize scheduler service."""
        self.logger = get_logger(__name__)
        self.config = config or ReminderConfig()
        self.scheduler = None
        self.reminder_jobs: Dict[str, ReminderJob] = {}
        self._initialized = False
        self._running = False

    async def initialize(self) -> bool:
        """Initialize the scheduler service."""
        try:
            from apscheduler.schedulers.asyncio import (  # type: ignore[import-not-found]
                AsyncIOScheduler,
            )
            from apscheduler.triggers.interval import (  # type: ignore[import-not-found]
                IntervalTrigger,
            )
            from apscheduler.events import (  # type: ignore[import-not-found]
                EVENT_JOB_EXECUTED,
                EVENT_JOB_ERROR,
            )

            self.logger.info("Initializing scheduler service...")

            # Create async scheduler
            self.scheduler = AsyncIOScheduler()

            # Add check reminder job (runs periodically)
            self.scheduler.add_job(
                self._check_reminders,
                IntervalTrigger(hours=self.config.check_interval_hours),
                id="check_reminders",
                name="Check and send pending reminders",
                replace_existing=True,
            )

            # Add cleanup job (runs daily)
            self.scheduler.add_job(
                self._cleanup_old_jobs,
                trigger="cron",
                hour=3,  # Run at 3 AM
                id="cleanup_old_jobs",
                name="Cleanup old reminder jobs",
                replace_existing=True,
            )

            # Event listeners for logging
            def job_executed(event):
                self.logger.debug(f"Job {event.job_id} executed successfully")

            def job_error(event):
                self.logger.error(f"Job {event.job_id} error: {event.exception}")

            self.scheduler.add_listener(job_executed, EVENT_JOB_EXECUTED)
            self.scheduler.add_listener(job_error, EVENT_JOB_ERROR)

            self._initialized = True
            self.logger.info("Scheduler service initialized successfully")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to initialize scheduler service: {e}", exc_info=True
            )
            return False

    async def start(self) -> bool:
        """Start the scheduler."""
        try:
            if not self._initialized:
                await self.initialize()

            if self.scheduler and not self.scheduler.running:
                self.scheduler.start()
                self._running = True
                self.logger.info("Scheduler started successfully")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}", exc_info=True)
            return False

    async def stop(self) -> None:
        """Stop the scheduler."""
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown()
                self._running = False
                self.logger.info("Scheduler stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}", exc_info=True)

    async def schedule_follow_up(
        self,
        application_id: str,
        user_id: str,
        application_date: datetime,
        job_title: str,
        company: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Schedule a follow-up reminder for a job application.

        Args:
            application_id: ID of the job application
            user_id: ID of the user
            application_date: When the application was submitted
            job_title: Title of the job
            company: Company name
            metadata: Additional metadata

        Returns:
            ID of the scheduled reminder job
        """
        try:
            follow_up_days = self.config.follow_up_days
            if metadata:
                override_days = metadata.get("days_until_followup")
                if isinstance(override_days, int) and override_days >= 0:
                    follow_up_days = override_days

            # Calculate follow-up time
            follow_up_time = application_date + timedelta(days=follow_up_days)

            # Create reminder job
            job_id = (
                f"follow_up_{application_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            reminder_job = ReminderJob(
                id=job_id,
                application_id=application_id,
                user_id=user_id,
                reminder_type="follow_up",
                scheduled_time=follow_up_time,
                metadata={
                    "job_title": job_title,
                    "company": company,
                    "application_date": application_date.isoformat(),
                    **(metadata or {}),
                },
            )

            # Store reminder job
            self.reminder_jobs[job_id] = reminder_job

            now = (
                datetime.now(follow_up_time.tzinfo)
                if follow_up_time.tzinfo
                else datetime.now()
            )

            if follow_up_time <= now:
                await self._send_follow_up_reminder(job_id)
            elif self.scheduler and self.scheduler.running:
                from apscheduler.triggers.date import (  # type: ignore[import-not-found]
                    DateTrigger,
                )

                self.scheduler.add_job(
                    self._send_follow_up_reminder,
                    trigger=DateTrigger(run_date=follow_up_time),
                    id=job_id,
                    name=f"Follow-up reminder for {job_title} at {company}",
                    replace_existing=True,
                    kwargs={"job_id": job_id},
                )

            self.logger.info(
                f"Scheduled follow-up reminder for {job_title} at {company} on {follow_up_time}"
            )
            return job_id

        except Exception as e:
            self.logger.error(
                f"Failed to schedule follow-up reminder: {e}", exc_info=True
            )
            return ""

    async def schedule_status_check(
        self,
        application_id: str,
        user_id: str,
        last_update: datetime,
        job_title: str,
        company: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Schedule a status check reminder for stale applications.

        Args:
            application_id: ID of the job application
            user_id: ID of the user
            last_update: When the application was last updated
            job_title: Title of the job
            company: Company name
            metadata: Additional metadata

        Returns:
            ID of the scheduled reminder job
        """
        try:
            check_days = self.config.stale_application_days
            if metadata:
                override_days = metadata.get("days_until_check")
                if isinstance(override_days, int) and override_days >= 0:
                    check_days = override_days

            # Calculate check time
            check_time = last_update + timedelta(days=check_days)

            # Create reminder job
            job_id = f"check_{application_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            reminder_job = ReminderJob(
                id=job_id,
                application_id=application_id,
                user_id=user_id,
                reminder_type="check_status",
                scheduled_time=check_time,
                metadata={
                    "job_title": job_title,
                    "company": company,
                    "last_update": last_update.isoformat(),
                    **(metadata or {}),
                },
            )

            # Store reminder job
            self.reminder_jobs[job_id] = reminder_job

            # Schedule with APScheduler if scheduler is running
            if self.scheduler and self.scheduler.running:
                from apscheduler.triggers.date import (  # type: ignore[import-not-found]
                    DateTrigger,
                )

                self.scheduler.add_job(
                    self._send_status_check_reminder,
                    trigger=DateTrigger(run_date=check_time),
                    id=job_id,
                    name=f"Status check reminder for {job_title} at {company}",
                    replace_existing=True,
                    kwargs={"job_id": job_id},
                )

            self.logger.info(
                f"Scheduled status check reminder for {job_title} at {company} on {check_time}"
            )
            return job_id

        except Exception as e:
            self.logger.error(
                f"Failed to schedule status check reminder: {e}", exc_info=True
            )
            return ""

    async def schedule_interview_prep(
        self,
        application_id: str,
        user_id: str,
        interview_date: datetime,
        job_title: str,
        company: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Schedule interview preparation reminder.

        Args:
            application_id: ID of the job application
            user_id: ID of the user
            interview_date: Scheduled interview date
            job_title: Title of the job
            company: Company name
            metadata: Additional metadata

        Returns:
            ID of the scheduled reminder job
        """
        try:
            days_before_interview = 2
            if metadata:
                override_days = metadata.get("days_before_interview")
                if isinstance(override_days, int) and override_days >= 0:
                    days_before_interview = override_days

            # Schedule reminder for days before interview
            reminder_time = interview_date - timedelta(days=days_before_interview)

            # Create reminder job
            job_id = (
                f"interview_{application_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            reminder_job = ReminderJob(
                id=job_id,
                application_id=application_id,
                user_id=user_id,
                reminder_type="interview_prep",
                scheduled_time=reminder_time,
                metadata={
                    "job_title": job_title,
                    "company": company,
                    "interview_date": interview_date.isoformat(),
                    **(metadata or {}),
                },
            )

            # Store reminder job
            self.reminder_jobs[job_id] = reminder_job

            # Schedule with APScheduler if scheduler is running
            if self.scheduler and self.scheduler.running:
                from apscheduler.triggers.date import (  # type: ignore[import-not-found]
                    DateTrigger,
                )

                self.scheduler.add_job(
                    self._send_interview_prep_reminder,
                    trigger=DateTrigger(run_date=reminder_time),
                    id=job_id,
                    name=f"Interview prep reminder for {job_title} at {company}",
                    replace_existing=True,
                    kwargs={"job_id": job_id},
                )

            self.logger.info(
                f"Scheduled interview prep reminder for {job_title} at {company} on {reminder_time}"
            )
            return job_id

        except Exception as e:
            self.logger.error(
                f"Failed to schedule interview prep reminder: {e}", exc_info=True
            )
            return ""

    async def cancel_reminder(self, job_id: str) -> bool:
        """Cancel a scheduled reminder.

        Args:
            job_id: ID of the reminder job to cancel

        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            # Remove from scheduler
            if self.scheduler and self.scheduler.running:
                self.scheduler.remove_job(job_id)

            # Remove from storage
            if job_id in self.reminder_jobs:
                del self.reminder_jobs[job_id]
                self.logger.info(f"Cancelled reminder: {job_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to cancel reminder: {e}", exc_info=True)
            return False

    async def get_pending_reminders(self, user_id: str) -> List[ReminderJob]:
        """Get all pending reminders for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of pending reminder jobs
        """
        return [
            job
            for job in self.reminder_jobs.values()
            if job.user_id == user_id and not job.sent
        ]

    async def get_reminder_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific reminder.

        Args:
            job_id: ID of the reminder job

        Returns:
            Dictionary with reminder status or None if not found
        """
        if job_id in self.reminder_jobs:
            job = self.reminder_jobs[job_id]
            return {
                "id": job.id,
                "application_id": job.application_id,
                "type": job.reminder_type,
                "scheduled_time": job.scheduled_time.isoformat(),
                "sent": job.sent,
                "sent_at": job.sent_at.isoformat() if job.sent_at else None,
            }
        return None

    # Internal methods

    async def _check_reminders(self):
        """Check and process pending reminders."""
        try:
            self.logger.debug("Checking for pending reminders...")
            now = datetime.now()

            for job_id, job in list(self.reminder_jobs.items()):
                if not job.sent and job.scheduled_time <= now:
                    # Send reminder based on type
                    if job.reminder_type == "follow_up":
                        await self._send_follow_up_reminder(job_id)
                    elif job.reminder_type == "check_status":
                        await self._send_status_check_reminder(job_id)
                    elif job.reminder_type == "interview_prep":
                        await self._send_interview_prep_reminder(job_id)

        except Exception as e:
            self.logger.error(f"Error checking reminders: {e}", exc_info=True)

    async def _send_follow_up_reminder(self, job_id: str):
        """Send follow-up reminder email."""
        try:
            job = self.reminder_jobs.get(job_id)
            if not job:
                return

            # Import notification service (lazy import to avoid circular dependency)
            from src.services.notification_service import notification_service

            reminder_metadata = job.metadata or {}

            # Send email
            success = await notification_service.send_follow_up_reminder(
                user_id=job.user_id,
                job_title=reminder_metadata.get("job_title", "Unknown"),
                company=reminder_metadata.get("company", "Unknown"),
                application_date=reminder_metadata.get("application_date", ""),
                user_email=reminder_metadata.get("user_email"),
                user_name=reminder_metadata.get("user_name"),
            )

            if success:
                job.sent = True
                job.sent_at = datetime.now()
                self.logger.info(f"Sent follow-up reminder: {job_id}")
            else:
                self.logger.error(f"Failed to send follow-up reminder: {job_id}")

        except Exception as e:
            self.logger.error(f"Error sending follow-up reminder: {e}", exc_info=True)

    async def _send_status_check_reminder(self, job_id: str):
        """Send status check reminder email."""
        try:
            job = self.reminder_jobs.get(job_id)
            if not job:
                return

            # Import notification service
            from src.services.notification_service import notification_service

            reminder_metadata = job.metadata or {}

            # Send email
            success = await notification_service.send_status_check_reminder(
                user_id=job.user_id,
                job_title=reminder_metadata.get("job_title", "Unknown"),
                company=reminder_metadata.get("company", "Unknown"),
                last_update=reminder_metadata.get("last_update", ""),
                user_email=reminder_metadata.get("user_email"),
                user_name=reminder_metadata.get("user_name"),
            )

            if success:
                job.sent = True
                job.sent_at = datetime.now()
                self.logger.info(f"Sent status check reminder: {job_id}")
            else:
                self.logger.error(f"Failed to send status check reminder: {job_id}")

        except Exception as e:
            self.logger.error(
                f"Error sending status check reminder: {e}", exc_info=True
            )

    async def _send_interview_prep_reminder(self, job_id: str):
        """Send interview preparation reminder email."""
        try:
            job = self.reminder_jobs.get(job_id)
            if not job:
                return

            # Import notification service
            from src.services.notification_service import notification_service

            reminder_metadata = job.metadata or {}

            # Send email
            success = await notification_service.send_interview_prep_reminder(
                user_id=job.user_id,
                job_title=reminder_metadata.get("job_title", "Unknown"),
                company=reminder_metadata.get("company", "Unknown"),
                interview_date=reminder_metadata.get("interview_date", ""),
                user_email=reminder_metadata.get("user_email"),
                user_name=reminder_metadata.get("user_name"),
            )

            if success:
                job.sent = True
                job.sent_at = datetime.now()
                self.logger.info(f"Sent interview prep reminder: {job_id}")
            else:
                self.logger.error(f"Failed to send interview prep reminder: {job_id}")

        except Exception as e:
            self.logger.error(
                f"Error sending interview prep reminder: {e}", exc_info=True
            )

    async def _cleanup_old_jobs(self):
        """Clean up old reminder jobs."""
        try:
            from datetime import timedelta

            # Remove jobs older than 30 days
            cutoff = datetime.now() - timedelta(days=30)
            removed_count = 0

            for job_id, job in list(self.reminder_jobs.items()):
                if job.sent and job.sent_at and job.sent_at < cutoff:
                    del self.reminder_jobs[job_id]
                    removed_count += 1

            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old reminder jobs")

        except Exception as e:
            self.logger.error(f"Error cleaning up old jobs: {e}", exc_info=True)

    async def health_check(self) -> Dict[str, Any]:
        """Check scheduler service health."""
        return {
            "status": "healthy" if self._running else "unhealthy",
            "initialized": self._initialized,
            "running": self._running,
            "pending_reminders": len(
                [j for j in self.reminder_jobs.values() if not j.sent]
            ),
            "sent_reminders": len([j for j in self.reminder_jobs.values() if j.sent]),
        }


# Global scheduler instance
scheduler_service = SchedulerService()
