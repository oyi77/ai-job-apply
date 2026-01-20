"""Notification validators for request validation."""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class EmailTemplateEnum(str, Enum):
    """Available email templates."""

    FOLLOW_UP_REMINDER = "follow_up_reminder"
    STATUS_CHECK_REMINDER = "status_check_reminder"
    INTERVIEW_PREP_REMINDER = "interview_prep_reminder"
    PASSWORD_RESET = "password_reset"
    APPLICATION_CONFIRMATION = "application_confirmation"
    WELCOME = "welcome"


class SendEmailRequest(BaseModel):
    """Request model for sending email notifications."""

    to_email: EmailStr = Field(..., description="Recipient email address")
    template_name: EmailTemplateEnum = Field(..., description="Template to use")
    template_data: Dict[str, Any] = Field(
        default_factory=dict, description="Dynamic data for template rendering"
    )
    attachments: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Optional email attachments"
    )
    tags: Optional[List[str]] = Field(
        default=None, description="Optional tags for tracking"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "to_email": "user@example.com",
                "template_name": "follow_up_reminder",
                "template_data": {
                    "user_name": "John Doe",
                    "job_title": "Software Engineer",
                    "company": "TechCorp",
                    "application_id": "app_123",
                },
            }
        }


class SendTestEmailRequest(BaseModel):
    """Request model for sending test emails."""

    to_email: EmailStr = Field(..., description="Recipient email address for test")
    template_name: Optional[EmailTemplateEnum] = Field(
        default=None, description="Optional template to test (defaults to welcome)"
    )

    class Config:
        json_schema_extra = {
            "example": {"to_email": "test@example.com", "template_name": "welcome"}
        }


class ListTemplatesResponse(BaseModel):
    """Response model for listing templates."""

    templates: List[Dict[str, Any]] = Field(
        ..., description="List of available templates"
    )


class SendEmailResponse(BaseModel):
    """Response model for send email endpoint."""

    success: bool = Field(..., description="Whether email was sent successfully")
    message: str = Field(..., description="Status message")
    message_id: Optional[str] = Field(
        default=None, description="Mailgun message ID if sent"
    )


class NotificationSettingsUpdate(BaseModel):
    """Request model for updating notification settings."""

    email_enabled: bool = Field(
        default=True, description="Enable/disable email notifications"
    )
    follow_up_reminders: bool = Field(
        default=True, description="Enable follow-up reminders"
    )
    interview_reminders: bool = Field(
        default=True, description="Enable interview reminders"
    )
    application_status_updates: bool = Field(
        default=True, description="Enable status update notifications"
    )
    marketing_emails: bool = Field(default=False, description="Enable marketing emails")
