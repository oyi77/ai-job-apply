"""
Tests for Analytics Service
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, AsyncMock

from src.services.analytics_service import AnalyticsService
from src.models.application import ApplicationStatus


@pytest.fixture
def mock_repository():
    """Create a mock application repository."""
    return Mock()


@pytest.fixture
def analytics_service(mock_repository):
    """Create analytics service with mock repository."""
    return AnalyticsService(repository=mock_repository)


@pytest.mark.asyncio
async def test_success_rate_calculation(analytics_service, mock_repository):
    """Test application success rate calculation."""
    # Mock applications
    now = datetime.now(timezone.utc)
    mock_apps = [
        Mock(status=ApplicationStatus.OFFER_RECEIVED, created_at=now),
        Mock(status=ApplicationStatus.ACCEPTED, created_at=now),
        Mock(status=ApplicationStatus.REJECTED, created_at=now),
        Mock(status=ApplicationStatus.APPLIED, created_at=now),
        Mock(status=ApplicationStatus.INTERVIEW_SCHEDULED, created_at=now),
    ]
    
    mock_repository.get_all = AsyncMock(return_value=mock_apps)
    
    # Get success rate
    result = await analytics_service.get_application_success_rate(user_id="test_user")
    
    # Assertions
    assert result["total_applications"] == 5
    assert result["successful_applications"] == 2
    assert result["success_rate"] == 40.0  # 2/5 * 100
    assert result["interview_rate"] == 60.0  # 3/5 * 100 (includes offers)


@pytest.mark.asyncio
async def test_response_time_analysis(analytics_service, mock_repository):
    """Test response time analysis."""
    now = datetime.now(timezone.utc)
    
    # Mock applications with different response times
    mock_apps = [
        Mock(
            status=ApplicationStatus.UNDER_REVIEW,
            created_at=now - timedelta(days=5),
            updated_at=now
        ),
        Mock(
            status=ApplicationStatus.INTERVIEW_SCHEDULED,
            created_at=now - timedelta(days=10),
            updated_at=now
        ),
        Mock(
            status=ApplicationStatus.APPLIED,
            created_at=now - timedelta(days=3),
            updated_at=now
        ),
    ]
    
    mock_repository.get_all = AsyncMock(return_value=mock_apps)
    
    # Get response time analysis
    result = await analytics_service.get_response_time_analysis(user_id="test_user")
    
    # Assertions
    assert result["total_responses"] == 2  # Excludes APPLIED status
    assert result["avg_response_time_days"] == 7.5  # (5 + 10) / 2
    assert result["fastest_response_days"] == 5
    assert result["slowest_response_days"] == 10


@pytest.mark.asyncio
async def test_interview_performance(analytics_service, mock_repository):
    """Test interview performance tracking."""
    now = datetime.now(timezone.utc)
    
    mock_apps = [
        Mock(status=ApplicationStatus.INTERVIEW_SCHEDULED, created_at=now),
        Mock(status=ApplicationStatus.INTERVIEWING, created_at=now),
        Mock(status=ApplicationStatus.OFFER_RECEIVED, created_at=now),
        Mock(status=ApplicationStatus.ACCEPTED, created_at=now),
        Mock(status=ApplicationStatus.REJECTED, created_at=now),
    ]
    
    mock_repository.get_all = AsyncMock(return_value=mock_apps)
    
    # Get interview performance
    result = await analytics_service.get_interview_performance(user_id="test_user")
    
    # Assertions
    assert result["total_interviews"] == 4  # Excludes final REJECTED
    assert result["offers_received"] == 2
    assert result["interview_to_offer_rate"] == 50.0  # 2/4 * 100


@pytest.mark.asyncio
async def test_company_analysis(analytics_service, mock_repository):
    """Test company analysis."""
    now = datetime.now(timezone.utc)
    
    mock_apps = [
        Mock(company_name="Company A", status=ApplicationStatus.OFFER_RECEIVED, created_at=now),
        Mock(company_name="Company A", status=ApplicationStatus.REJECTED, created_at=now),
        Mock(company_name="Company B", status=ApplicationStatus.APPLIED, created_at=now),
        Mock(company_name="Company B", status=ApplicationStatus.INTERVIEW_SCHEDULED, created_at=now),
    ]
    
    mock_repository.get_all = AsyncMock(return_value=mock_apps)
    
    # Get company analysis
    result = await analytics_service.get_company_analysis(user_id="test_user")
    
    # Assertions
    assert result["total_companies"] == 2
    assert len(result["companies"]) == 2
    
    # Check Company A stats
    company_a = next(c for c in result["companies"] if c["company"] == "Company A")
    assert company_a["total"] == 2
    assert company_a["offers"] == 1
    assert company_a["rejections"] == 1
    assert company_a["success_rate"] == 50.0


@pytest.mark.asyncio
async def test_empty_applications(analytics_service, mock_repository):
    """Test analytics with no applications."""
    mock_repository.get_all = AsyncMock(return_value=[])
    
    # Get success rate with empty data
    result = await analytics_service.get_application_success_rate(user_id="test_user")
    
    # Assertions
    assert result["total_applications"] == 0
    assert result["success_rate"] == 0.0
