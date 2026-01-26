"""Integration tests for notification system (email + push).

Tests end-to-end notification flows using mocked external providers.
NO real external calls to Mailgun or Web Push services.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.database.config import Base
from src.database.models import DBUser
from src.models.push_subscription import PushMessage, PushSubscriptionCreate
from src.services.push_service import PushService
from src.services.mailgun_client import MailgunProvider
from src.services.email_templates import email_template_renderer
from tests.fixtures.notification_fixtures import (
    sample_email_request_data,
    sample_follow_up_email_data,
    sample_interview_prep_email_data,
    sample_push_subscription_data,
    sample_push_message_data,
    sample_email_with_attachments_data,
)


@pytest.fixture
async def db_session_factory():
    """Create an isolated in-memory DB for integration tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        yield factory
    finally:
        await engine.dispose()


@pytest.fixture
async def test_user(db_session_factory) -> str:
    """Create a test user and return user ID."""
    user_id = str(uuid.uuid4())
    async with db_session_factory() as session:
        async with session.begin():
            session.add(
                DBUser(
                    id=user_id,
                    email=f"integration_{user_id}@example.com",
                    password_hash="test_hash",
                    name="Integration Test User",
                )
            )
    return user_id


@pytest.fixture
def mailgun_provider_mock() -> MailgunProvider:
    """Create a mocked Mailgun provider."""
    provider = MailgunProvider(
        api_key="test-api-key",
        domain="test.example.com",
        from_email="test@example.com",
        from_name="Test Sender",
    )
    # Mock the session to prevent real HTTP calls
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={"message": "Queued. Thank you.", "id": "<test@example.com>"}
    )
    mock_session.post = AsyncMock(return_value=mock_response)
    mock_session.closed = False
    provider._session = mock_session
    return provider


@pytest.fixture
def push_service_instance(db_session_factory) -> PushService:
    """Create a PushService instance for testing."""
    return PushService(
        session_factory=db_session_factory,
        vapid_private_key="test-private-key",
        vapid_subject="mailto:test@example.com",
    )


class TestEmailNotificationIntegration:
    """Integration tests for email notification flow."""

    @pytest.mark.asyncio
    async def test_send_welcome_email_end_to_end(
        self, mailgun_provider_mock: MailgunProvider
    ):
        """Test complete welcome email flow from request to send."""
        # Arrange
        email_data = sample_email_request_data()

        # Render template
        subject, body_html, body_text = await email_template_renderer.render(
            template_name=email_data["template_name"],
            data=email_data["template_data"],
        )

        # Act - Send email
        result = await mailgun_provider_mock.send_email(
            to_email=email_data["to_email"],
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            tags=email_data["tags"],
        )

        # Assert
        assert result is True
        mailgun_provider_mock._session.post.assert_called_once()
        # Verify the email was sent (don't inspect FormData internals)
        assert "Welcome" in subject

    @pytest.mark.asyncio
    async def test_send_follow_up_reminder_email(
        self, mailgun_provider_mock: MailgunProvider
    ):
        """Test follow-up reminder email flow."""
        # Arrange
        email_data = sample_follow_up_email_data()

        # Render template
        subject, body_html, body_text = await email_template_renderer.render(
            template_name=email_data["template_name"],
            data=email_data["template_data"],
        )

        # Act
        result = await mailgun_provider_mock.send_email(
            to_email=email_data["to_email"],
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            tags=email_data["tags"],
        )

        # Assert
        assert result is True
        assert "TechCorp Inc." in body_html
        assert "Senior Software Engineer" in body_html
        assert "follow up" in subject.lower()

    @pytest.mark.asyncio
    async def test_send_interview_prep_reminder_email(
        self, mailgun_provider_mock: MailgunProvider
    ):
        """Test interview prep reminder email flow."""
        # Arrange
        email_data = sample_interview_prep_email_data()

        # Render template
        subject, body_html, body_text = await email_template_renderer.render(
            template_name=email_data["template_name"],
            data=email_data["template_data"],
        )

        # Act
        result = await mailgun_provider_mock.send_email(
            to_email=email_data["to_email"],
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            tags=email_data["tags"],
        )

        # Assert
        assert result is True
        assert "StartupXYZ" in body_html
        assert "Full Stack Developer" in body_html
        assert "interview" in subject.lower()

    @pytest.mark.asyncio
    async def test_send_email_with_attachments(
        self, mailgun_provider_mock: MailgunProvider
    ):
        """Test email with attachments flow."""
        # Arrange
        email_data = sample_email_with_attachments_data()

        # Render template
        subject, body_html, body_text = await email_template_renderer.render(
            template_name=email_data["template_name"],
            data=email_data["template_data"],
        )

        # Act
        result = await mailgun_provider_mock.send_email(
            to_email=email_data["to_email"],
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            attachments=email_data["attachments"],
            tags=email_data["tags"],
        )

        # Assert
        assert result is True
        mailgun_provider_mock._session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_email_template_rendering_all_templates(self):
        """Test that all email templates render successfully."""
        templates_to_test = [
            ("welcome", {"user_name": "Test", "app_url": "https://app.example.com"}),
            (
                "follow_up_reminder",
                {
                    "user_name": "Test",
                    "job_title": "Engineer",
                    "company": "TechCorp",
                    "application_date": "2024-01-15",
                    "application_id": "123",
                    "app_url": "https://app.example.com",
                },
            ),
            (
                "status_check_reminder",
                {
                    "user_name": "Test",
                    "job_title": "Engineer",
                    "company": "TechCorp",
                    "last_update": "2024-01-15",
                    "application_id": "123",
                    "app_url": "https://app.example.com",
                },
            ),
            (
                "interview_prep_reminder",
                {
                    "user_name": "Test",
                    "job_title": "Engineer",
                    "company": "TechCorp",
                    "interview_date": "2024-02-01",
                    "application_id": "123",
                    "app_url": "https://app.example.com",
                },
            ),
            (
                "password_reset",
                {
                    "user_name": "Test",
                    "reset_link": "https://app.example.com/reset",
                    "expiry_hours": 1,
                },
            ),
            (
                "application_confirmation",
                {
                    "user_name": "Test",
                    "job_title": "Engineer",
                    "company": "TechCorp",
                    "application_id": "123",
                    "app_url": "https://app.example.com",
                },
            ),
        ]

        for template_name, template_data in templates_to_test:
            subject, body_html, body_text = await email_template_renderer.render(
                template_name=template_name, data=template_data
            )

            # Assert all templates render with content
            assert subject
            assert body_html
            assert body_text
            assert len(subject) > 0
            assert len(body_html) > 50
            assert len(body_text) > 50


class TestPushNotificationIntegration:
    """Integration tests for push notification flow."""

    @pytest.mark.asyncio
    async def test_subscribe_and_send_push_notification(
        self, push_service_instance: PushService, test_user: str
    ):
        """Test complete push notification flow: subscribe -> send."""
        # Arrange
        subscription_data = PushSubscriptionCreate(**sample_push_subscription_data())
        message_data = PushMessage(**sample_push_message_data())

        # Act - Subscribe
        subscription_id = await push_service_instance.subscribe(
            user_id=test_user, subscription=subscription_data
        )

        # Mock the actual web push send to avoid real HTTP calls
        with patch("src.services.push_service.anyio.to_thread.run_sync") as mock_send:
            mock_send.return_value = None

            # Act - Send push notification
            attempted = await push_service_instance.send_to_user(
                user_id=test_user, message=message_data
            )

        # Assert
        assert subscription_id
        assert attempted == 1
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_unsubscribe_prevents_push_delivery(
        self, push_service_instance: PushService, test_user: str
    ):
        """Test that unsubscribing prevents push notifications."""
        # Arrange
        subscription_data = PushSubscriptionCreate(**sample_push_subscription_data())
        message_data = PushMessage(**sample_push_message_data())

        # Subscribe
        await push_service_instance.subscribe(
            user_id=test_user, subscription=subscription_data
        )

        # Unsubscribe
        removed = await push_service_instance.unsubscribe(
            user_id=test_user, endpoint=subscription_data.endpoint
        )

        # Act - Try to send push notification
        with patch("src.services.push_service.anyio.to_thread.run_sync") as mock_send:
            mock_send.return_value = None
            attempted = await push_service_instance.send_to_user(
                user_id=test_user, message=message_data
            )

        # Assert
        assert removed is True
        assert attempted == 0
        mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_multiple_subscriptions_for_user(
        self, push_service_instance: PushService, test_user: str
    ):
        """Test sending push to user with multiple subscriptions."""
        # Arrange - Create 3 subscriptions
        subscriptions = []
        for i in range(3):
            sub_data = sample_push_subscription_data()
            sub_data["endpoint"] = f"https://fcm.googleapis.com/fcm/send/token-{i}"
            subscription = PushSubscriptionCreate(**sub_data)
            await push_service_instance.subscribe(
                user_id=test_user, subscription=subscription
            )
            subscriptions.append(subscription)

        message_data = PushMessage(**sample_push_message_data())

        # Act - Send to all subscriptions
        with patch("src.services.push_service.anyio.to_thread.run_sync") as mock_send:
            mock_send.return_value = None
            attempted = await push_service_instance.send_to_user(
                user_id=test_user, message=message_data
            )

        # Assert
        assert attempted == 3
        assert mock_send.call_count == 3


class TestEmailAndPushIntegration:
    """Integration tests for combined email + push notification flows."""

    @pytest.mark.asyncio
    async def test_send_email_and_push_for_application_confirmation(
        self,
        mailgun_provider_mock: MailgunProvider,
        push_service_instance: PushService,
        test_user: str,
    ):
        """Test sending both email and push notification for application confirmation."""
        # Arrange
        email_data = sample_email_with_attachments_data()
        subscription_data = PushSubscriptionCreate(**sample_push_subscription_data())
        push_message = PushMessage(
            title="Application Confirmed",
            body=f"Your application to {email_data['template_data']['company']} has been submitted",
            data={"application_id": email_data["template_data"]["application_id"]},
        )

        # Subscribe to push
        await push_service_instance.subscribe(
            user_id=test_user, subscription=subscription_data
        )

        # Act - Send email
        subject, body_html, body_text = await email_template_renderer.render(
            template_name=email_data["template_name"],
            data=email_data["template_data"],
        )

        email_result = await mailgun_provider_mock.send_email(
            to_email=email_data["to_email"],
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            attachments=email_data["attachments"],
            tags=email_data["tags"],
        )

        # Act - Send push
        with patch("src.services.push_service.anyio.to_thread.run_sync") as mock_send:
            mock_send.return_value = None
            push_attempted = await push_service_instance.send_to_user(
                user_id=test_user, message=push_message
            )

        # Assert
        assert email_result is True
        assert push_attempted == 1
        mailgun_provider_mock._session.post.assert_called_once()
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_and_push_for_interview_reminder(
        self,
        mailgun_provider_mock: MailgunProvider,
        push_service_instance: PushService,
        test_user: str,
    ):
        """Test sending both email and push for interview reminder."""
        # Arrange
        email_data = sample_interview_prep_email_data()
        subscription_data = PushSubscriptionCreate(**sample_push_subscription_data())
        push_message = PushMessage(
            title="Interview Reminder",
            body=f"Interview for {email_data['template_data']['job_title']} at {email_data['template_data']['company']}",
            data={
                "application_id": email_data["template_data"]["application_id"],
                "interview_date": email_data["template_data"]["interview_date"],
            },
        )

        # Subscribe to push
        await push_service_instance.subscribe(
            user_id=test_user, subscription=subscription_data
        )

        # Act - Send email
        subject, body_html, body_text = await email_template_renderer.render(
            template_name=email_data["template_name"],
            data=email_data["template_data"],
        )

        email_result = await mailgun_provider_mock.send_email(
            to_email=email_data["to_email"],
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            tags=email_data["tags"],
        )

        # Act - Send push
        with patch("src.services.push_service.anyio.to_thread.run_sync") as mock_send:
            mock_send.return_value = None
            push_attempted = await push_service_instance.send_to_user(
                user_id=test_user, message=push_message
            )

        # Assert
        assert email_result is True
        assert push_attempted == 1
        assert "interview" in subject.lower()

    @pytest.mark.asyncio
    async def test_graceful_degradation_when_push_unavailable(
        self, mailgun_provider_mock: MailgunProvider, test_user: str
    ):
        """Test that email still works when push service is unavailable."""
        # Arrange
        email_data = sample_follow_up_email_data()

        # Create push service without VAPID key (simulates unavailable)
        push_service_no_vapid = PushService(
            vapid_private_key=None,  # No VAPID key
            vapid_subject="mailto:test@example.com",
        )

        # Act - Send email (should succeed)
        subject, body_html, body_text = await email_template_renderer.render(
            template_name=email_data["template_name"],
            data=email_data["template_data"],
        )

        email_result = await mailgun_provider_mock.send_email(
            to_email=email_data["to_email"],
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            tags=email_data["tags"],
        )

        # Act - Try to send push (should gracefully fail)
        push_message = PushMessage(
            title="Test", body="Test message", data={"test": "data"}
        )
        push_attempted = await push_service_no_vapid.send_to_user(
            user_id=test_user, message=push_message
        )

        # Assert
        assert email_result is True  # Email succeeds
        assert push_attempted == 0  # Push gracefully skipped

    @pytest.mark.asyncio
    async def test_notification_flow_with_user_preferences(
        self,
        mailgun_provider_mock: MailgunProvider,
        push_service_instance: PushService,
        test_user: str,
    ):
        """Test notification flow respecting user preferences."""
        # Arrange - User preferences
        user_preferences = {
            "email_enabled": True,
            "push_enabled": True,
            "follow_up_reminders": True,
            "interview_reminders": True,
        }

        email_data = sample_follow_up_email_data()
        subscription_data = PushSubscriptionCreate(**sample_push_subscription_data())

        # Subscribe to push
        await push_service_instance.subscribe(
            user_id=test_user, subscription=subscription_data
        )

        # Act - Send notifications based on preferences
        notifications_sent = {"email": False, "push": False}

        if (
            user_preferences["email_enabled"]
            and user_preferences["follow_up_reminders"]
        ):
            subject, body_html, body_text = await email_template_renderer.render(
                template_name=email_data["template_name"],
                data=email_data["template_data"],
            )
            email_result = await mailgun_provider_mock.send_email(
                to_email=email_data["to_email"],
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                tags=email_data["tags"],
            )
            notifications_sent["email"] = email_result

        if user_preferences["push_enabled"] and user_preferences["follow_up_reminders"]:
            push_message = PushMessage(
                title="Follow-up Reminder",
                body=f"Time to follow up on {email_data['template_data']['company']}",
                data={"application_id": email_data["template_data"]["application_id"]},
            )
            with patch(
                "src.services.push_service.anyio.to_thread.run_sync"
            ) as mock_send:
                mock_send.return_value = None
                push_attempted = await push_service_instance.send_to_user(
                    user_id=test_user, message=push_message
                )
                notifications_sent["push"] = push_attempted > 0

        # Assert
        assert notifications_sent["email"] is True
        assert notifications_sent["push"] is True


class TestNotificationErrorHandling:
    """Integration tests for error handling in notification flows."""

    @pytest.mark.asyncio
    async def test_email_send_failure_handling(self):
        """Test handling of email send failures."""
        # Arrange - Create provider with failing session
        provider = MailgunProvider(
            api_key="test-api-key",
            domain="test.example.com",
        )
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 400  # Bad request
        mock_response.text = AsyncMock(return_value="Bad Request")
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_session.closed = False
        provider._session = mock_session

        # Act
        result = await provider.send_email(
            to_email="test@example.com",
            subject="Test",
            body_html="<p>Test</p>",
            body_text="Test",
        )

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_push_send_with_network_error(
        self, push_service_instance: PushService, test_user: str
    ):
        """Test push send with network error (graceful handling)."""
        # Arrange
        subscription_data = PushSubscriptionCreate(**sample_push_subscription_data())
        await push_service_instance.subscribe(
            user_id=test_user, subscription=subscription_data
        )

        message_data = PushMessage(**sample_push_message_data())

        # Mock web push to simulate network error (not 410, to avoid deletion logic)
        with patch("src.services.push_service.anyio.to_thread.run_sync") as mock_send:
            # Simulate a generic network error
            mock_send.side_effect = Exception("Network error")

            # Act - Send will attempt but fail gracefully
            attempted = await push_service_instance.send_to_user(
                user_id=test_user, message=message_data
            )

        # Assert - Should attempt delivery (even though it fails)
        assert attempted == 1
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_template_rendering_with_missing_data(self):
        """Test template rendering with missing data fields."""
        # Arrange - Minimal data (missing optional fields)
        minimal_data = {
            "user_name": "Test User",
        }

        # Act - Should use defaults for missing fields
        subject, body_html, body_text = await email_template_renderer.render(
            template_name="welcome", data=minimal_data
        )

        # Assert - Should render successfully with defaults
        assert subject
        assert body_html
        assert body_text
        assert "Test User" in body_html
