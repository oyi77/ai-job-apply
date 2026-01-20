"""API endpoints for job application automation."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from src.api.v1.dependencies import get_current_user
from src.utils.logger import get_logger

router = APIRouter(prefix="/automation", tags=["Job Application Automation"])
logger = get_logger(__name__)


class AutoApplyRequest(BaseModel):
    """Request model for automated job application."""

    job_url: str = Field(..., description="URL of the job posting")
    resume_id: Optional[str] = Field(None, description="ID of resume to use")
    cover_letter_id: Optional[str] = Field(
        None, description="ID of cover letter to use"
    )
    platform: str = Field(
        "auto", description="Platform (linkedin, indeed, glassdoor, auto)"
    )
    additional_data: Optional[Dict[str, Any]] = Field(
        None, description="Additional application data"
    )


class PlatformApplyRequest(BaseModel):
    """Request model for platform-specific application."""

    job_url: str = Field(..., description="URL of the job posting")
    resume_path: str = Field(..., description="Path to resume file")
    cover_letter_path: Optional[str] = Field(None, description="Path to cover letter")
    profile_data: Dict[str, Any] = Field(
        ..., description="User profile data for form filling"
    )


class ApplicationFormRequest(BaseModel):
    """Request model for application form extraction."""

    job_url: str = Field(..., description="URL of the job posting")


@router.post("/apply")
async def apply_to_job_automatically(
    request: AutoApplyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Apply to a job automatically using browser automation.

    This endpoint uses Playwright to navigate to the job posting,
    detect form fields, and submit an application with the user's
    resume and cover letter.
    """
    try:
        from src.services.service_registry import service_registry

        # Get job application service
        job_app_service = await service_registry.get_job_application_service()

        # Get resume and cover letter if IDs provided
        resume_service = await service_registry.get_resume_service()

        resume = None
        cover_letter = ""

        if request.resume_id:
            resume = await resume_service.get_resume(request.resume_id)
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")

        if request.cover_letter_id:
            cover_letter_service = await service_registry.get_cover_letter_service()
            cover_letter_obj = await cover_letter_service.get_cover_letter(
                request.cover_letter_id
            )
            if cover_letter_obj:
                cover_letter = cover_letter_obj.content

        # Get job details from URL (simplified - would need job service)
        from src.models.job import Job

        job = Job(
            title="Job from URL",
            company="Company",
            location="Location",
            url=request.job_url,
            portal=request.platform,
        )

        # Apply to job
        result = await job_app_service.apply_to_job(
            job=job,
            resume=resume,
            cover_letter=cover_letter,
            additional_data=request.additional_data,
        )

        return result

    except Exception as e:
        logger.error(f"Auto-apply failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Application failed: {str(e)}")


@router.post("/extract-form")
async def extract_application_form(
    request: ApplicationFormRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Extract application form information from a job posting.

    Uses browser automation to navigate to the job URL and
    detect form fields, required inputs, and file upload fields.
    """
    try:
        from src.services.service_registry import service_registry

        job_app_service = await service_registry.get_job_application_service()

        form_info = await job_app_service.extract_application_form(request.job_url)

        if form_info:
            return {"success": True, "form": form_info.model_dump()}
        else:
            return {"success": False, "message": "Could not extract form information"}

    except Exception as e:
        logger.error(f"Form extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get("/platforms")
async def get_supported_platforms(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get list of supported platforms for automated applications."""
    try:
        from src.services.service_registry import service_registry

        job_app_service = await service_registry.get_job_application_service()
        platforms = await job_app_service.get_supported_platforms()

        return {"platforms": platforms, "count": len(platforms)}

    except Exception as e:
        logger.error(f"Failed to get platforms: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_application_data(
    request: PlatformApplyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Validate application data before submission.

    Checks that all required fields are present and valid,
    and returns warnings about potential issues.
    """
    try:
        from src.services.service_registry import service_registry

        job_app_service = await service_registry.get_job_application_service()

        # Create dummy job and resume for validation
        from src.models.job import Job
        from src.models.resume import Resume

        job = Job(
            title="Validation Job",
            company="Company",
            location="Location",
            url=request.job_url,
            portal="validation",
        )

        resume = Resume(
            content="Resume content for validation", file_path=request.resume_path
        )

        validation = await job_app_service.validate_application_data(
            job=job, resume=resume, cover_letter=request.cover_letter_path or ""
        )

        return validation

    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_automation_health(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Check the health of browser automation service."""
    try:
        from src.services.service_registry import service_registry

        job_app_service = await service_registry.get_job_application_service()
        health = await job_app_service.health_check()

        return health

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {"status": "unhealthy", "error": str(e)}
