"""Email service for sending notifications."""

import abc
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Optional, Dict, Any
from src.utils.logger import get_logger
from src.config import config


class EmailProvider(abc.ABC):
    """Abstract base class for email providers."""

    @abc.abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Send an email."""
        pass


class ConsoleEmailProvider(EmailProvider):
    """Email provider that logs emails to console (for development)."""

    def __init__(self):
        self.logger = get_logger(__name__)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Log email details to console/logger."""
        self.logger.info("--- EMAIL SIMULATION ---")
        self.logger.info(f"To: {to_email}")
        self.logger.info(f"Subject: {subject}")
        self.logger.debug(f"Body (Text): {body_text}")
        if attachments:
            self.logger.info(
                f"Attachments: {[a.get('filename', 'unnamed') for a in attachments]}"
            )
        self.logger.info("--- END EMAIL ---")
        return True


class SMTPEmailProvider(EmailProvider):
    """Email provider that sends emails via SMTP server."""

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        use_tls: bool = True,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
        """Initialize SMTP email provider.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            use_tls: Whether to use TLS/SSL
            from_email: Sender email address
            from_name: Sender name
        """
        self.logger = get_logger(__name__)
        self.smtp_host = smtp_host or getattr(config, "SMTP_HOST", "localhost")
        self.smtp_port = smtp_port or getattr(config, "SMTP_PORT", 587)
        self.smtp_user = smtp_user or getattr(config, "SMTP_USER", "")
        self.smtp_password = smtp_password or getattr(config, "SMTP_PASSWORD", "")
        self.use_tls = (
            use_tls if use_tls is not None else getattr(config, "USE_TLS", True)
        )
        self.from_email = from_email or getattr(
            config, "FROM_EMAIL", "noreply@example.com"
        )
        self.from_name = from_name or getattr(
            config, "FROM_NAME", "Job Application Assistant"
        )

        self._connection: Optional[smtplib.SMTP] = None
        self._connected = False

    async def _get_connection(self) -> smtplib.SMTP:
        """Get or create SMTP connection."""
        if self._connected and self._connection:
            return self._connection

        try:
            # Create connection
            if self.smtp_port == 465:
                # SSL connection
                self._connection = smtplib.SMTP_SSL(
                    self.smtp_host, self.smtp_port, timeout=30
                )
            else:
                # TLS connection
                self._connection = smtplib.SMTP(
                    self.smtp_host, self.smtp_port, timeout=30
                )
                if self.use_tls:
                    self._connection.starttls()

            # Login if credentials provided
            if self.smtp_user and self.smtp_password:
                self._connection.login(self.smtp_user, self.smtp_password)

            self._connected = True
            self.logger.info(
                f"Connected to SMTP server {self.smtp_host}:{self.smtp_port}"
            )
            return self._connection

        except Exception as e:
            self.logger.error(f"Failed to connect to SMTP server: {e}", exc_info=True)
            raise

    async def _close_connection(self):
        """Close SMTP connection."""
        if self._connection and self._connected:
            try:
                self._connection.quit()
            except Exception as e:
                self.logger.warning(f"Error closing SMTP connection: {e}")
            finally:
                self._connection = None
                self._connected = False

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Send email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body
            attachments: Optional list of attachments

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            # Attach plain text and HTML versions
            part1 = MIMEText(body_text, "plain")
            part2 = MIMEText(body_html, "html")
            msg.attach(part1)
            msg.attach(part2)

            # Add attachments
            if attachments:
                for attachment in attachments:
                    filename = attachment.get("filename", "attachment")
                    content = attachment.get("content", b"")
                    part = MIMEApplication(content, Name=filename)
                    part["Content-Disposition"] = f'attachment; filename="{filename}"'
                    msg.attach(part)

            # Get connection and send
            connection = await self._get_connection()
            connection.send_message(msg)

            self.logger.info(f"Sent email to {to_email}: {subject}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {e}", exc_info=True)
            # Try to reconnect on next attempt
            await self._close_connection()
            return False

    async def test_connection(self) -> bool:
        """Test SMTP connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            await self._get_connection()
            self.logger.info("SMTP connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {e}")
            return False


class EmailService:
    """Service for sending emails."""

    def __init__(self, provider: Optional[EmailProvider] = None):
        """Initialize email service.

        Args:
            provider: Email provider instance (defaults to ConsoleEmailProvider for development)
        """
        self.logger = get_logger(__name__)

        # Choose provider based on configuration
        if provider is not None:
            self.provider = provider
        else:
            # Check if SMTP is configured
            smtp_host = getattr(config, "SMTP_HOST", None)
            if smtp_host:
                self.provider = SMTPEmailProvider()
                self.logger.info(f"Using SMTP email provider ({smtp_host})")
            else:
                self.provider = ConsoleEmailProvider()
                self.logger.info("Using console email provider (development mode)")

    def set_provider(self, provider: EmailProvider):
        """Set email provider at runtime.

        Args:
            provider: Email provider instance
        """
        self.provider = provider
        self.logger.info(f"Changed email provider to {type(provider).__name__}")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Send an email using the configured provider."""
        return await self.provider.send_email(
            to_email=to_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            attachments=attachments,
        )

    async def send_password_reset_email(
        self, to_email: str, reset_token: str, user_name: Optional[str] = None
    ):
        """Send password reset email."""
        reset_link = f"{config.frontend_url}/reset-password?token={reset_token}"
        name = user_name or "User"

        subject = "Reset Your Password"

        body_text = f"""
        Hello {name},
        
        You have requested to reset your password. Please click the link below to reset it:
        
        {reset_link}
        
        If you did not request this, please ignore this email.
        
        This link will expire in 1 hour.
        """

        body_html = f"""
        <html>
            <body>
                <h2>Reset Your Password</h2>
                <p>Hello {name},</p>
                <p>You have requested to reset your password. Please click the link below to reset it:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>If you did not request this, please ignore this email.</p>
                <p>This link will expire in 1 hour.</p>
            </body>
        </html>
        """

        return await self.provider.send_email(to_email, subject, body_html, body_text)
