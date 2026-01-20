"""API endpoints for resume building and generation."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

from src.api.v1.dependencies import get_current_user
from src.utils.logger import get_logger

router = APIRouter(prefix="/resumes/build", tags=["Resume Builder"])
logger = get_logger(__name__)


class ResumeTemplateEnum(str, Enum):
    """Available resume templates."""

    modern = "modern"
    professional = "professional"
    minimalist = "minimalist"
    creative = "creative"
    technical = "technical"


class ResumeFormatEnum(str, Enum):
    """Output format for resume."""

    pdf = "pdf"
    docx = "docx"
    html = "html"


class ExperienceItem(BaseModel):
    """Work experience item."""

    title: str
    company: str
    location: Optional[str] = None
    start_date: str
    end_date: str
    description: Optional[str] = None
    achievements: List[str] = []


class EducationItem(BaseModel):
    """Education item."""

    degree: str
    field: str
    school: str
    graduation_date: str
    gpa: Optional[str] = None
    honors: List[str] = []


class ProjectItem(BaseModel):
    """Project item."""

    name: str
    description: Optional[str] = None
    technologies: List[str] = []
    url: Optional[str] = None


class ProfileDataRequest(BaseModel):
    """User profile data for resume generation."""

    full_name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Location")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    portfolio: Optional[str] = Field(None, description="Portfolio website")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    summary: Optional[str] = Field(None, description="Professional summary")
    skills: List[str] = Field(default_factory=list, description="List of skills")
    experience: List[ExperienceItem] = Field(
        default_factory=list, description="Work experience"
    )
    education: List[EducationItem] = Field(
        default_factory=list, description="Education"
    )
    projects: List[ProjectItem] = Field(default_factory=list, description="Projects")
    certifications: List[str] = Field(
        default_factory=list, description="Certifications"
    )
    languages: List[str] = Field(default_factory=list, description="Languages spoken")


class ResumeBuildRequest(BaseModel):
    """Request to build a resume."""

    profile: ProfileDataRequest
    template: ResumeTemplateEnum = ResumeTemplateEnum.modern
    format: ResumeFormatEnum = ResumeFormatEnum.pdf
    target_job: Optional[Dict[str, Any]] = Field(
        None, description="Target job for optimization"
    )
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")


class ResumeBuildResponse(BaseModel):
    """Response from resume build operation."""

    success: bool
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    format: Optional[str] = None
    template: Optional[str] = None
    error: Optional[str] = None


@router.post("/", response_model=ResumeBuildResponse)
async def build_resume(
    request: ResumeBuildRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Build a professional resume from profile data.

    Creates a resume in the specified format (PDF, DOCX, or HTML)
    using the selected template.
    """
    try:
        from src.services.service_registry import service_registry
        from src.services.resume_builder_service import (
            ResumeBuilderService,
            ResumeTemplate,
            ResumeFormat,
            ProfileData,
        )

        resume_builder = await service_registry.get_resume_builder_service()

        # Convert request to ProfileData
        profile_data = ProfileData(
            full_name=request.profile.full_name,
            email=request.profile.email,
            phone=request.profile.phone,
            location=request.profile.location,
            linkedin=request.profile.linkedin,
            portfolio=request.profile.portfolio,
            github=request.profile.github,
            summary=request.profile.summary,
            skills=request.profile.skills,
            experience=[exp.model_dump() for exp in request.profile.experience],
            education=[edu.model_dump() for edu in request.profile.education],
            projects=[proj.model_dump() for proj in request.profile.projects],
            certifications=request.profile.certifications,
            languages=request.profile.languages,
        )

        # Convert options
        from src.services.resume_builder_service import ResumeOptions

        options = ResumeOptions(
            template=ResumeTemplate(request.template.value),
            format=ResumeFormat(request.format.value),
        )

        # Build resume
        result = await resume_builder.build_resume(
            profile_data=profile_data,
            options=options,
            target_job=request.target_job,
        )

        if result.get("success"):
            return ResumeBuildResponse(
                success=True,
                file_path=result.get("file_path"),
                file_name=result.get("file_name"),
                format=result.get("format"),
                template=result.get("template"),
            )
        else:
            return ResumeBuildResponse(success=False, error=result.get("error"))

    except Exception as e:
        logger.error(f"Failed to build resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_resume_for_job(
    request: ResumeBuildRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Build an optimized resume for a specific job.

    Uses AI to optimize the resume content for the target job,
    highlighting relevant skills and experience.
    """
    if not request.target_job:
        raise HTTPException(
            status_code=400, detail="Target job is required for optimization"
        )

    try:
        from src.services.service_registry import service_registry

        # Use the same build endpoint but with optimization flag
        request_copy = request.model_copy()
        # The build_resume method already handles optimization if target_job is provided

        return await build_resume(request_copy, current_user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to optimize resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_available_templates(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get list of available resume templates."""
    return {
        "templates": [
            {
                "id": "modern",
                "name": "Modern",
                "description": "Clean and contemporary design",
            },
            {
                "id": "professional",
                "name": "Professional",
                "description": "Traditional and formal style",
            },
            {
                "id": "minimalist",
                "name": "Minimalist",
                "description": "Simple and elegant layout",
            },
            {
                "id": "creative",
                "name": "Creative",
                "description": "Bold and innovative design",
            },
            {
                "id": "technical",
                "name": "Technical",
                "description": "Optimized for technical roles",
            },
        ]
    }


@router.get("/formats")
async def get_available_formats(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get list of available output formats."""
    return {
        "formats": [
            {
                "id": "pdf",
                "name": "PDF",
                "description": "Best for printing and sharing",
            },
            {"id": "docx", "name": "DOCX", "description": "Editable Word document"},
            {"id": "html", "name": "HTML", "description": "Web-friendly format"},
        ]
    }


@router.post("/preview")
async def preview_resume(
    request: ResumeBuildRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generate a preview of the resume in HTML format.

    Useful for reviewing the resume before generating the final file.
    """
    try:
        from src.services.service_registry import service_registry
        from src.services.resume_builder_service import (
            ResumeBuilderService,
            ResumeTemplate,
            ResumeFormat,
            ProfileData,
        )

        resume_builder = await service_registry.get_resume_builder_service()

        # Convert request to ProfileData
        profile_data = ProfileData(
            full_name=request.profile.full_name,
            email=request.profile.email,
            phone=request.profile.phone,
            location=request.profile.location,
            linkedin=request.profile.linkedin,
            portfolio=request.profile.portfolio,
            github=request.profile.github,
            summary=request.profile.summary,
            skills=request.profile.skills,
            experience=[exp.model_dump() for exp in request.profile.experience],
            education=[edu.model_dump() for edu in request.profile.education],
            projects=[proj.model_dump() for proj in request.profile.projects],
            certifications=request.profile.certifications,
            languages=request.profile.languages,
        )

        # Build in HTML format for preview
        from src.services.resume_builder_service import ResumeOptions

        options = ResumeOptions(
            template=ResumeTemplate(request.template.value),
            format=ResumeFormat.html,
        )

        result = await resume_builder.build_resume(
            profile_data=profile_data,
            options=options,
            target_job=request.target_job,
        )

        if result.get("success"):
            return {
                "success": True,
                "html": result.get("content"),
                "template": request.template.value,
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def check_resume_builder_health(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Check the health of the resume builder service."""
    try:
        from src.services.service_registry import service_registry

        resume_builder = await service_registry.get_resume_builder_service()
        health = await resume_builder.health_check()

        return health

    except Exception as e:
        logger.error(f"Resume builder health check failed: {e}", exc_info=True)
        return {"status": "unhealthy", "error": str(e)}
