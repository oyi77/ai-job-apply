"""Tests for Mailgun email provider."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.mailgun_client import MailgunProvider, create_mailgun_provider
from src.config import config


@pytest.fixture
def mailgun_provider() -> MailgunProvider:
    """Create a MailgunProvider instance for testing."""
    return MailgunProvider(
        api_key="test-api-key",
        domain="test.example.com",
        from_email="test@example.com",
        from_name="Test Sender",
    )


class TestMailgunProvider:
    """Tests for MailgunProvider class."""

    def test_initialization(self, mailgun_provider: MailgunProvider):
        """Test provider initialization."""
        assert mailgun_provider.api_key == "test-api-key"
        assert mailgun_provider.domain == "test.example.com"
        assert mailgun_provider.from_email == "test@example.com"
        assert mailgun_provider.from_name == "Test Sender"
        assert (
            mailgun_provider.base_url == "https://api.mailgun.net/v3/test.example.com"
        )

    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        provider = MailgunProvider(
            api_key="key",
            domain="domain.com",
        )
        assert provider.from_email == "noreply@example.com"
        assert provider.from_name == "AI Job Application Assistant"
        assert provider.timeout == 30

    @pytest.mark.asyncio
    async def test_send_email_success(self, mailgun_provider: MailgunProvider):
        """Test successful email sending."""
        # Mock session and response
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "message": "Queued. Thank you.",
                "id": "<12345.67890@example.com>",
            }
        )
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_session.closed = False

        mailgun_provider._session = mock_session

        result = await mailgun_provider.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body_html="<p>HTML body</p>",
            body_text="Plain text body",
        )

        assert result is True
        mock_session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_failure(self, mailgun_provider: MailgunProvider):
        """Test email sending failure."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad Request")
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_session.closed = False

        mailgun_provider._session = mock_session

        result = await mailgun_provider.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body_html="<p>HTML body</p>",
            body_text="Plain text body",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_send_email_with_attachments(self, mailgun_provider: MailgunProvider):
        """Test sending email with attachments."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"message": "Queued. Thank you."})
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_session.closed = False

        mailgun_provider._session = mock_session

        attachments = [
            {
                "filename": "document.pdf",
                "content": b"PDF content",
                "mime_type": "application/pdf",
            }
        ]

        result = await mailgun_provider.send_email(
            to_email="recipient@example.com",
            subject="Test with Attachment",
            body_html="<p>See attachment</p>",
            body_text="See attachment",
            attachments=attachments,
        )

        assert result is True
        call_args = mock_session.post.call_args
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_send_email_with_tags(self, mailgun_provider: MailgunProvider):
        """Test sending email with tags."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"message": "Queued. Thank you."})
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_session.closed = False

        mailgun_provider._session = mock_session

        result = await mailgun_provider.send_email(
            to_email="recipient@example.com",
            subject="Tagged Email",
            body_html="<p>Tagged</p>",
            body_text="Tagged",
            tags=["welcome", "onboarding"],
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_email_not_configured(self):
        """Test sending email when not configured."""
        provider = MailgunProvider(api_key=None, domain=None)

        result = await provider.send_email(
            to_email="recipient@example.com",
            subject="Test",
            body_html="<p>Test</p>",
            body_text="Test",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_validate_email_success(self, mailgun_provider: MailgunProvider):
        """Test successful email validation."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "is_valid": True,
                "is_disposable": False,
                "is_role": False,
                "is_free": True,
                "risk": "low",
            }
        )
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.closed = False

        mailgun_provider._session = mock_session

        result = await mailgun_provider.validate_email("user@gmail.com")

        assert result["is_valid"] is True
        assert result["risk"] == "low"

    @pytest.mark.asyncio
    async def test_validate_email_not_configured(self):
        """Test email validation when not configured."""
        provider = MailgunProvider(api_key=None, domain=None)

        result = await provider.validate_email("user@example.com")

        assert result["is_valid"] is True  # Fallback to assuming valid
        assert result["risk"] == "unknown"

    @pytest.mark.asyncio
    async def test_test_connection_success(self, mailgun_provider: MailgunProvider):
        """Test successful connection test."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"items": []})
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.closed = False

        mailgun_provider._session = mock_session

        result = await mailgun_provider.test_connection()

        assert result is True

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, mailgun_provider: MailgunProvider):
        """Test failed connection test."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.closed = False

        mailgun_provider._session = mock_session

        result = await mailgun_provider.test_connection()

        assert result is False

    @pytest.mark.asyncio
    async def test_close_session(self, mailgun_provider: MailgunProvider):
        """Test session cleanup."""
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.close = AsyncMock()
        mailgun_provider._session = mock_session

        await mailgun_provider._close_session()

        mock_session.close.assert_called_once()
        assert mailgun_provider._session is None

    @pytest.mark.asyncio
    async def test_close_already_closed_session(
        self, mailgun_provider: MailgunProvider
    ):
        """Test closing already closed session."""
        mailgun_provider._session = None

        # Should not raise
        await mailgun_provider._close_session()

        assert mailgun_provider._session is None


class TestCreateMailgunProvider:
    """Tests for create_mailgun_provider factory function."""

    def test_create_with_config(self):
        """Test creating provider when configured."""
        with patch.object(config, "mailgun_api_key", "test-key"):
            with patch.object(config, "mailgun_domain", "test.com"):
                provider = create_mailgun_provider()

                assert provider is not None
                assert provider.api_key == "test-key"
                assert provider.domain == "test.com"

    def test_create_without_config(self):
        """Test creating provider when not configured."""
        with patch.object(config, "mailgun_api_key", None):
            with patch.object(config, "mailgun_domain", None):
                provider = create_mailgun_provider()

                assert provider is None


class TestMailgunConfigFields:
    """Tests for Mailgun configuration fields in Settings."""

    def test_mailgun_config_fields_exist(self):
        """Test that Mailgun config fields exist in Settings."""
        # These fields should be accessible on config
        assert hasattr(config, "mailgun_api_key")
        assert hasattr(config, "mailgun_domain")
        assert hasattr(config, "mailgun_region")
        assert hasattr(config, "mailgun_from_email")
        assert hasattr(config, "mailgun_from_name")
