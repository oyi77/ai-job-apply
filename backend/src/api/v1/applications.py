"""Applications API endpoints for the AI Job Application Assistant."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from ...models.application import JobApplication, ApplicationUpdateRequest, ApplicationStatus
from ...services.service_registry import service_registry
from ...utils.response_wrapper import success_response, error_response, paginated_response
from loguru import logger

router = APIRouter()


@router.post("/", response_model=Dict[str, Any])
async def create_application(
    job_info: Dict[str, Any],
    resume_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new job application.
    
    Args:
        job_info: Job information dictionary
        resume_path: Optional path to resume file
        
    Returns:
        Consistent API response with created application
    """
    try:
        # Get application service from registry
        application_service = await service_registry.get_application_service()
        
        # Use the application service
        application = await application_service.create_application(job_info, resume_path)
        
        logger.info(f"Application created for {application.job_title} at {application.company}")
        return success_response(application.dict(), "Application created successfully").dict()
        
    except Exception as e:
        logger.error(f"Error creating application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Application creation failed: {str(e)}")


@router.get("", response_model=Dict[str, Any])
async def get_all_applications(
    status: Optional[ApplicationStatus] = None
) -> Dict[str, Any]:
    """
    Get all applications with optional status filter.
    
    Args:
        status: Optional status filter
        
    Returns:
        Consistent API response with list of applications
    """
    try:
        # Get application service from registry
        application_service = await service_registry.get_application_service()
        
        # Use the application service
        if status:
            applications = await application_service.get_applications_by_status(status)
        else:
            applications = await application_service.get_all_applications()
        
        return success_response([app.dict() for app in applications], f"Retrieved {len(applications)} applications").dict()
        
    except Exception as e:
        logger.error(f"Error getting applications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get applications: {str(e)}")


@router.get("/stats")
async def get_application_stats() -> Dict[str, Any]:
    """
    Get application statistics and summary.
    
    Returns:
        Consistent API response with application statistics
    """
    try:
        # Get application service from registry
        application_service = await service_registry.get_application_service()
        
        # Get statistics from service
        stats = await application_service.get_application_stats()
        return success_response(stats, "Application statistics retrieved successfully").dict()
        
    except Exception as e:
        logger.error(f"Error getting application stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get application statistics: {str(e)}")


@router.get("/stats/summary")
async def get_application_stats_summary() -> Dict[str, Any]:
    """
    Get application statistics summary (legacy endpoint).
    
    Returns:
        Application statistics
    """
    return await get_application_stats()


@router.get("/{application_id}", response_model=Dict[str, Any])
async def get_application(application_id: str) -> Dict[str, Any]:
    """
    Get a specific application by ID.
    
    Args:
        application_id: Application identifier
        
    Returns:
        Consistent API response with application object
    """
    try:
        # Get application service from registry
        application_service = await service_registry.get_application_service()
        
        # Get application by ID
        application = await application_service.get_application(application_id)
        
        if not application:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        return success_response(application.dict(), "Application retrieved successfully").dict()
        
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
    Update an application.
    
    Args:
        application_id: Application identifier
        updates: Update request object
        
    Returns:
        Updated application object
    """
    try:
        # Get application service from registry
        application_service = await service_registry.get_application_service()
        
        # Update application
        updated_application = await application_service.update_application(application_id, updates)
        
        if not updated_application:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        logger.info(f"Application {application_id} updated successfully")
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
        application_service = await service_registry.get_application_service()
        
        # Delete application
        success = await application_service.delete_application(application_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        logger.info(f"Application {application_id} deleted successfully")
        return {"message": f"Application {application_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application {application_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")


@router.post("/{application_id}/follow-up")
async def schedule_follow_up(
    application_id: str,
    follow_up_date: str
) -> Dict[str, str]:
    """
    Schedule a follow-up for an application.
    
    Args:
        application_id: Application identifier
        follow_up_date: Follow-up date (ISO format)
        
    Returns:
        Success message
    """
    try:
        # Get application service from registry
        application_service = await service_registry.get_application_service()
        
        # Schedule follow-up
        success = await application_service.schedule_follow_up(application_id, follow_up_date)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        
        logger.info(f"Follow-up scheduled for application {application_id} on {follow_up_date}")
        return {"message": f"Follow-up scheduled for {follow_up_date}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling follow-up for {application_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to schedule follow-up: {str(e)}")


@router.get("/follow-ups/upcoming")
async def get_upcoming_follow_ups() -> List[JobApplication]:
    """
    Get applications with upcoming follow-ups.
    
    Returns:
        List of applications needing follow-up
    """
    try:
        # Get application service from registry
        application_service = await service_registry.get_application_service()
        
        # Get upcoming follow-ups
        follow_ups = await application_service.get_upcoming_follow_ups()
        return follow_ups
        
    except Exception as e:
        logger.error(f"Error getting upcoming follow-ups: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get upcoming follow-ups: {str(e)}")


@router.get("/company/{company}")
async def get_applications_by_company(company: str) -> List[JobApplication]:
    """
    Get all applications for a specific company.
    
    Args:
        company: Company name
        
    Returns:
        List of applications for the company
    """
    try:
        # Get application service from registry
        application_service = await service_registry.get_application_service()
        
        # Get applications by company
        applications = await application_service.get_applications_by_company(company)
        return applications
        
    except Exception as e:
        logger.error(f"Error getting applications for company {company}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get applications for company: {str(e)}")


@router.get("/search/{query}")
async def search_applications(query: str) -> List[JobApplication]:
    """
    Search applications by query.
    
    Args:
        query: Search query
        
    Returns:
        List of matching applications
    """
    try:
        # Get application service from registry
        application_service = await service_registry.get_application_service()
        
        # Search applications
        applications = await application_service.search_applications(query)
        return applications
        
    except Exception as e:
        logger.error(f"Error searching applications with query '{query}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search applications: {str(e)}")


@router.get("/{application_id}/timeline")
async def get_application_timeline(application_id: str) -> List[Dict[str, Any]]:
    """
    Get timeline of events for an application.
    
    Args:
        application_id: Application identifier
        
    Returns:
        List of timeline events
    """
    try:
        # Get application service from registry
        application_service = await service_registry.get_application_service()
        
        # Get application timeline
        timeline = await application_service.get_application_timeline(application_id)
        return timeline
        
    except Exception as e:
        logger.error(f"Error getting timeline for application {application_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get application timeline: {str(e)}")
