"""Notification API endpoints for email and push notifications."""

from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Dict, Any, Optional
from src.validators.notification_validators import (
    SendEmailRequest,
    SendTestEmailRequest,
    SendEmailResponse,
    EmailTemplateEnum,
    NotificationSettingsUpdate,
)
from src.models.user import UserProfile
from src.services.service_registry import service_registry
from src.services.email_templates import email_template_renderer
from src.utils.response_wrapper import success_response, error_response
from src.api.dependencies import get_current_user
from src.database.config import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.push_subscription import (
    PushSubscriptionCreate,
    PushSubscriptionDelete,
    PushMessage,
)
from loguru import logger

router = APIRouter()


@router.post("/email", response_model=Dict[str, Any])
async def send_email_notification(
    request: SendEmailRequest, current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Send an email notification using a template.

    Args:
        request: Email notification request with template and data
        current_user: Authenticated user

    Returns:
        Success response with message ID
    """
    try:
        # Get mailgun provider from service registry
        mailgun_provider = await service_registry.get_mailgun_provider()

        if mailgun_provider is None:
            # Check if we have SMTP as fallback
            email_service = await service_registry.get_email_service()
            if email_service is None:
                raise HTTPException(
                    status_code=503,
                    detail="Email service not configured. Please set up Mailgun or SMTP.",
                )

        # Render the email template
        subject, body_html, body_text = await email_template_renderer.render(
            template_name=request.template_name.value, data=request.template_data
        )

        # Send the email
        if mailgun_provider:
            # Use Mailgun
            result = await mailgun_provider.send_email(
                to_email=request.to_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                attachments=request.attachments,
                tags=request.tags,
            )

            if result:
                logger.info(f"Email sent to {request.to_email} using Mailgun")
                return success_response(
                    {"message_id": f"mailgun_{request.to_email}"},
                    "Email sent successfully via Mailgun",
                ).dict()
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to send email via Mailgun"
                )
        else:
            # Fall back to SMTP
            email_service = await service_registry.get_email_service()
            result = await email_service.send_email(
                to_email=request.to_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
            )

            if result:
                logger.info(f"Email sent to {request.to_email} using SMTP")
                return success_response(
                    {"message_id": f"smtp_{request.to_email}"},
                    "Email sent successfully via SMTP",
                ).dict()
            else:
                raise HTTPException(
                    status_code=500, detail="Failed to send email via SMTP"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email notification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/email/test", response_model=Dict[str, Any])
async def send_test_email(
    request: SendTestEmailRequest, current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Send a test email to verify configuration.

    Args:
        request: Test email request
        current_user: Authenticated user

    Returns:
        Success response
    """
    try:
        # Get mailgun provider
        mailgun_provider = await service_registry.get_mailgun_provider()

        if mailgun_provider is None:
            raise HTTPException(status_code=503, detail="Email service not configured")

        # Use welcome template if none specified
        template_name = (
            request.template_name.value if request.template_name else "welcome"
        )

        # Render template with test data
        subject, body_html, body_text = await email_template_renderer.render(
            template_name=template_name,
            data={
                "user_name": current_user.name or "Test User",
                "app_url": "https://app.example.com",
            },
        )

        # Send test email
        result = await mailgun_provider.send_email(
            to_email=request.to_email,
            subject=f"[TEST] {subject}",
            body_html=body_html,
            body_text=body_text,
        )

        if result:
            logger.info(f"Test email sent to {request.to_email}")
            return success_response(
                {"test_sent_to": request.to_email}, "Test email sent successfully"
            ).dict()
        else:
            raise HTTPException(status_code=500, detail="Failed to send test email")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test email: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to send test email: {str(e)}"
        )


@router.get("/email/templates", response_model=Dict[str, Any])
async def list_email_templates(
    current_user: UserProfile = Depends(get_current_user),
) -> Dict[str, Any]:
    """List all available email templates.

    Args:
        current_user: Authenticated user

    Returns:
        List of available templates
    """
    try:
        templates = []

        for template_value, template_name in EmailTemplateEnum.__members__.items():
            # Get a sample rendering of each template
            sample_data = {
                "user_name": current_user.name or "User",
                "job_title": "Sample Position",
                "company": "Sample Company",
                "application_id": "sample_id",
                "app_url": "https://app.example.com",
            }

            # Don't actually render - just list the templates
            templates.append(
                {
                    "id": template_value,
                    "name": template_name.value,
                    "description": f"Template for {template_name.value.replace('_', ' ')}",
                }
            )

        return success_response(
            {"templates": templates}, "Templates retrieved successfully"
        ).dict()

    except Exception as e:
        logger.error(f"Error listing templates: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to list templates: {str(e)}"
        )


@router.post("/settings", response_model=Dict[str, Any])
async def update_notification_settings(
    settings: NotificationSettingsUpdate,
    current_user: UserProfile = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update user notification settings.

    Args:
        settings: New notification settings
        current_user: Authenticated user

    Returns:
        Success response
    """
    try:
        # Store settings (in a real app, this would go to the database)
        logger.info(f"Updating notification settings for user {current_user.id}")

        return success_response(
            settings.dict(), "Notification settings updated successfully"
        ).dict()

    except Exception as e:
        logger.error(f"Error updating notification settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to update settings: {str(e)}"
        )


@router.get("/settings", response_model=Dict[str, Any])
async def get_notification_settings(
    current_user: UserProfile = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get current notification settings.

    Args:
        current_user: Authenticated user

    Returns:
        Current notification settings
    """
    try:
        # Return default settings (in a real app, this would come from the database)
        default_settings = {
            "email_enabled": True,
            "follow_up_reminders": True,
            "interview_reminders": True,
            "application_status_updates": True,
            "marketing_emails": False,
        }

        return success_response(
            default_settings, "Settings retrieved successfully"
        ).dict()

    except Exception as e:
        logger.error(f"Error getting notification settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")


@router.post("/push/subscribe", response_model=Dict[str, Any])
async def subscribe_push_notifications(
    subscription: PushSubscriptionCreate,
    current_user: UserProfile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Subscribe the current user to Web Push notifications."""

    try:
        push_service = await service_registry.get_push_service()
        subscription_id = await push_service.subscribe(
            user_id=current_user.id, subscription=subscription, session=session
        )
        return success_response(
            {"subscription_id": subscription_id}, "Push subscription saved"
        ).dict()
    except KeyError:
        raise HTTPException(status_code=503, detail="Push service not available")
    except Exception as e:
        logger.error(f"Error subscribing to push notifications: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to subscribe: {str(e)}"
        )


@router.post("/push/unsubscribe", response_model=Dict[str, Any])
async def unsubscribe_push_notifications(
    request: PushSubscriptionDelete,
    current_user: UserProfile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Unsubscribe the current user from a Web Push endpoint."""

    try:
        push_service = await service_registry.get_push_service()
        removed = await push_service.unsubscribe(
            user_id=current_user.id, endpoint=request.endpoint, session=session
        )
        return success_response(
            {"removed": removed}, "Push subscription removed"
        ).dict()
    except KeyError:
        raise HTTPException(status_code=503, detail="Push service not available")
    except Exception as e:
        logger.error(f"Error unsubscribing from push notifications: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to unsubscribe: {str(e)}"
        )


@router.post("/push/test", response_model=Dict[str, Any])
async def send_test_push_notification(
    message: PushMessage,
    current_user: UserProfile = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Send a test push notification to the current user."""

    try:
        push_service = await service_registry.get_push_service()
        attempted = await push_service.send_to_user(
            user_id=current_user.id, message=message, session=session
        )
        return success_response(
            {"attempted": attempted}, "Push send attempted"
        ).dict()
    except KeyError:
        raise HTTPException(status_code=503, detail="Push service not available")
    except Exception as e:
        logger.error(f"Error sending test push notification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send push: {str(e)}")
