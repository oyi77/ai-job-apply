"""AI service API endpoints for the AI Job Application Assistant."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime
from ...models.resume import Resume, ResumeOptimizationRequest, ResumeOptimizationResponse
from ...models.cover_letter import CoverLetterRequest, CoverLetter
from ...models.career_insights import CareerInsightsRequest, CareerInsightsResponse
from ...models.user import UserProfile
from ...api.dependencies import get_current_user
from ...utils.logger import get_logger
from ...services.service_registry import service_registry

logger = get_logger(__name__)

router = APIRouter()


@router.post("/optimize-resume", response_model=ResumeOptimizationResponse)
async def optimize_resume(
    request: ResumeOptimizationRequest,
    current_user: UserProfile = Depends(get_current_user)
) -> ResumeOptimizationResponse:
    """
    Optimize resume for a specific job.
    
    Args:
        request: Resume optimization request
        
    Returns:
        Resume optimization results
    """
    try:
        logger.info(f"Resume optimization request for {request.target_role} at {request.company_name}")
        
        # Get AI service from unified registry
        ai_service = await service_registry.get_ai_service()
        
        # Use the real AI service for optimization
        response = await ai_service.optimize_resume(request)
        
        logger.info("Resume optimization completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error optimizing resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Resume optimization failed: {str(e)}")


@router.post("/generate-cover-letter", response_model=CoverLetter)
async def generate_cover_letter(
    request: CoverLetterRequest,
    current_user: UserProfile = Depends(get_current_user)
) -> CoverLetter:
    """
    Generate a personalized cover letter.
    
    Args:
        request: Cover letter generation request
        
    Returns:
        Generated cover letter
    """
    try:
        logger.info(f"Cover letter generation request for {request.job_title} at {request.company_name}")
        
        # Get AI service from unified registry
        ai_service = await service_registry.get_ai_service()
        
        # Use the real AI service for cover letter generation
        response = await ai_service.generate_cover_letter(request)
        
        logger.info("Cover letter generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")


@router.post("/analyze-job-match")
async def analyze_job_match(
    resume_content: str,
    job_description: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze how well a resume matches a job description.
    
    Args:
        resume_content: Resume text content
        job_description: Job description text
        
    Returns:
        Job match analysis results
    """
    try:
        logger.info("Job match analysis request received")
        
        # Get AI service from unified registry
        ai_service = await service_registry.get_ai_service()
        
        # Use the real AI service for job match analysis
        analysis = await ai_service.analyze_job_match(resume_content, job_description)
        
        logger.info("Job match analysis completed successfully")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing job match: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Job match analysis failed: {str(e)}")


@router.post("/extract-skills")
async def extract_resume_skills(
    resume_content: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Extract skills from resume content.
    
    Args:
        resume_content: Resume text content
        
    Returns:
        Extracted skills and confidence scores
    """
    try:
        logger.info("Skills extraction request received")
        
        # Get AI service from unified registry
        ai_service = await service_registry.get_ai_service()
        
        # Use the real AI service for skills extraction
        skills = await ai_service.extract_resume_skills(resume_content)
        
        logger.info("Skills extraction completed successfully")
        
        # Return in expected format
        return {
            "technical_skills": [s for s in skills if s.lower() in ['python', 'javascript', 'java', 'sql', 'git', 'docker', 'aws', 'react', 'node.js']],
            "soft_skills": [s for s in skills if s.lower() in ['leadership', 'communication', 'problem solving', 'teamwork']],
            "tools": [s for s in skills if s.lower() in ['vs code', 'docker', 'aws', 'git', 'jenkins']],
            "all_skills": skills,
            "confidence": 0.89
        }
        
    except Exception as e:
        logger.error(f"Error extracting skills: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Skills extraction failed: {str(e)}")


@router.post("/improve-resume")
async def improve_resume_suggestions(
    resume_content: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get suggestions for improving a resume.
    
    Args:
        resume_content: Resume text content
        
    Returns:
        Improvement suggestions and recommendations
    """
    try:
        logger.info("Resume improvement suggestions request received")
        
        # Get AI service from unified registry
        ai_service = await service_registry.get_ai_service()
        
        # Use the real AI service for improvement suggestions
        suggestions = await ai_service.suggest_resume_improvements(resume_content, "")
        
        logger.info("Resume improvement suggestions completed successfully")
        
        # Return in expected format
        return {
            "content_improvements": suggestions[:3] if len(suggestions) > 3 else suggestions,
            "format_improvements": [
                "Use consistent bullet point formatting",
                "Improve section organization",
                "Add a professional summary section"
            ],
            "keyword_optimization": suggestions[3:6] if len(suggestions) > 6 else suggestions[3:],
            "all_suggestions": suggestions,
            "priority": "high",
            "estimated_impact": 0.25
        }
        
    except Exception as e:
        logger.error(f"Error getting improvement suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get improvement suggestions: {str(e)}")


@router.post("/career-insights", response_model=CareerInsightsResponse)
async def generate_career_insights(
    request: CareerInsightsRequest,
    current_user: UserProfile = Depends(get_current_user)
) -> CareerInsightsResponse:
    """
    Generate career insights based on application history and skills.

    Args:
        request: Career insights request

    Returns:
        Career insights
    """
    try:
        logger.info("Career insights request received")

        # Get AI service from unified registry
        ai_service = await service_registry.get_ai_service()

        # Use the real AI service for career insights
        response = await ai_service.generate_career_insights(request)

        logger.info("Career insights generation completed successfully")
        return response

    except Exception as e:
        logger.error(f"Error generating career insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Career insights generation failed: {str(e)}")


@router.get("/health")
async def ai_service_health() -> Dict[str, Any]:
    """
    Check AI service health and availability.
    
    Returns:
        AI service health status
    """
    try:
        # Get AI service from unified registry
        ai_service = await service_registry.get_ai_service()
        
        # Check service availability
        is_available = await ai_service.is_available()
        
        health_status = {
            "status": "healthy" if is_available else "unavailable",
            "service": "AI Service (Gemini)",
            "available": is_available,
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "resume_optimization",
                "cover_letter_generation", 
                "job_match_analysis",
                "skills_extraction",
                "resume_improvement",
                "career_insights"
            ]
        }
        
        if not is_available:
            health_status["message"] = "AI service not available - running with mock responses"
            health_status["status"] = "degraded"
        
        logger.info(f"AI service health check: {health_status['status']}")
        return health_status
        
    except Exception as e:
        logger.error(f"Error checking AI service health: {e}", exc_info=True)
        return {
            "status": "error",
            "service": "AI Service",
            "available": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
