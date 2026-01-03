"""Email service for sending notifications."""

import abc
from typing import List, Optional, Dict, Any
from ..utils.logger import get_logger
from ..config import config

class EmailProvider(abc.ABC):
    """Abstract base class for email providers."""
    
    @abc.abstractmethod
    async def send_email(self, to_email: str, subject: str, body_html: str, body_text: str) -> bool:
        """Send an email."""
        pass

class ConsoleEmailProvider(EmailProvider):
    """Email provider that logs emails to console (for development)."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
    async def send_email(self, to_email: str, subject: str, body_html: str, body_text: str) -> bool:
        """Log email details to console/logger."""
        self.logger.info(f"--- EMAIL SIMULATION ---")
        self.logger.info(f"To: {to_email}")
        self.logger.info(f"Subject: {subject}")
        self.logger.debug(f"Body (Text): {body_text}")
        self.logger.info(f"--- END EMAIL ---")
        return True

class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        """Initialize email service."""
        self.logger = get_logger(__name__)
        # In a real app, choose provider based on config
        self.provider = ConsoleEmailProvider()
        
    async def send_password_reset_email(self, to_email: str, reset_token: str, user_name: Optional[str] = None):
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
