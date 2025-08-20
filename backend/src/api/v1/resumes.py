"""Resumes API endpoints for the AI Job Application Assistant."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List, Optional, Dict, Any
from ...models.resume import Resume, ResumeOptimizationRequest, ResumeOptimizationResponse
from ...utils.logger import get_logger
from ...utils.validators import validate_file_type, validate_file_size
from ...services.service_registry import service_registry

logger = get_logger(__name__)

router = APIRouter()


def create_api_response(data: Any, success: bool = True, message: str = None) -> Dict[str, Any]:
    """Create a standardized API response."""
    response = {
        "success": success,
        "data": data
    }
    if message:
        response["message"] = message
    return response


@router.post("/upload", response_model=Dict[str, Any])
async def upload_resume(
    file: UploadFile = File(...),
    name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload a new resume file.
    
    Args:
        file: Resume file to upload
        name: Optional custom name for the resume
        
    Returns:
        Created resume object
    """
    try:
        logger.info(f"Resume upload request received: {file.filename}, size: {file.size}")
        
        # Validate file type
        if not validate_file_type(file.filename, [".pdf", ".docx", ".txt"]):
            logger.warning(f"Invalid file type attempted: {file.filename}")
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only PDF, DOCX, and TXT files are allowed."
            )
        
        # Validate file size (10MB limit)
        if not validate_file_size(file.filename, 10.0):
            logger.warning(f"File too large: {file.filename}, size: {file.size}")
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Get resume service from unified registry
        resume_service = await service_registry.get_resume_service()
        
        # Get file service from unified registry
        file_service = await service_registry.get_file_service()
        
        # Read file content
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Generate unique filename
        import uuid
        from pathlib import Path
        file_extension = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("backend/uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Save file to uploads directory
        file_path = uploads_dir / unique_filename
        
        # Write file using file service
        success = await file_service.save_file(str(file_path), file_content)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")
        
        # Upload resume using resume service
        resume_name = name or file.filename or "Unnamed Resume"
        resume = await resume_service.upload_resume(str(file_path), resume_name)
        
        logger.info(f"Resume uploaded successfully: {resume.name} (ID: {resume.id})")
        return create_api_response(resume.model_dump(), True, "Resume uploaded successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Resume upload failed: {str(e)}")


@router.get("", response_model=Dict[str, Any])
async def get_all_resumes() -> Dict[str, Any]:
    """
    Get all available resumes.
    
    Returns:
        List of all resumes
    """
    try:
        # Get resume service from unified registry
        resume_service = await service_registry.get_resume_service()
        
        # Use the real resume service
        resumes = await resume_service.get_all_resumes()
        logger.info(f"Successfully retrieved {len(resumes)} resumes")
        
        # Return empty list if no resumes (this is normal)
        return create_api_response([resume.model_dump() for resume in resumes], True, f"Retrieved {len(resumes)} resumes")
        
    except Exception as e:
        logger.error(f"Error getting resumes: {e}", exc_info=True)
        # Return empty list instead of throwing error for better UX
        logger.warning("Returning empty resume list due to error")
        return create_api_response([], False, f"Failed to get resumes: {str(e)}")


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
        # Get resume service from unified registry
        resume_service = await service_registry.get_resume_service()
        
        # Get the resume
        resume = await resume_service.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail=f"Resume not found: {resume_id}")
        
        logger.info(f"Resume retrieved successfully: {resume.name} (ID: {resume_id})")
        return resume
        
    except HTTPException:
        raise
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
        # Get resume service from unified registry
        resume_service = await service_registry.get_resume_service()
        
        # Prepare updates
        updates = {}
        if name is not None:
            updates['name'] = name
        if is_default is not None:
            updates['is_default'] = is_default
        
        if not updates:
            raise HTTPException(status_code=400, detail="No update fields provided")
        
        # Update the resume
        updated_resume = await resume_service.update_resume(resume_id, updates)
        if not updated_resume:
            raise HTTPException(status_code=404, detail=f"Resume not found: {resume_id}")
        
        logger.info(f"Resume updated successfully: {updated_resume.name} (ID: {resume_id})")
        return updated_resume
        
    except HTTPException:
        raise
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
        # Get resume service from unified registry
        resume_service = await service_registry.get_resume_service()
        
        # Delete the resume
        success = await resume_service.delete_resume(resume_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Resume not found: {resume_id}")
        
        logger.info(f"Resume deleted successfully: {resume_id}")
        return {"message": "Resume deleted successfully", "resume_id": resume_id}
        
    except HTTPException:
        raise
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
        # Get resume service from unified registry
        resume_service = await service_registry.get_resume_service()
        
        # Set as default resume
        success = await resume_service.set_default_resume(resume_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Resume not found: {resume_id}")
        
        logger.info(f"Default resume set successfully: {resume_id}")
        return {"message": "Resume set as default successfully", "resume_id": resume_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting default resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to set default resume: {str(e)}")
