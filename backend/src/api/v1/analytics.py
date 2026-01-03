"""Analytics API endpoints for advanced reporting and insights."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
from loguru import logger
import io

from src.api.dependencies import get_current_user
from src.models.user import User
from src.services.analytics_service import AnalyticsService
from src.services.analytics_exporter import AnalyticsExporter
from src.services.analytics_insights_service import AnalyticsInsightsService
from src.services.ai_service import ModernAIService
from src.services.service_registry import service_registry

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/metrics/success-rate")
async def get_success_rate_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    current_user: User = Depends(get_current_user)
):
    """
    Get application success rate metrics.
    
    Returns:
        Success rate, interview rate, rejection rate, and status breakdown
    """
    try:
        # Get analytics service
        analytics_service = AnalyticsService(
            repository=await service_registry.get_application_repository()
        )
        
        metrics = await analytics_service.get_application_success_rate(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {"data": metrics}
        
    except Exception as e:
        logger.error(f"Error getting success rate metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve success rate metrics"
        )


@router.get("/metrics/response-time")
async def get_response_time_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    Get response time analysis metrics.
    
    Returns:
        Average response times, fastest/slowest responses
    """
    try:
        analytics_service = AnalyticsService(
            repository=await service_registry.get_application_repository()
        )
        
        metrics = await analytics_service.get_response_time_analysis(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {"data": metrics}
        
    except Exception as e:
        logger.error(f"Error getting response time metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve response time metrics"
        )


@router.get("/metrics/interview-performance")
async def get_interview_performance_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    Get interview performance metrics.
    
    Returns:
        Interview counts, offer rates, conversion metrics
    """
    try:
        analytics_service = AnalyticsService(
            repository=await service_registry.get_application_repository()
        )
        
        metrics = await analytics_service.get_interview_performance(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {"data": metrics}
        
    except Exception as e:
        logger.error(f"Error getting interview performance metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview performance metrics"
        )


@router.get("/trends")
async def get_trend_analysis(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """
    Get trend analysis over time.
    
    Returns:
        Weekly trends, application patterns
    """
    try:
        analytics_service = AnalyticsService(
            repository=await service_registry.get_application_repository()
        )
        
        trends = await analytics_service.get_trend_analysis(
            user_id=current_user.id,
            days=days
        )
        
        return {"data": trends}
        
    except Exception as e:
        logger.error(f"Error getting trend analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trend analysis"
        )


@router.get("/insights/skills-gap")
async def get_skills_gap_analysis(
    current_user: User = Depends(get_current_user)
):
    """
    Get skills gap analysis.
    
    Returns:
        Most requested skills, skill frequency
    """
    try:
        analytics_service = AnalyticsService(
            repository=await service_registry.get_application_repository()
        )
        
        analysis = await analytics_service.get_skills_gap_analysis(
            user_id=current_user.id
        )
        
        return {"data": analysis}
        
    except Exception as e:
        logger.error(f"Error getting skills gap analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve skills gap analysis"
        )


@router.get("/insights/companies")
async def get_company_analysis(
    current_user: User = Depends(get_current_user)
):
    """
    Get company analysis.
    
    Returns:
        Application statistics by company
    """
    try:
        analytics_service = AnalyticsService(
            repository=await service_registry.get_application_repository()
        )
        
        analysis = await analytics_service.get_company_analysis(
            user_id=current_user.id
        )
        
        return {"data": analysis}
        
    except Exception as e:
        logger.error(f"Error getting company analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company analysis"
        )


@router.get("/dashboard")
async def get_analytics_dashboard(
    days: int = Query(30, description="Number of days for trends"),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive analytics dashboard data.
    
    Returns all analytics in one call for dashboard display.
    """
    try:
        analytics_service = AnalyticsService(
            repository=await service_registry.get_application_repository()
        )
        
        # Get all analytics concurrently would be ideal, but for simplicity doing sequentially
        success_rate = await analytics_service.get_application_success_rate(user_id=current_user.id)
        response_time = await analytics_service.get_response_time_analysis(user_id=current_user.id)
        interview_perf = await analytics_service.get_interview_performance(user_id=current_user.id)
        trends = await analytics_service.get_trend_analysis(user_id=current_user.id, days=days)
        skills_gap = await analytics_service.get_skills_gap_analysis(user_id=current_user.id)
        companies = await analytics_service.get_company_analysis(user_id=current_user.id)
        
        return {
            "data": {
                "success_metrics": success_rate,
                "response_time_metrics": response_time,
                "interview_metrics": interview_perf,
                "trends": trends,
                "skills_gap": skills_gap,
                "companies": companies
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics dashboard"
        )
