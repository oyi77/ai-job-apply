"""Mailgun email provider for sending transactional emails.

This module provides a Mailgun API-based email provider that integrates
with the existing EmailProvider interface.
"""

import abc
import asyncio
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import aiohttp
from src.utils.logger import get_logger
from src.config import config


@dataclass
class MailgunConfig:
    """Mailgun configuration."""

    api_key: str
    domain: str
    region: str = "us"  # 'us' or 'eu'
    from_email: str = "noreply@example.com"
    from_name: str = "AI Job Application Assistant"
    timeout: int = 30  # seconds


class MailgunProvider:
    """Mailgun email provider using the HTTP API.

    This provider sends emails via Mailgun's API instead of SMTP,
    which is more reliable for transactional emails and provides
    better deliverability and analytics.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        domain: Optional[str] = None,
        region: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        timeout: int = 30,
    ):
        """Initialize Mailgun provider.

        Args:
            api_key: Mailgun API key (defaults to config.MAILGUN_API_KEY)
            domain: Mailgun domain (defaults to config.MAILGUN_DOMAIN)
            region: Mailgun region ('us' or 'eu')
            from_email: Sender email address
            from_name: Sender name
            timeout: Request timeout in seconds
        """
        self.logger = get_logger(__name__)

        # Load from config if not provided
        self.api_key = api_key or getattr(config, "mailgun_api_key", None)
        self.domain = domain or getattr(config, "mailgun_domain", None)
        self.region = region or getattr(config, "mailgun_region", "us")
        self.from_email = from_email or getattr(
            config, "mailgun_from_email", "noreply@example.com"
        )
        self.from_name = from_name or getattr(
            config, "mailgun_from_name", "AI Job Application Assistant"
        )
        self.timeout = timeout

        # Validate configuration
        if not self.api_key:
            self.logger.warning("Mailgun API key not configured")
        if not self.domain:
            self.logger.warning("Mailgun domain not configured")

        # Base URL for API requests
        self.base_url = (
            f"https://api.mailgun.net/v3/{self.domain}" if self.domain else ""
        )

        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def _close_session(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        custom_data: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Send an email via Mailgun API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body
            attachments: Optional list of attachments
            tags: Optional list of tags for tracking
            custom_data: Optional custom data for tracking

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.api_key or not self.domain:
            self.logger.error("Mailgun not configured - missing API key or domain")
            return False

        try:
            session = await self._get_session()

            # Build multipart form data
            data = aiohttp.FormData()
            data.add_field("from", f"{self.from_name} <{self.from_email}>")
            data.add_field("to", to_email)
            data.add_field("subject", subject)
            data.add_field("text", body_text)
            data.add_field("html", body_html)

            # Add tags if provided
            if tags:
                for tag in tags:
                    data.add_field("o:tag", tag)

            # Add custom data if provided
            if custom_data:
                for key, value in custom_data.items():
                    data.add_field(f"v:{key}", value)

            # Add attachments if provided
            if attachments:
                for idx, attachment in enumerate(attachments):
                    filename = attachment.get("filename", f"attachment_{idx}")
                    content = attachment.get("content", b"")
                    mime_type = attachment.get("mime_type", "application/octet-stream")

                    data.add_field(
                        f"attachment{idx + 1}"
                        if len(attachments) > 1
                        else "attachment",
                        content,
                        filename=filename,
                        content_type=mime_type,
                    )

            # Send request
            response = await session.post(
                f"{self.base_url}/messages",
                auth=aiohttp.BasicAuth("api", self.api_key),
                data=data,
            )

            if response.status == 200:
                result = await response.json()
                self.logger.info(
                    f"Sent email to {to_email}: {result.get('message', 'OK')}"
                )
                return True
            else:
                error_text = await response.text()
                self.logger.error(
                    f"Failed to send email to {to_email}: "
                    f"HTTP {response.status} - {error_text}"
                )
                return False

        except asyncio.TimeoutError:
            self.logger.error(f"Mailgun request timed out for {to_email}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {e}", exc_info=True)
            return False

    async def send_template_email(
        self,
        to_email: str,
        template_name: str,
        template_vars: Dict[str, str],
        subject: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Send a templated email via Mailgun.

        Note: This requires Mailgun Templates to be configured in your account.

        Args:
            to_email: Recipient email address
            template_name: Name of the Mailgun template
            template_vars: Variables to substitute in template
            subject: Email subject (optional, can be set in template)
            tags: Optional list of tags for tracking

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.api_key or not self.domain:
            self.logger.error("Mailgun not configured")
            return False

        try:
            session = await self._get_session()

            data = aiohttp.FormData()
            data.add_field("from", f"{self.from_name} <{self.from_email}>")
            data.add_field("to", to_email)
            data.add_field("template", template_name)

            # Add template variables
            for key, value in template_vars.items():
                data.add_field(f"v:{key}", value)

            if subject:
                data.add_field("subject", subject)

            if tags:
                for tag in tags:
                    data.add_field("o:tag", tag)

            response = await session.post(
                f"{self.base_url}/messages",
                auth=aiohttp.BasicAuth("api", self.api_key),
                data=data,
            )

            if response.status == 200:
                result = await response.json()
                self.logger.info(
                    f"Sent template email to {to_email}: {result.get('message', 'OK')}"
                )
                return True
            else:
                error_text = await response.text()
                self.logger.error(
                    f"Failed to send template email to {to_email}: "
                    f"HTTP {response.status} - {error_text}"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Failed to send template email to {to_email}: {e}", exc_info=True
            )
            return False

    async def validate_email(self, email: str) -> Dict[str, Any]:
        """Validate an email address using Mailgun's validation API.

        Args:
            email: Email address to validate

        Returns:
            Dict with validation results:
            - is_valid: bool
            - is_disposable: bool
            - is_role: bool
            - is_free: bool
            - risk: str ('low', 'medium', 'high')
        """
        if not self.api_key:
            self.logger.warning("Mailgun API key not configured for validation")
            return {"is_valid": True, "risk": "unknown"}

        try:
            session = await self._get_session()

            response = await session.get(
                f"https://api.mailgun.net/v4/address/validate",
                auth=aiohttp.BasicAuth("api", self.api_key),
                params={"address": email},
            )

            if response.status == 200:
                result = await response.json()
                return {
                    "is_valid": result.get("is_valid", False),
                    "is_disposable": result.get("is_disposable", False),
                    "is_role": result.get("is_role", False),
                    "is_free": result.get("is_free", False),
                    "risk": result.get("risk", "unknown"),
                    "reason": result.get("reason", None),
                }
            else:
                self.logger.warning(f"Email validation failed: HTTP {response.status}")
                return {"is_valid": True, "risk": "unknown"}

        except Exception as e:
            self.logger.error(f"Email validation error: {e}")
            return {"is_valid": True, "risk": "unknown"}

    async def get_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get email statistics from Mailgun.

        Args:
            start_date: Start date (ISO format, e.g., '2024-01-01')
            end_date: End date (ISO format)

        Returns:
            Dict with statistics
        """
        if not self.api_key or not self.domain:
            return {}

        try:
            session = await self._get_session()

            params = {}
            if start_date:
                params["start"] = start_date
            if end_date:
                params["end"] = end_date

            response = await session.get(
                f"{self.base_url}/stats",
                auth=aiohttp.BasicAuth("api", self.api_key),
                params=params,
            )

            if response.status == 200:
                result = await response.json()
                return result.get("stats", [])
            else:
                return {}

        except Exception as e:
            self.logger.error(f"Failed to get Mailgun stats: {e}")
            return {}

    async def test_connection(self) -> bool:
        """Test Mailgun connection.

        Returns:
            True if connection successful, False otherwise
        """
        if not self.api_key or not self.domain:
            return False

        try:
            session = await self._get_session()

            response = await session.get(
                f"{self.base_url}/domains",
                auth=aiohttp.BasicAuth("api", self.api_key),
            )

            if response.status == 200:
                self.logger.info("Mailgun connection test successful")
                return True
            else:
                self.logger.warning(
                    f"Mailgun connection test failed: HTTP {response.status}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Mailgun connection test error: {e}")
            return False

    async def close(self):
        """Clean up resources."""
        await self._close_session()


# Factory function for creating Mailgun provider
def create_mailgun_provider() -> Optional[MailgunProvider]:
    """Create a Mailgun provider from configuration.

    Returns:
        MailgunProvider instance if configured, None otherwise
    """
    api_key = getattr(config, "mailgun_api_key", None)
    domain = getattr(config, "mailgun_domain", None)

    if api_key and domain:
        return MailgunProvider()

    return None
