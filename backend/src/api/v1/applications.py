"""Applications API endpoints for the AI Job Application Assistant."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from ...models.application import JobApplication, ApplicationUpdateRequest, ApplicationStatus
from ...utils.logger import get_logger
from ...services.service_registry import service_registry
from ...services.database_service_registry import database_service_registry

logger = get_logger(__name__)

router = APIRouter()


@router.post("/", response_model=JobApplication)
async def create_application(
    job_info: Dict[str, Any],
    resume_path: Optional[str] = None
) -> JobApplication:
    """
    Create a new job application.
    
    Args:
        job_info: Job information dictionary
        resume_path: Optional path to resume file
        
    Returns:
        Created application object
    """
    try:
        # Get application service from registry
        # Try database service registry first, fallback to in-memory
        try:
            application_service = database_service_registry.get_application_service()
        except RuntimeError:
            application_service = service_registry.get_application_service()
        
        # Use the real application service
        application = await application_service.create_application(job_info, resume_path)
        
        logger.info(f"Application created for {application.job_title} at {application.company}")
        return application
        
    except Exception as e:
        logger.error(f"Error creating application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Application creation failed: {str(e)}")


@router.get("/", response_model=List[JobApplication])
async def get_all_applications(
    status: Optional[ApplicationStatus] = None
) -> List[JobApplication]:
    """
    Get all applications with optional status filter.
    
    Args:
        status: Optional status filter
        
    Returns:
        List of applications
    """
    try:
        # Get application service from registry
        # Try database service registry first, fallback to in-memory
        try:
            application_service = database_service_registry.get_application_service()
        except RuntimeError:
            application_service = service_registry.get_application_service()
        
        # Use the real application service
        if status:
            applications = await application_service.get_applications_by_status(status)
        else:
            applications = await application_service.get_all_applications()
        
        return applications
        
    except Exception as e:
        logger.error(f"Error getting applications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get applications: {str(e)}")


@router.get("/stats/summary")
async def get_application_stats() -> Dict[str, Any]:
    """
    Get application statistics and summary.
    
    Returns:
        Application statistics
    """
    try:
        # Get application service from registry
        # Try database service registry first, fallback to in-memory
        try:
            application_service = database_service_registry.get_application_service()
        except RuntimeError:
            application_service = service_registry.get_application_service()
        
        # Get statistics from service
        stats = await application_service.get_application_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting application stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get application statistics: {str(e)}")


@router.get("/{application_id}", response_model=JobApplication)
async def get_application(application_id: str) -> JobApplication:
    """
    Get a specific application by ID.
    
    Args:
        application_id: Application identifier
        
    Returns:
        Application object
    """
    try:
        # Get application service from registry
        # Try database service registry first, fallback to in-memory
        try:
            application_service = database_service_registry.get_application_service()
        except RuntimeError:
            application_service = service_registry.get_application_service()
        
        # Get application by ID
        application = await application_service.get_application(application_id)
        
        if not application:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        return application
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting application {application_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get application: {str(e)}")


@router.put("/{application_id}", response_model=JobApplication)
async def update_application(
    application_id: str,
    updates: ApplicationUpdateRequest
) -> JobApplication:
    """
    Update application status and information.
    
    Args:
        application_id: Application identifier
        updates: Update request data
        
    Returns:
        Updated application object
    """
    try:
        # Get application service from registry
        # Try database service registry first, fallback to in-memory
        try:
            application_service = database_service_registry.get_application_service()
        except RuntimeError:
            application_service = service_registry.get_application_service()
        
        # Update application
        updated_application = await application_service.update_application(application_id, updates)
        
        if not updated_application:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        return updated_application
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application {application_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update application: {str(e)}")


@router.delete("/{application_id}")
async def delete_application(application_id: str) -> Dict[str, str]:
    """
    Delete an application.
    
    Args:
        application_id: Application identifier
        
    Returns:
        Success message
    """
    try:
        # Get application service from registry
        # Try database service registry first, fallback to in-memory
        try:
            application_service = database_service_registry.get_application_service()
        except RuntimeError:
            application_service = service_registry.get_application_service()
        
        # Delete application
        success = await application_service.delete_application(application_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        return {"message": f"Application {application_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application {application_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")
