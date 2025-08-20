"""AI service API endpoints for the AI Job Application Assistant."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime
from ...models.resume import Resume, ResumeOptimizationRequest, ResumeOptimizationResponse
from ...models.cover_letter import CoverLetterRequest, CoverLetter
from ...utils.logger import get_logger
from ...services.service_registry import service_registry
from ...services.database_service_registry import database_service_registry

logger = get_logger(__name__)

router = APIRouter()


@router.post("/optimize-resume", response_model=ResumeOptimizationResponse)
async def optimize_resume(request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
    """
    Optimize resume for a specific job.
    
    Args:
        request: Resume optimization request
        
    Returns:
        Resume optimization results
    """
    try:
        logger.info(f"Resume optimization request for {request.target_role} at {request.company_name}")
        
        # Get AI service from registry
        # Try database service registry first, fallback to in-memory
        try:
            ai_service = database_service_registry.get_ai_service()
        except RuntimeError:
            ai_service = service_registry.get_ai_service()
        
        # Use the real AI service for optimization
        response = await ai_service.optimize_resume(request)
        
        logger.info("Resume optimization completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error optimizing resume: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Resume optimization failed: {str(e)}")


@router.post("/generate-cover-letter", response_model=CoverLetter)
async def generate_cover_letter(request: CoverLetterRequest) -> CoverLetter:
    """
    Generate a personalized cover letter.
    
    Args:
        request: Cover letter generation request
        
    Returns:
        Generated cover letter
    """
    try:
        logger.info(f"Cover letter generation request for {request.job_title} at {request.company_name}")
        
        # Get AI service from registry
        # Try database service registry first, fallback to in-memory
        try:
            ai_service = database_service_registry.get_ai_service()
        except RuntimeError:
            ai_service = service_registry.get_ai_service()
        
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
    job_description: str
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
        
        # Get AI service from registry
        # Try database service registry first, fallback to in-memory
        try:
            ai_service = database_service_registry.get_ai_service()
        except RuntimeError:
            ai_service = service_registry.get_ai_service()
        
        # Use the real AI service for job match analysis
        analysis = await ai_service.analyze_job_match(resume_content, job_description)
        
        logger.info("Job match analysis completed successfully")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing job match: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Job match analysis failed: {str(e)}")


@router.post("/extract-skills")
async def extract_resume_skills(resume_content: str) -> Dict[str, Any]:
    """
    Extract skills from resume content.
    
    Args:
        resume_content: Resume text content
        
    Returns:
        Extracted skills and analysis
    """
    try:
        logger.info("Skills extraction request received")
        
        # Get AI service from registry
        # Try database service registry first, fallback to in-memory
        try:
            ai_service = database_service_registry.get_ai_service()
        except RuntimeError:
            ai_service = service_registry.get_ai_service()
        
        # Use the real AI service for skills extraction
        skills = await ai_service.extract_resume_skills(resume_content)
        
        # Return in expected format
        skills_analysis = {
            "technical_skills": [s for s in skills if s.lower() in ['python', 'javascript', 'java', 'sql', 'git', 'docker', 'aws', 'react', 'node.js']],
            "soft_skills": [s for s in skills if s.lower() in ['leadership', 'communication', 'problem solving', 'teamwork']],
            "tools": [s for s in skills if s.lower() in ['vs code', 'docker', 'aws', 'git', 'jenkins']],
            "all_skills": skills,
            "confidence": 0.89
        }
        
        logger.info("Skills extraction completed successfully")
        return skills_analysis
        
    except Exception as e:
        logger.error(f"Error extracting skills: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Skills extraction failed: {str(e)}")


@router.post("/suggest-improvements")
async def suggest_resume_improvements(
    resume_content: str,
    job_description: str
) -> Dict[str, Any]:
    """
    Suggest improvements for a resume based on job description.
    
    Args:
        resume_content: Resume text content
        job_description: Job description text
        
    Returns:
        Improvement suggestions
    """
    try:
        logger.info("Resume improvement suggestions request received")
        
        # Get AI service from registry
        # Try database service registry first, fallback to in-memory
        try:
            ai_service = database_service_registry.get_ai_service()
        except RuntimeError:
            ai_service = service_registry.get_ai_service()
        
        # Use the real AI service for improvement suggestions
        improvements = await ai_service.suggest_resume_improvements(resume_content, job_description)
        
        # Return in expected format
        suggestions = {
            "content_improvements": improvements[:3] if len(improvements) > 3 else improvements,
            "format_improvements": [
                "Use consistent bullet point formatting",
                "Improve section organization",
                "Add a professional summary section"
            ],
            "keyword_optimization": improvements[3:6] if len(improvements) > 6 else improvements[3:],
            "all_suggestions": improvements,
            "priority": "high",
            "estimated_impact": 0.25
        }
        
        logger.info("Improvement suggestions generated successfully")
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating improvement suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Improvement suggestions failed: {str(e)}")


@router.get("/health")
async def ai_service_health() -> Dict[str, Any]:
    """
    Check AI service health status.
    
    Returns:
        Service health information
    """
    try:
        # Get AI service from registry
        # Try database service registry first, fallback to in-memory
        try:
            ai_service = database_service_registry.get_ai_service()
        except RuntimeError:
            ai_service = service_registry.get_ai_service()
        
        # Check if AI service is available
        is_available = await ai_service.is_available()
        
        health_status = {
            "status": "healthy" if is_available else "degraded",
            "service": "AI Job Application Assistant",
            "ai_provider": "Google Gemini",
            "model": "gemini-1.5-flash",
            "available": is_available,
            "response_time": "fast",
            "last_check": datetime.utcnow().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error checking AI service health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
