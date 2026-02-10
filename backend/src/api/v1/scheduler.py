"""API endpoints for job application reminders and scheduling."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

from src.api.dependencies import get_current_user
from src.utils.logger import get_logger

router = APIRouter(prefix="/scheduler", tags=["Job Application Reminders"])
logger = get_logger(__name__)


def _get_user_value(current_user: Any, key: str) -> Optional[Any]:
    """Safely read user values from profile or dict."""
    if isinstance(current_user, dict):
        return current_user.get(key)
    return getattr(current_user, key, None)


class FollowUpReminderRequest(BaseModel):
    """Request to schedule follow-up reminder."""

    application_id: str = Field(..., description="ID of the job application")
    job_title: str = Field(..., description="Title of the job")
    company: str = Field(..., description="Company name")
    application_date: datetime = Field(
        ..., description="When the application was submitted"
    )
    days_until_followup: int = Field(
        default=7, description="Days after application to send reminder"
    )


class StatusCheckRequest(BaseModel):
    """Request to schedule status check reminder."""

    application_id: str = Field(..., description="ID of the job application")
    job_title: str = Field(..., description="Title of the job")
    company: str = Field(..., description="Company name")
    last_update: datetime = Field(
        ..., description="When the application was last updated"
    )
    days_until_check: int = Field(
        default=14, description="Days without update to send reminder"
    )


class InterviewPrepRequest(BaseModel):
    """Request to schedule interview preparation reminder."""

    application_id: str = Field(..., description="ID of the job application")
    job_title: str = Field(..., description="Title of the job")
    company: str = Field(..., description="Company name")
    interview_date: datetime = Field(..., description="Scheduled interview date")
    days_before_interview: int = Field(
        default=2, description="Days before interview to send reminder"
    )


class ReminderResponse(BaseModel):
    """Response model for reminder operations."""

    success: bool
    reminder_id: Optional[str] = None
    message: str


class ReminderListResponse(BaseModel):
    """Response model for listing reminders."""

    reminders: List[Dict[str, Any]]
    count: int


@router.post("/follow-up", response_model=ReminderResponse)
async def schedule_follow_up_reminder(
    request: FollowUpReminderRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Schedule a follow-up reminder for a job application.

    Sends a reminder after the specified number of days to help
    the user follow up on their application.
    """
    try:
        from src.services.service_registry import service_registry

        scheduler_service = await service_registry.get_scheduler_service()

        reminder_id = await scheduler_service.schedule_follow_up(
            application_id=request.application_id,
            user_id=_get_user_value(current_user, "id"),
            application_date=request.application_date,
            job_title=request.job_title,
            company=request.company,
            metadata={
                "user_email": _get_user_value(current_user, "email"),
                "user_name": _get_user_value(current_user, "name"),
                "days_until_followup": request.days_until_followup,
            },
        )

        if reminder_id:
            return ReminderResponse(
                success=True,
                reminder_id=reminder_id,
                message=f"Follow-up reminder scheduled for {request.job_title} at {request.company}",
            )
        else:
            return ReminderResponse(
                success=False, message="Failed to schedule reminder"
            )

    except Exception as e:
        logger.error(f"Failed to schedule follow-up reminder: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/status-check", response_model=ReminderResponse)
async def schedule_status_check_reminder(
    request: StatusCheckRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Schedule a status check reminder for a stale application.

    Sends a reminder if the application hasn't been updated in the
    specified number of days.
    """
    try:
        from src.services.service_registry import service_registry

        scheduler_service = await service_registry.get_scheduler_service()

        reminder_id = await scheduler_service.schedule_status_check(
            application_id=request.application_id,
            user_id=_get_user_value(current_user, "id"),
            last_update=request.last_update,
            job_title=request.job_title,
            company=request.company,
            metadata={
                "user_email": _get_user_value(current_user, "email"),
                "user_name": _get_user_value(current_user, "name"),
                "days_until_check": request.days_until_check,
            },
        )

        if reminder_id:
            return ReminderResponse(
                success=True,
                reminder_id=reminder_id,
                message=f"Status check reminder scheduled for {request.job_title} at {request.company}",
            )
        else:
            return ReminderResponse(
                success=False, message="Failed to schedule reminder"
            )

    except Exception as e:
        logger.error(f"Failed to schedule status check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview-prep", response_model=ReminderResponse)
async def schedule_interview_prep_reminder(
    request: InterviewPrepRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Schedule an interview preparation reminder.

    Sends a reminder before the scheduled interview to help
    the user prepare.
    """
    try:
        from src.services.service_registry import service_registry

        scheduler_service = await service_registry.get_scheduler_service()

        reminder_id = await scheduler_service.schedule_interview_prep(
            application_id=request.application_id,
            user_id=_get_user_value(current_user, "id"),
            interview_date=request.interview_date,
            job_title=request.job_title,
            company=request.company,
            metadata={
                "user_email": _get_user_value(current_user, "email"),
                "user_name": _get_user_value(current_user, "name"),
                "days_before_interview": request.days_before_interview,
            },
        )

        if reminder_id:
            return ReminderResponse(
                success=True,
                reminder_id=reminder_id,
                message=f"Interview prep reminder scheduled for {request.job_title} at {request.company}",
            )
        else:
            return ReminderResponse(
                success=False, message="Failed to schedule reminder"
            )

    except Exception as e:
        logger.error(f"Failed to schedule interview prep: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reminder/{reminder_id}", response_model=ReminderResponse)
async def cancel_reminder(
    reminder_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Cancel a scheduled reminder."""
    try:
        from src.services.service_registry import service_registry

        scheduler_service = await service_registry.get_scheduler_service()

        success = await scheduler_service.cancel_reminder(reminder_id)

        if success:
            return ReminderResponse(
                success=True, message=f"Reminder {reminder_id} cancelled"
            )
        else:
            return ReminderResponse(
                success=False, message=f"Reminder {reminder_id} not found"
            )

    except Exception as e:
        logger.error(f"Failed to cancel reminder: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reminders", response_model=ReminderListResponse)
async def get_pending_reminders(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get all pending reminders for the current user."""
    try:
        from src.services.service_registry import service_registry

        scheduler_service = await service_registry.get_scheduler_service()

        reminders = await scheduler_service.get_pending_reminders(
            _get_user_value(current_user, "id")
        )

        # Convert to dict format
        reminder_list = []
        for reminder in reminders:
            reminder_list.append(
                {
                    "id": reminder.id,
                    "application_id": reminder.application_id,
                    "type": reminder.reminder_type,
                    "scheduled_time": reminder.scheduled_time.isoformat(),
                    "sent": reminder.sent,
                    "metadata": reminder.metadata,
                }
            )

        return ReminderListResponse(reminders=reminder_list, count=len(reminder_list))

    except Exception as e:
        logger.error(f"Failed to get reminders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reminder/{reminder_id}/status")
async def get_reminder_status(
    reminder_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get the status of a specific reminder."""
    try:
        from src.services.service_registry import service_registry

        scheduler_service = await service_registry.get_scheduler_service()

        status = await scheduler_service.get_reminder_status(reminder_id)

        if status:
            return status
        else:
            raise HTTPException(status_code=404, detail="Reminder not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reminder status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_scheduler(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Start the scheduler service (admin only)."""
    try:
        from src.services.service_registry import service_registry

        scheduler_service = await service_registry.get_scheduler_service()

        success = await scheduler_service.start()

        return {
            "success": success,
            "message": "Scheduler started" if success else "Failed to start scheduler",
        }

    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_scheduler(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Stop the scheduler service (admin only)."""
    try:
        from src.services.service_registry import service_registry

        scheduler_service = await service_registry.get_scheduler_service()

        await scheduler_service.stop()

        return {"success": True, "message": "Scheduler stopped"}

    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_scheduler_health(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Check the health of the scheduler service."""
    try:
        from src.services.service_registry import service_registry

        scheduler_service = await service_registry.get_scheduler_service()
        health = await scheduler_service.health_check()

        return health

    except Exception as e:
        logger.error(f"Scheduler health check failed: {e}", exc_info=True)
        return {"status": "unhealthy", "error": str(e)}
