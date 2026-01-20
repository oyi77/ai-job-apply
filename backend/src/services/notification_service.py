"""Notification service for sending emails and other notifications."""

import asyncio
from typing import Optional, Dict, Any, List

from src.utils.logger import get_logger
from src.config import config
from src.services.email_service import EmailService
from src.services.push_service import PushService
from src.models.push_subscription import PushMessage


class NotificationService:
    """Service for sending various types of notifications."""

    def __init__(
        self,
        email_service: Optional[EmailService] = None,
        push_service: Optional[PushService] = None,
    ):
        """Initialize notification service.

        Args:
            email_service: Email service instance (injected via ServiceRegistry)
        """
        self.logger = get_logger(__name__)
        self.email_service = email_service or EmailService()
        self.push_service = push_service
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the notification service."""
        try:
            self.logger.info("Initializing notification service...")
            # Email service is already initialized in __init__
            self._initialized = True
            self.logger.info("Notification service initialized successfully")
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to initialize notification service: {e}", exc_info=True
            )
            return False

    async def send_follow_up_reminder(
        self,
        user_id: str,
        job_title: str,
        company: str,
        application_date: str,
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> bool:
        """Send follow-up reminder email.

        Args:
            user_id: ID of the user
            job_title: Title of the job
            company: Company name
            application_date: When the application was submitted
            user_email: User's email address (optional, will fetch if not provided)
            user_name: User's name (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Get user email if not provided
            if not user_email:
                user_email = await self._get_user_email(user_id)
                if not user_email:
                    self.logger.error(f"Could not get email for user {user_id}")
                    return False

            # Get user name if not provided
            if not user_name:
                user_name = await self._get_user_name(user_id)

            # Render email template
            from src.services.email_templates import email_template_renderer

            template_data = {
                "user_id": user_id,
                "user_name": user_name or "there",
                "job_title": job_title,
                "company": company,
                "application_date": application_date,
                "app_url": config.frontend_url,
            }

            subject, body_html, body_text = await email_template_renderer.render(
                "follow_up_reminder", template_data
            )

            # Send email
            success = await self.email_service.send_email(
                to_email=user_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
            )

            if success:
                self.logger.info(
                    f"Sent follow-up reminder to {user_email} for {job_title} at {company}"
                )
            else:
                self.logger.error(f"Failed to send follow-up reminder to {user_email}")

            return success

        except Exception as e:
            self.logger.error(f"Error sending follow-up reminder: {e}", exc_info=True)
            return False

    async def send_status_check_reminder(
        self,
        user_id: str,
        job_title: str,
        company: str,
        last_update: str,
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> bool:
        """Send status check reminder email.

        Args:
            user_id: ID of the user
            job_title: Title of the job
            company: Company name
            last_update: When the application was last updated
            user_email: User's email address (optional)
            user_name: User's name (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Get user email if not provided
            if not user_email:
                user_email = await self._get_user_email(user_id)
                if not user_email:
                    return False

            # Get user name if not provided
            if not user_name:
                user_name = await self._get_user_name(user_id)

            # Render email template
            from src.services.email_templates import email_template_renderer

            template_data = {
                "user_id": user_id,
                "user_name": user_name or "there",
                "job_title": job_title,
                "company": company,
                "last_update": last_update,
                "app_url": config.frontend_url,
            }

            subject, body_html, body_text = await email_template_renderer.render(
                "status_check_reminder", template_data
            )

            # Send email
            success = await self.email_service.send_email(
                to_email=user_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
            )

            if success:
                self.logger.info(
                    f"Sent status check reminder to {user_email} for {job_title} at {company}"
                )

            return success

        except Exception as e:
            self.logger.error(
                f"Error sending status check reminder: {e}", exc_info=True
            )
            return False

    async def send_interview_prep_reminder(
        self,
        user_id: str,
        job_title: str,
        company: str,
        interview_date: str,
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> bool:
        """Send interview preparation reminder email.

        Args:
            user_id: ID of the user
            job_title: Title of the job
            company: Company name
            interview_date: Scheduled interview date
            user_email: User's email address (optional)
            user_name: User's name (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Get user email if not provided
            if not user_email:
                user_email = await self._get_user_email(user_id)
                if not user_email:
                    return False

            # Get user name if not provided
            if not user_name:
                user_name = await self._get_user_name(user_id)

            # Render email template
            from src.services.email_templates import email_template_renderer

            template_data = {
                "user_id": user_id,
                "user_name": user_name or "there",
                "job_title": job_title,
                "company": company,
                "interview_date": interview_date,
                "app_url": config.frontend_url,
            }

            subject, body_html, body_text = await email_template_renderer.render(
                "interview_prep_reminder", template_data
            )

            # Send email
            success = await self.email_service.send_email(
                to_email=user_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
            )

            if success:
                self.logger.info(
                    f"Sent interview prep reminder to {user_email} for {job_title} at {company}"
                )

            return success

        except Exception as e:
            self.logger.error(
                f"Error sending interview prep reminder: {e}", exc_info=True
            )
            return False

    async def send_application_confirmation(
        self,
        user_id: str,
        job_title: str,
        company: str,
        application_id: str,
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> bool:
        """Send application confirmation email.

        Args:
            user_id: ID of the user
            job_title: Title of the job
            company: Company name
            application_id: ID of the application
            user_email: User's email address (optional)
            user_name: User's name (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Get user email if not provided
            if not user_email:
                user_email = await self._get_user_email(user_id)
                if not user_email:
                    return False

            # Get user name if not provided
            if not user_name:
                user_name = await self._get_user_name(user_id)

            # Render email template
            from src.services.email_templates import email_template_renderer

            template_data = {
                "user_id": user_id,
                "user_name": user_name or "there",
                "job_title": job_title,
                "company": company,
                "application_id": application_id,
                "app_url": config.frontend_url,
            }

            subject, body_html, body_text = await email_template_renderer.render(
                "application_confirmation", template_data
            )

            # Send email
            success = await self.email_service.send_email(
                to_email=user_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
            )

            if success:
                self.logger.info(
                    f"Sent application confirmation to {user_email} for {job_title} at {company}"
                )

            return success

        except Exception as e:
            self.logger.error(
                f"Error sending application confirmation: {e}", exc_info=True
            )
            return False

    async def send_bulk_reminders(
        self, reminders: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Send multiple reminder emails in batch.

        Args:
            reminders: List of reminder data dictionaries

        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failure_count = 0

        for reminder in reminders:
            reminder_type = reminder.get("type", "follow_up")

            if reminder_type == "follow_up":
                success = await self.send_follow_up_reminder(**reminder)
            elif reminder_type == "status_check":
                success = await self.send_status_check_reminder(**reminder)
            elif reminder_type == "interview_prep":
                success = await self.send_interview_prep_reminder(**reminder)
            else:
                self.logger.warning(f"Unknown reminder type: {reminder_type}")
                failure_count += 1
                continue

            if success:
                success_count += 1
            else:
                failure_count += 1

            # Add delay between emails to avoid rate limiting
            await asyncio.sleep(1)

        return {
            "total": len(reminders),
            "success": success_count,
            "failed": failure_count,
        }

    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Get user email from database.

        Args:
            user_id: ID of the user

        Returns:
            User's email or None if not found
        """
        try:
            # Try to get user from database
            from src.database.user_repository import user_repository

            user = await user_repository.get_by_id(user_id)
            if user:
                return user.email

            return None

        except Exception as e:
            self.logger.error(f"Error getting user email: {e}", exc_info=True)
            return None

    async def _get_user_name(self, user_id: str) -> Optional[str]:
        """Get user name from database.

        Args:
            user_id: ID of the user

        Returns:
            User's name or None if not found
        """
        try:
            from src.database.user_repository import user_repository

            user = await user_repository.get_by_id(user_id)
            if user:
                return getattr(user, "name", None) or getattr(user, "username", None)

            return None

        except Exception as e:
            self.logger.error(f"Error getting user name: {e}", exc_info=True)
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Check notification service health."""
        return {
            "status": "healthy",
            "email_service_available": True,
            "push_service_available": self.push_service is not None,
            "initialized": self._initialized,
        }

    async def send_push_notification(
        self,
        *,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Send a Web Push notification.

        Returns:
            Number of attempted deliveries (0 means user unsubscribed / no subs).
        """

        if self.push_service is None:
            self.logger.warning("Push service not configured")
            return 0

        return await self.push_service.send_to_user(
            user_id=user_id,
            message=PushMessage(title=title, body=body, data=data),
        )


# Global notification service instance
notification_service = NotificationService()
