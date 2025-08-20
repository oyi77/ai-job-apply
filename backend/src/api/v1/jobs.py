"""Jobs API endpoints for the AI Job Application Assistant."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ...models.job import JobSearchRequest, JobSearchResponse, Job
from ...utils.logger import get_logger
from ...services.service_registry import service_registry

logger = get_logger(__name__)

router = APIRouter()


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest) -> JobSearchResponse:
    """
    Search for jobs across multiple portals.
    
    Args:
        request: Job search request parameters
        
    Returns:
        Job search results grouped by portal
    """
    try:
        logger.info(f"Job search request: {request.keywords} in {request.location}")
        
        # Get job search service from unified registry
        job_search_service = await service_registry.get_job_search_service()
        
        # Use the real job search service
        response = await job_search_service.search_jobs(request)
        
        logger.info(f"Found {response.total_jobs} jobs across {len(response.jobs)} sites")
        return response
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")


@router.get("/sites", response_model=List[str])
async def get_available_sites() -> List[str]:
    """
    Get list of available job search sites.
    
    Returns:
        List of available job search sites
    """
    try:
        # Get job search service from unified registry
        job_search_service = await service_registry.get_job_search_service()
        
        # Use the real job search service
        return job_search_service.get_available_sites()
        
    except Exception as e:
        logger.error(f"Error getting available sites: {e}", exc_info=True)
        # Fallback to hardcoded list
        return ["indeed", "linkedin", "glassdoor", "ziprecruiter", "google_jobs"]


@router.get("/{job_id}", response_model=Job)
async def get_job_details(job_id: str) -> Job:
    """
    Get detailed job information by ID.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Detailed job information
    """
    try:
        # Get job search service from unified registry
        job_search_service = await service_registry.get_job_search_service()
        
        # Extract platform from job_id (assuming format: platform_jobid)
        if "_" in job_id:
            platform, actual_job_id = job_id.split("_", 1)
        else:
            platform = "unknown"
            actual_job_id = job_id
        
        # Use the real job search service
        job = await job_search_service.get_job_details(actual_job_id, platform)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return job
        
    except Exception as e:
        logger.error(f"Error getting job details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get job details: {str(e)}")


def _generate_mock_jobs(request: JobSearchRequest) -> Dict[str, List[Job]]:
    """Generate mock job data for testing."""
    from datetime import datetime
    
    mock_jobs = {}
    sites = ["indeed", "linkedin", "glassdoor"]
    
    for site in sites:
        site_jobs = []
        for i in range(3):  # 3 jobs per site
            job = Job(
                title=f"{' '.join(request.keywords).title()} Developer",
                company=f"TechCorp {i+1}",
                location=request.location,
                url=f"https://{site}.com/jobs/{i+1}",
                portal=site,
                description=f"Exciting opportunity for a {' '.join(request.keywords)} professional.",
                salary="$60,000 - $120,000",
                posted_date="2 days ago",
                experience_level=request.experience_level,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            site_jobs.append(job)
        
        mock_jobs[site] = site_jobs
    
    return mock_jobs
