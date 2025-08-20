"""Resumes API endpoints for the AI Job Application Assistant."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List, Optional
from ...models.resume import Resume, ResumeOptimizationRequest, ResumeOptimizationResponse
from ...utils.logger import get_logger
from ...utils.validators import validate_file_type, validate_file_size
from ...services.service_registry import service_registry
from ...services.database_service_registry import database_service_registry

logger = get_logger(__name__)

router = APIRouter()


@router.post("/upload", response_model=Resume)
async def upload_resume(
    file: UploadFile = File(...),
    name: Optional[str] = None
) -> Resume:
    """
    Upload a new resume file.
    
    Args:
        file: Resume file to upload
        name: Optional custom name for the resume
        
    Returns:
        Created resume object
    """
    try:
        # Validate file type
        if not validate_file_type(file.filename, [".pdf", ".docx", ".txt"]):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only PDF, DOCX, and TXT files are allowed."
            )
        
        # Validate file size (10MB limit)
        if not validate_file_size(file.filename, 10.0):
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # TODO: Implement actual file upload service
        resume_name = name or file.filename or "Unnamed Resume"
        
        # Mock resume creation
        resume = Resume(
            name=resume_name,
            file_path=f"./resumes/{file.filename}",
            file_type=file.filename.split(".")[-1] if "." in file.filename else "unknown"
        )
        
        logger.info(f"Resume uploaded: {resume.name}")
        return resume
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Resume upload failed: {str(e)}")


@router.get("/", response_model=List[Resume])
async def get_all_resumes() -> List[Resume]:
    """
    Get all available resumes.
    
    Returns:
        List of all resumes
    """
    try:
        # Get resume service from registry
        # Try database service registry first, fallback to in-memory
        try:
            resume_service = database_service_registry.get_resume_service()
        except RuntimeError:
            resume_service = service_registry.get_resume_service()
        
        # Use the real resume service
        resumes = await resume_service.get_all_resumes()
        
        return resumes
        
    except Exception as e:
        logger.error(f"Error getting resumes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get resumes: {str(e)}")


@router.get("/{resume_id}", response_model=Resume)
async def get_resume(resume_id: str) -> Resume:
    """
    Get a specific resume by ID.
    
    Args:
        resume_id: Resume identifier
        
    Returns:
        Resume object
    """
    try:
        # TODO: Implement actual resume retrieval service
        raise HTTPException(status_code=501, detail="Resume retrieval not yet implemented")
        
    except Exception as e:
        logger.error(f"Error getting resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get resume: {str(e)}")


@router.put("/{resume_id}", response_model=Resume)
async def update_resume(
    resume_id: str,
    name: Optional[str] = None,
    is_default: Optional[bool] = None
) -> Resume:
    """
    Update resume information.
    
    Args:
        resume_id: Resume identifier
        name: New name for the resume
        is_default: Whether to set as default resume
        
    Returns:
        Updated resume object
    """
    try:
        # TODO: Implement actual resume update service
        raise HTTPException(status_code=501, detail="Resume update not yet implemented")
        
    except Exception as e:
        logger.error(f"Error updating resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update resume: {str(e)}")


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str) -> dict:
    """
    Delete a resume.
    
    Args:
        resume_id: Resume identifier
        
    Returns:
        Deletion confirmation
    """
    try:
        # TODO: Implement actual resume deletion service
        raise HTTPException(status_code=501, detail="Resume deletion not yet implemented")
        
    except Exception as e:
        logger.error(f"Error deleting resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete resume: {str(e)}")


@router.post("/{resume_id}/set-default")
async def set_default_resume(resume_id: str) -> dict:
    """
    Set a resume as the default.
    
    Args:
        resume_id: Resume identifier
        
    Returns:
        Confirmation message
    """
    try:
        # TODO: Implement actual default resume setting service
        raise HTTPException(status_code=501, detail="Default resume setting not yet implemented")
        
    except Exception as e:
        logger.error(f"Error setting default resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to set default resume: {str(e)}")
