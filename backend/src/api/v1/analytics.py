"""Analytics API endpoints for advanced reporting and insights."""

import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Any, Dict, Optional
from loguru import logger

from src.api.dependencies import get_current_user
from src.database.config import database_config
from src.database.models import DBJobApplication
from src.database.repositories.application_repository import ApplicationRepository
from src.models.user import User
from src.services.analytics_service import AnalyticsService
from src.services.cache_service import analytics_cache_service
from src.services.service_registry import service_registry
from sqlalchemy import func, select

router = APIRouter(prefix="/analytics", tags=["analytics"])


DASHBOARD_TTL_SECONDS = 60
SUCCESS_RATE_TTL_SECONDS = 120
RESPONSE_TIME_TTL_SECONDS = 120
INTERVIEW_PERFORMANCE_TTL_SECONDS = 120
TRENDS_TTL_SECONDS = 300
SKILLS_GAP_TTL_SECONDS = 60  # AI output varies; keep short
COMPANIES_TTL_SECONDS = 300


def _analytics_cache_key(user_id: str, endpoint: str) -> str:
    return f"analytics:{user_id}:{endpoint}"


async def _get_user_applications(user_id: str):
    async with database_config.get_session() as session:
        repository = ApplicationRepository(session)
        return await repository.get_all(user_id=user_id)


async def _get_applications_cache_buster(user_id: str) -> str:
    """Return a cheap "version" that changes when applications change."""

    async with database_config.get_session() as session:
        stmt = select(
            func.count(DBJobApplication.id),
            func.max(DBJobApplication.updated_at),
        ).where(DBJobApplication.user_id == user_id)
        result = await session.execute(stmt)
        count, max_updated_at = result.one()
        max_updated_str = max_updated_at.isoformat() if max_updated_at else "none"
        return f"{count}:{max_updated_str}"


@router.get("/metrics/success-rate")
async def get_success_rate_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    current_user: User = Depends(get_current_user),
):
    """
    Get application success rate metrics.

    Returns:
        Success rate, interview rate, rejection rate, and status breakdown
    """
    try:
        buster = await _get_applications_cache_buster(current_user.id)
        cache_key = _analytics_cache_key(
            current_user.id,
            (
                "success_rate:"
                f"{start_date.isoformat() if start_date else 'none'}:"
                f"{end_date.isoformat() if end_date else 'none'}:v{buster}"
            ),
        )
        cached = await analytics_cache_service.get(cache_key)
        if cached is not None:
            return {"data": cached}

        applications = await _get_user_applications(current_user.id)
        analytics_service = AnalyticsService()
        metrics = await analytics_service.get_application_success_rate(
            user_id=current_user.id,
            applications=applications,
            start_date=start_date,
            end_date=end_date,
        )

        await analytics_cache_service.set(
            cache_key, metrics, ttl_seconds=SUCCESS_RATE_TTL_SECONDS
        )
        return {"data": metrics}

    except Exception as e:
        logger.error(f"Error getting success rate metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve success rate metrics",
        )


@router.get("/metrics/response-time")
async def get_response_time_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """
    Get response time analysis metrics.

    Returns:
        Average response times, fastest/slowest responses
    """
    try:
        buster = await _get_applications_cache_buster(current_user.id)
        cache_key = _analytics_cache_key(
            current_user.id,
            (
                "response_time:"
                f"{start_date.isoformat() if start_date else 'none'}:"
                f"{end_date.isoformat() if end_date else 'none'}:v{buster}"
            ),
        )
        cached = await analytics_cache_service.get(cache_key)
        if cached is not None:
            return {"data": cached}

        applications = await _get_user_applications(current_user.id)
        analytics_service = AnalyticsService()
        metrics = await analytics_service.get_response_time_analysis(
            user_id=current_user.id,
            applications=applications,
            start_date=start_date,
            end_date=end_date,
        )
        await analytics_cache_service.set(
            cache_key, metrics, ttl_seconds=RESPONSE_TIME_TTL_SECONDS
        )
        return {"data": metrics}

    except Exception as e:
        logger.error(f"Error getting response time metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve response time metrics",
        )


@router.get("/metrics/interview-performance")
async def get_interview_performance_metrics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """
    Get interview performance metrics.

    Returns:
        Interview counts, offer rates, conversion metrics
    """
    try:
        buster = await _get_applications_cache_buster(current_user.id)
        cache_key = _analytics_cache_key(
            current_user.id,
            (
                "interview_performance:"
                f"{start_date.isoformat() if start_date else 'none'}:"
                f"{end_date.isoformat() if end_date else 'none'}:v{buster}"
            ),
        )
        cached = await analytics_cache_service.get(cache_key)
        if cached is not None:
            return {"data": cached}

        applications = await _get_user_applications(current_user.id)
        analytics_service = AnalyticsService()
        metrics = await analytics_service.get_interview_performance(
            user_id=current_user.id,
            applications=applications,
            start_date=start_date,
            end_date=end_date,
        )
        await analytics_cache_service.set(
            cache_key, metrics, ttl_seconds=INTERVIEW_PERFORMANCE_TTL_SECONDS
        )
        return {"data": metrics}

    except Exception as e:
        logger.error(f"Error getting interview performance metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview performance metrics",
        )


@router.get("/trends")
async def get_trend_analysis(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
):
    """
    Get trend analysis over time.

    Returns:
        Weekly trends, application patterns
    """
    try:
        buster = await _get_applications_cache_buster(current_user.id)
        cache_key = _analytics_cache_key(current_user.id, f"trends:{days}:v{buster}")
        cached = await analytics_cache_service.get(cache_key)
        if cached is not None:
            return {"data": cached}

        applications = await _get_user_applications(current_user.id)
        analytics_service = AnalyticsService()
        trends = await analytics_service.get_trend_analysis(
            user_id=current_user.id, days=days, applications=applications
        )
        await analytics_cache_service.set(cache_key, trends, ttl_seconds=TRENDS_TTL_SECONDS)
        return {"data": trends}

    except Exception as e:
        logger.error(f"Error getting trend analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trend analysis",
        )


@router.get("/insights/skills-gap")
async def get_skills_gap_analysis(current_user: User = Depends(get_current_user)):
    """
    Get AI-powered skills gap analysis.

    Returns:
        Most requested skills, skill frequency, AI-powered recommendations
    """
    try:
        buster = await _get_applications_cache_buster(current_user.id)
        cache_key = _analytics_cache_key(current_user.id, f"skills_gap:v{buster}")
        cached = await analytics_cache_service.get(cache_key)
        if cached is not None:
            return {"data": cached}

        ai_service = await service_registry.get_ai_service()
        applications = await _get_user_applications(current_user.id)
        analytics_service = AnalyticsService(ai_service=ai_service)

        analysis = await analytics_service.get_skills_gap_analysis(
            user_id=current_user.id, applications=applications
        )

        await analytics_cache_service.set(
            cache_key, analysis, ttl_seconds=SKILLS_GAP_TTL_SECONDS
        )
        return {"data": analysis}

    except Exception as e:
        logger.error(f"Error getting skills gap analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve skills gap analysis",
        )


@router.get("/insights/companies")
async def get_company_analysis(current_user: User = Depends(get_current_user)):
    """
    Get company analysis.

    Returns:
        Application statistics by company
    """
    try:
        buster = await _get_applications_cache_buster(current_user.id)
        cache_key = _analytics_cache_key(current_user.id, f"companies:v{buster}")
        cached = await analytics_cache_service.get(cache_key)
        if cached is not None:
            return {"data": cached}

        applications = await _get_user_applications(current_user.id)
        analytics_service = AnalyticsService()
        analysis = await analytics_service.get_company_analysis(
            user_id=current_user.id, applications=applications
        )
        await analytics_cache_service.set(
            cache_key, analysis, ttl_seconds=COMPANIES_TTL_SECONDS
        )
        return {"data": analysis}

    except Exception as e:
        logger.error(f"Error getting company analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company analysis",
        )


@router.get("/dashboard")
async def get_analytics_dashboard(
    days: int = Query(30, description="Number of days for trends"),
    current_user: User = Depends(get_current_user),
):
    """
    Get comprehensive analytics dashboard data with AI-powered insights.

    Returns all analytics in one call for dashboard display.
    """
    try:
        buster = await _get_applications_cache_buster(current_user.id)
        dashboard_cache_key = _analytics_cache_key(
            current_user.id, f"dashboard:{days}:v{buster}"
        )
        cached = await analytics_cache_service.get(dashboard_cache_key)
        if cached is not None:
            return {"data": cached}

        ai_service = await service_registry.get_ai_service()
        applications = await _get_user_applications(current_user.id)
        analytics_service = AnalyticsService(ai_service=ai_service)

        success_rate_coro = analytics_service.get_application_success_rate(
            user_id=current_user.id, applications=applications
        )
        response_time_coro = analytics_service.get_response_time_analysis(
            user_id=current_user.id, applications=applications
        )
        interview_perf_coro = analytics_service.get_interview_performance(
            user_id=current_user.id, applications=applications
        )
        trends_coro = analytics_service.get_trend_analysis(
            user_id=current_user.id, days=days, applications=applications
        )

        skills_gap_cache_key = _analytics_cache_key(current_user.id, f"skills_gap:v{buster}")
        companies_cache_key = _analytics_cache_key(current_user.id, f"companies:v{buster}")

        async def skills_gap_task():
            cached_skills = await analytics_cache_service.get(skills_gap_cache_key)
            if cached_skills is not None:
                return cached_skills
            result = await analytics_service.get_skills_gap_analysis(
                user_id=current_user.id, applications=applications
            )
            await analytics_cache_service.set(
                skills_gap_cache_key, result, ttl_seconds=SKILLS_GAP_TTL_SECONDS
            )
            return result

        async def companies_task():
            cached_companies = await analytics_cache_service.get(companies_cache_key)
            if cached_companies is not None:
                return cached_companies
            result = await analytics_service.get_company_analysis(
                user_id=current_user.id, applications=applications
            )
            await analytics_cache_service.set(
                companies_cache_key, result, ttl_seconds=COMPANIES_TTL_SECONDS
            )
            return result

        (
            success_rate,
            response_time,
            interview_perf,
            trends,
            skills_gap,
            companies,
        ) = await asyncio.gather(
            success_rate_coro,
            response_time_coro,
            interview_perf_coro,
            trends_coro,
            skills_gap_task(),
            companies_task(),
        )

        ai_powered = (
            bool(skills_gap.get("ai_powered", False))
            if isinstance(skills_gap, dict)
            else False
        )

        dashboard_data: Dict[str, Any] = {
            "success_metrics": success_rate,
            "response_time_metrics": response_time,
            "interview_metrics": interview_perf,
            "trends": trends,
            "skills_gap": skills_gap,
            "companies": companies,
            "ai_powered": ai_powered,
        }

        await analytics_cache_service.set(
            dashboard_cache_key, dashboard_data, ttl_seconds=DASHBOARD_TTL_SECONDS
        )

        return {"data": dashboard_data}

    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics dashboard",
        )
