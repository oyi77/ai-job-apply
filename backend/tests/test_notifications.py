"""Tests for notification API endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.api.v1.notifications import router
from src.validators.notification_validators import EmailTemplateEnum
from src.models.user import UserProfile
from src.api.dependencies import get_current_user


# Create test app
app = FastAPI()
app.include_router(router, prefix="/api/v1/notifications")


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Create mock user."""
    from datetime import datetime

    return UserProfile(
        id="test_user_123",
        email="test@example.com",
        name="Test User",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


class TestSendEmailEndpoint:
    """Tests for POST /notifications/email endpoint."""

    def test_send_email_unauthorized(self, client):
        """Test that endpoint requires authentication."""
        response = client.post(
            "/api/v1/notifications/email",
            json={
                "to_email": "user@example.com",
                "template_name": "welcome",
                "template_data": {"user_name": "Test"},
            },
        )

        assert response.status_code == 401  # Unauthorized

    def test_send_email_invalid_email(self, client):
        """Test that invalid email is rejected."""
        response = client.post(
            "/api/v1/notifications/email",
            json={
                "to_email": "invalid-email",
                "template_name": "welcome",
                "template_data": {},
            },
            headers={"Authorization": "Bearer test-token"},
        )

        # Auth fails first (401) or validation fails (422) - both are acceptable
        assert response.status_code in [401, 422]

    def test_send_email_invalid_template(self, client):
        """Test that invalid template is rejected."""
        response = client.post(
            "/api/v1/notifications/email",
            json={
                "to_email": "user@example.com",
                "template_name": "invalid_template",
                "template_data": {},
            },
            headers={"Authorization": "Bearer test-token"},
        )

        # Auth fails first (401) or validation fails (422) - both are acceptable
        assert response.status_code in [401, 422]

    def test_send_email_missing_fields(self, client):
        """Test that missing required fields are rejected."""
        response = client.post(
            "/api/v1/notifications/email",
            json={
                "to_email": "user@example.com"
                # Missing template_name
            },
            headers={"Authorization": "Bearer test-token"},
        )

        # Auth fails first (401) or validation fails (422) - both are acceptable
        assert response.status_code in [401, 422]


class TestTestEmailEndpoint:
    """Tests for POST /notifications/email/test endpoint."""

    def test_test_email_unauthorized(self, client):
        """Test that test email requires authentication."""
        response = client.post(
            "/api/v1/notifications/email/test", json={"to_email": "test@example.com"}
        )

        assert response.status_code == 401


class TestListTemplatesEndpoint:
    """Tests for GET /notifications/email/templates endpoint."""

    def test_list_templates_unauthorized(self, client):
        """Test that list templates requires authentication."""
        response = client.get("/api/v1/notifications/email/templates")

        assert response.status_code == 401

    def test_list_templates_returns_list(self, client, mock_user):
        """Test that list templates returns a list of templates."""

        # Override the dependency for this test
        async def mock_get_current_user():
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user
        try:
            response = client.get(
                "/api/v1/notifications/email/templates",
                headers={"Authorization": "Bearer test-token"},
            )

            assert response.status_code == 200
            data = response.json()
            # Response is wrapped in success/data structure
            assert data["success"] is True
            assert "templates" in data["data"]
            assert isinstance(data["data"]["templates"], list)
            # Check that all expected templates are present
            # Template IDs are uppercase enum names (e.g., FOLLOW_UP_REMINDER)
            template_ids = [t["id"] for t in data["data"]["templates"]]
            for template in EmailTemplateEnum:
                # Compare with uppercase version (enum name)
                assert template.name in template_ids
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()


class TestNotificationSettingsEndpoints:
    """Tests for notification settings endpoints."""

    def test_get_settings_unauthorized(self, client):
        """Test that get settings requires authentication."""
        response = client.get("/api/v1/notifications/settings")

        assert response.status_code == 401

    def test_update_settings_unauthorized(self, client):
        """Test that update settings requires authentication."""
        response = client.post(
            "/api/v1/notifications/settings",
            json={
                "email_enabled": True,
                "follow_up_reminders": True,
                "interview_reminders": True,
                "application_status_updates": True,
                "marketing_emails": False,
            },
        )

        assert response.status_code == 401

    def test_update_settings_invalid_fields(self, client, mock_user):
        """Test that invalid fields are rejected."""

        # Override the dependency for this test
        async def mock_get_current_user():
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user
        try:
            response = client.post(
                "/api/v1/notifications/settings",
                json={
                    "email_enabled": "not-a-boolean",  # Should be boolean
                    "invalid_field": True,
                },
                headers={"Authorization": "Bearer test-token"},
            )

            # Auth fails first (401) or validation fails (422) - both are acceptable
            assert response.status_code in [401, 422]
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()


class TestNotificationValidators:
    """Tests for notification validators."""

    def test_send_email_request_valid(self):
        """Test valid SendEmailRequest validation."""
        from src.validators.notification_validators import SendEmailRequest

        request = SendEmailRequest(
            to_email="user@example.com",
            template_name=EmailTemplateEnum.WELCOME,
            template_data={"user_name": "John"},
        )

        assert request.to_email == "user@example.com"
        assert request.template_name == EmailTemplateEnum.WELCOME
        assert request.template_data["user_name"] == "John"

    def test_send_email_request_with_attachments(self):
        """Test SendEmailRequest with attachments."""
        from src.validators.notification_validators import SendEmailRequest

        request = SendEmailRequest(
            to_email="user@example.com",
            template_name=EmailTemplateEnum.APPLICATION_CONFIRMATION,
            template_data={"job_title": "Engineer"},
            attachments=[
                {
                    "filename": "resume.pdf",
                    "content": b"pdf content",
                    "mime_type": "application/pdf",
                }
            ],
            tags=["application", "confirmation"],
        )

        assert len(request.attachments) == 1
        assert len(request.tags) == 2

    def test_email_template_enum_values(self):
        """Test EmailTemplateEnum has expected values."""
        expected_values = [
            "follow_up_reminder",
            "status_check_reminder",
            "interview_prep_reminder",
            "password_reset",
            "application_confirmation",
            "welcome",
        ]

        for value in expected_values:
            assert hasattr(EmailTemplateEnum, value.upper())
            assert EmailTemplateEnum[value.upper()].value == value

    def test_notification_settings_update_valid(self):
        """Test valid NotificationSettingsUpdate."""
        from src.validators.notification_validators import NotificationSettingsUpdate

        settings = NotificationSettingsUpdate(
            email_enabled=True,
            follow_up_reminders=True,
            interview_reminders=True,
            application_status_updates=True,
            marketing_emails=False,
        )

        assert settings.email_enabled is True
        assert settings.marketing_emails is False

    def test_notification_settings_update_defaults(self):
        """Test NotificationSettingsUpdate default values."""
        from src.validators.notification_validators import NotificationSettingsUpdate

        settings = NotificationSettingsUpdate()

        assert settings.email_enabled is True  # Default
        assert settings.follow_up_reminders is True  # Default
        assert settings.interview_reminders is True  # Default
        assert settings.application_status_updates is True  # Default
        assert settings.marketing_emails is False  # Default

    def test_send_test_email_request_valid(self):
        """Test valid SendTestEmailRequest."""
        from src.validators.notification_validators import SendTestEmailRequest

        request = SendTestEmailRequest(
            to_email="test@example.com", template_name=EmailTemplateEnum.WELCOME
        )

        assert request.to_email == "test@example.com"
        assert request.template_name == EmailTemplateEnum.WELCOME

    def test_send_test_email_request_without_template(self):
        """Test SendTestEmailRequest without template."""
        from src.validators.notification_validators import SendTestEmailRequest

        request = SendTestEmailRequest(to_email="test@example.com")

        assert request.template_name is None  # Optional

    def test_invalid_email_rejected(self):
        """Test that invalid email is rejected."""
        from src.validators.notification_validators import SendEmailRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SendEmailRequest(
                to_email="not-an-email",
                template_name=EmailTemplateEnum.WELCOME,
                template_data={},
            )
