"""Job Application API endpoints for the AI Job Application Assistant."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...models.job import Job, ApplicationInfo
from ...models.resume import Resume
from ...models.application import JobApplication
from ...models.user import UserProfile
from ...api.dependencies import get_current_user
from ...utils.logger import get_logger
from ...utils.response_wrapper import success_response, error_response
from ...services.service_registry import service_registry

logger = get_logger(__name__)

router = APIRouter()


@router.post("/apply", response_model=Dict[str, Any])
async def apply_to_job(
    job_id: str = Form(...),
    resume_id: str = Form(...),
    cover_letter: str = Form(...),
    additional_data: Optional[str] = Form(None),
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Apply to a job using the appropriate method.
    
    Args:
        job_id: ID of the job to apply to
        resume_id: ID of the resume to submit
        cover_letter: Cover letter text
        additional_data: Additional form data as JSON string
        
    Returns:
        Application result with status and details
    """
    try:
        logger.info(f"Job application request: job_id={job_id}, resume_id={resume_id}")
        
        # Get required services
        job_search_service = await service_registry.get_job_search_service()
        resume_service = await service_registry.get_resume_service()
        application_service = await service_registry.get_job_application_service()
        
        # Get job details
        job = await job_search_service.get_job_details(job_id, "unknown")
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Get resume
        resume = await resume_service.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")
        
        # Parse additional data
        parsed_additional_data = {}
        if additional_data:
            try:
                import json
                parsed_additional_data = json.loads(additional_data)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in additional_data: {additional_data}")
        
        # Apply to job
        result = await application_service.apply_to_job(
            job=job,
            resume=resume,
            cover_letter=cover_letter,
            additional_data=parsed_additional_data
        )
        
        if result.get("success"):
            # Prepare application data
            application_data = {
                "job_id": job_id,
                "job_title": job.title,
                "company": job.company,
                "status": "applied",
                "resume_path": None,  # Resume ID tracked in notes/relations
                "cover_letter_path": None, # Cover letter content in notes/relations
                "applied_date": datetime.utcnow(),
                "notes": f"Applied via {result.get('method', 'unknown')} method. Resume ID: {resume_id}, Cover Letter Length: {len(cover_letter)}"
            }
            
            # Save application with user association
            await application_service.create_application(application_data, user_id=current_user.id)
            
            logger.info(f"Successfully applied to job: {job.title} at {job.company}")
            return {
                "success": True,
                "data": result,
                "message": "Job application submitted successfully"
            }
        else:
            logger.error(f"Job application failed: {result.get('error')}")
            raise HTTPException(status_code=400, detail=f"Job application failed: {result.get('error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying to job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Application failed: {str(e)}")


@router.get("/info/{job_id}", response_model=ApplicationInfo)
async def get_job_application_info(
    job_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> ApplicationInfo:
    """
    Get application information for a specific job.
    
    Args:
        job_id: ID of the job
        
    Returns:
        Application information including method, URLs, and forms
    """
    try:
        logger.info(f"Getting application info for job: {job_id}")
        
        # Get required services
        job_search_service = await service_registry.get_job_search_service()
        application_service = await service_registry.get_job_application_service()
        
        # Get job details
        job = await job_search_service.get_job_details(job_id, "unknown")
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Get application info
        application_info = await application_service.get_application_info(job)
        
        logger.info(f"Retrieved application info for job: {job.title}")
        return application_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting application info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get application info: {str(e)}")


@router.get("/status/{application_id}", response_model=Dict[str, Any])
async def get_application_status(
    application_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check the status of a submitted application.
    
    Args:
        application_id: Unique identifier for the application
        
    Returns:
        Application status information
    """
    try:
        logger.info(f"Checking application status: {application_id}")
        
        # Get application service
        application_service = await service_registry.get_job_application_service()
        
        # Get application status
        status = await application_service.get_application_status(application_id)
        
        logger.info(f"Retrieved status for application: {application_id}")
        return success_response(
            data=status,
            message="Application status retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error checking application status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to check status: {str(e)}")


@router.post("/validate", response_model=Dict[str, Any])
async def validate_application_data(
    job_id: str = Form(...),
    resume_id: str = Form(...),
    cover_letter: str = Form(...),
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate application data before submission.
    
    Args:
        job_id: ID of the job to apply to
        resume_id: ID of the resume to submit
        cover_letter: Cover letter text
        
    Returns:
        Validation results with any errors or warnings
    """
    try:
        logger.info(f"Validating application data: job_id={job_id}, resume_id={resume_id}")
        
        # Get required services
        job_search_service = await service_registry.get_job_search_service()
        resume_service = await service_registry.get_resume_service()
        application_service = await service_registry.get_job_application_service()
        
        # Get job details
        job = await job_search_service.get_job_details(job_id, "unknown")
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Get resume
        resume = await resume_service.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")
        
        # Validate application data
        validation = await application_service.validate_application_data(
            job=job,
            resume=resume,
            cover_letter=cover_letter
        )
        
        logger.info(f"Application validation completed: valid={validation.get('valid')}")
        return validation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating application data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/platforms", response_model=List[str])
async def get_supported_platforms() -> List[str]:
    """
    Get list of platforms that support automated applications.
    
    Returns:
        List of supported platform names
    """
    try:
        logger.info("Getting supported application platforms")
        
        # Get application service
        application_service = await service_registry.get_job_application_service()
        
        # Get supported platforms
        platforms = await application_service.get_supported_platforms()
        
        logger.info(f"Retrieved {len(platforms)} supported platforms")
        return platforms
        
    except Exception as e:
        logger.error(f"Error getting supported platforms: {e}", exc_info=True)
        # Return fallback list
        return ["linkedin", "indeed", "glassdoor", "google_jobs", "zip_recruiter", "mock"]


@router.get("/health", response_model=Dict[str, Any])
async def get_application_service_health() -> Dict[str, Any]:
    """
    Check the health of the job application service.
    
    Returns:
        Service health information
    """
    try:
        logger.info("Checking job application service health")
        
        # Get application service
        application_service = await service_registry.get_job_application_service()
        
        # Get health status
        health = await application_service.health_check()
        
        logger.info(f"Application service health: {health.get('status')}")
        return health
        
    except Exception as e:
        logger.error(f"Error checking application service health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to check application service health: {str(e)}")


@router.post("/bulk-apply", response_model=Dict[str, Any])
async def bulk_apply_to_jobs(
    job_ids: List[str] = Form(...),
    resume_id: str = Form(...),
    cover_letter_template: str = Form(...),
    customizations: Optional[str] = Form(None),
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Apply to multiple jobs using a template cover letter.
    
    Args:
        job_ids: List of job IDs to apply to
        resume_id: ID of the resume to submit
        cover_letter_template: Template cover letter text
        customizations: Job-specific customizations as JSON string
        
    Returns:
        Bulk application results
    """
    try:
        logger.info(f"Bulk application request: {len(job_ids)} jobs, resume_id={resume_id}")
        
        # Get required services
        job_search_service = await service_registry.get_job_search_service()
        resume_service = await service_registry.get_resume_service()
        application_service = await service_registry.get_job_application_service()
        
        # Get resume
        resume = await resume_service.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")
        
        # Parse customizations
        parsed_customizations = {}
        if customizations:
            try:
                import json
                parsed_customizations = json.loads(customizations)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in customizations: {customizations}")
        
        # Process each job
        results = []
        successful_applications = 0
        failed_applications = 0
        
        for job_id in job_ids:
            try:
                # Get job details
                job = await job_search_service.get_job_details(job_id, "unknown")
                if not job:
                    results.append({
                        "job_id": job_id,
                        "success": False,
                        "error": "Job not found"
                    })
                    failed_applications += 1
                    continue
                
                # Customize cover letter
                cover_letter = cover_letter_template
                if job_id in parsed_customizations:
                    job_customization = parsed_customizations[job_id]
                    cover_letter = cover_letter.replace("{company}", job.company)
                    cover_letter = cover_letter.replace("{position}", job.title)
                    cover_letter = cover_letter.replace("{customization}", job_customization)
                
                # Apply to job
                result = await application_service.apply_to_job(
                    job=job,
                    resume=resume,
                    cover_letter=cover_letter
                )
                
                if result.get("success"):
                    successful_applications += 1
                else:
                    failed_applications += 1
                
                results.append({
                    "job_id": job_id,
                    "company": job.company,
                    "position": job.title,
                    **result
                })
                
            except Exception as e:
                logger.error(f"Error applying to job {job_id}: {e}")
                results.append({
                    "job_id": job_id,
                    "success": False,
                    "error": str(e)
                })
                failed_applications += 1
        
        # Prepare response
        response_data = {
            "total_jobs": len(job_ids),
            "successful_applications": successful_applications,
            "failed_applications": failed_applications,
            "results": results
        }
        
        logger.info(f"Bulk application completed: {successful_applications} successful, {failed_applications} failed")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Bulk application failed: {str(e)}")
