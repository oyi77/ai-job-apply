"""Notification test fixtures for email and push notifications."""

from datetime import datetime
from typing import Dict, Any
from unittest.mock import AsyncMock
import uuid


def sample_email_request_data() -> Dict[str, Any]:
    """Generate sample email request data for testing."""
    return {
        "to_email": "test@example.com",
        "template_name": "welcome",
        "template_data": {
            "user_name": "Test User",
            "app_url": "https://app.example.com",
        },
        "attachments": [],
        "tags": ["test", "welcome"],
    }


def sample_follow_up_email_data() -> Dict[str, Any]:
    """Generate sample follow-up reminder email data."""
    return {
        "to_email": "user@example.com",
        "template_name": "follow_up_reminder",
        "template_data": {
            "user_name": "John Doe",
            "job_title": "Senior Software Engineer",
            "company": "TechCorp Inc.",
            "application_date": "2024-01-15",
            "application_id": str(uuid.uuid4()),
            "app_url": "https://app.example.com",
        },
        "tags": ["follow_up", "reminder"],
    }


def sample_interview_prep_email_data() -> Dict[str, Any]:
    """Generate sample interview prep reminder email data."""
    return {
        "to_email": "user@example.com",
        "template_name": "interview_prep_reminder",
        "template_data": {
            "user_name": "Jane Smith",
            "job_title": "Full Stack Developer",
            "company": "StartupXYZ",
            "interview_date": "2024-02-01",
            "application_id": str(uuid.uuid4()),
            "app_url": "https://app.example.com",
        },
        "tags": ["interview", "reminder"],
    }


def sample_push_subscription_data() -> Dict[str, Any]:
    """Generate sample push subscription data."""
    return {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test-token-123",
        "keys": {
            "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM=",
            "auth": "tBHItJI5svbpez7KI4CCXg==",
        },
    }


def sample_push_message_data() -> Dict[str, Any]:
    """Generate sample push message data."""
    return {
        "title": "New Job Match!",
        "body": "We found a job that matches your profile",
        "data": {
            "job_id": str(uuid.uuid4()),
            "url": "/jobs/123",
            "action": "view_job",
        },
    }


def sample_notification_settings_data() -> Dict[str, Any]:
    """Generate sample notification settings data."""
    return {
        "email_enabled": True,
        "follow_up_reminders": True,
        "interview_reminders": True,
        "application_status_updates": True,
        "marketing_emails": False,
    }


def mock_mailgun_provider() -> AsyncMock:
    """Create a mock Mailgun provider for testing."""
    mock_provider = AsyncMock()
    mock_provider.send_email = AsyncMock(return_value=True)
    mock_provider.validate_email = AsyncMock(
        return_value={
            "is_valid": True,
            "is_disposable": False,
            "is_role": False,
            "is_free": True,
            "risk": "low",
        }
    )
    mock_provider.test_connection = AsyncMock(return_value=True)
    return mock_provider


def mock_push_service() -> AsyncMock:
    """Create a mock Push service for testing."""
    mock_service = AsyncMock()
    mock_service.subscribe = AsyncMock(return_value=str(uuid.uuid4()))
    mock_service.unsubscribe = AsyncMock(return_value=True)
    mock_service.send_to_user = AsyncMock(return_value=1)  # 1 subscription attempted
    return mock_service


def mock_email_template_renderer() -> AsyncMock:
    """Create a mock email template renderer for testing."""
    mock_renderer = AsyncMock()
    mock_renderer.render = AsyncMock(
        return_value=(
            "Test Subject",
            "<html><body>Test HTML Body</body></html>",
            "Test Plain Text Body",
        )
    )
    return mock_renderer


def sample_user_profile() -> Dict[str, Any]:
    """Generate sample user profile for testing."""
    return {
        "id": str(uuid.uuid4()),
        "email": "testuser@example.com",
        "name": "Test User",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def sample_email_with_attachments_data() -> Dict[str, Any]:
    """Generate sample email request with attachments."""
    return {
        "to_email": "user@example.com",
        "template_name": "application_confirmation",
        "template_data": {
            "user_name": "Test User",
            "job_title": "Software Engineer",
            "company": "TechCorp",
            "application_id": str(uuid.uuid4()),
            "app_url": "https://app.example.com",
        },
        "attachments": [
            {
                "filename": "resume.pdf",
                "content": b"PDF content here",
                "mime_type": "application/pdf",
            },
            {
                "filename": "cover_letter.pdf",
                "content": b"Cover letter content",
                "mime_type": "application/pdf",
            },
        ],
        "tags": ["application", "confirmation"],
    }


def sample_test_email_request_data() -> Dict[str, Any]:
    """Generate sample test email request data."""
    return {
        "to_email": "test@example.com",
        "template_name": "welcome",
    }


def sample_multiple_push_subscriptions(count: int = 3) -> list[Dict[str, Any]]:
    """Generate multiple push subscription samples."""
    subscriptions = []
    for i in range(count):
        sub = sample_push_subscription_data()
        sub["endpoint"] = f"https://fcm.googleapis.com/fcm/send/test-token-{i}"
        subscriptions.append(sub)
    return subscriptions
