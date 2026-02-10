"""Unit tests for EmailService."""

from unittest.mock import AsyncMock

import pytest

from src.services.email_service import EmailService, EmailProvider


@pytest.mark.asyncio
async def test_email_service_send_email_delegates() -> None:
    """EmailService should delegate send_email to provider."""
    provider = AsyncMock(spec=EmailProvider)
    provider.send_email = AsyncMock(return_value=True)
    service = EmailService(provider=provider)

    result = await service.send_email(
        to_email="user@example.com",
        subject="Subject",
        body_html="<p>Hi</p>",
        body_text="Hi",
    )

    assert result is True
    provider.send_email.assert_called_once_with(
        to_email="user@example.com",
        subject="Subject",
        body_html="<p>Hi</p>",
        body_text="Hi",
        attachments=None,
    )
