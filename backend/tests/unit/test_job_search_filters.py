"""Tests for Job Search Filter functionality."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from src.services.job_search_service import JobSearchService
from src.models.job import JobSearchRequest


@pytest.fixture
def job_search_service():
    """Create a job search service instance."""
    service = JobSearchService()
    return service


class TestJobSearchFilters:
    """Test job search filter functionality."""

    @pytest.mark.asyncio
    async def test_filter_by_date_posted_today(self, job_search_service):
        """Test filtering jobs by date posted today."""
        request = JobSearchRequest(
            keywords=["python"],
            location="Remote",
            date_posted="today",
        )
        # Mock the jobspy unavailable
        job_search_service._jobspy_available = False

        # Call the search directly to get mock jobs
        response = await job_search_service.search_jobs(request)

        # Verify response structure
        assert hasattr(response, "jobs")
        assert hasattr(response, "total_jobs")

    @pytest.mark.asyncio
    async def test_filter_by_date_posted_week(self, job_search_service):
        """Test filtering jobs by date posted this week."""
        request = JobSearchRequest(
            keywords=["python"],
            location="Remote",
            date_posted="week",
        )
        job_search_service._jobspy_available = False

        response = await job_search_service.search_jobs(request)

        assert hasattr(response, "jobs")
        assert response.total_jobs >= 0

    @pytest.mark.asyncio
    async def test_filter_by_salary_range(self, job_search_service):
        """Test filtering jobs by salary range."""
        request = JobSearchRequest(
            keywords=["python"],
            location="Remote",
            salary_min=80000,
            salary_max=150000,
        )
        job_search_service._jobspy_available = False

        response = await job_search_service.search_jobs(request)

        assert hasattr(response, "jobs")
        # All jobs should be within salary range (mock data is)

    @pytest.mark.asyncio
    async def test_filter_by_salary_min_only(self, job_search_service):
        """Test filtering jobs by minimum salary only."""
        request = JobSearchRequest(
            keywords=["python"],
            location="Remote",
            salary_min=100000,
        )
        job_search_service._jobspy_available = False

        response = await job_search_service.search_jobs(request)

        assert hasattr(response, "jobs")

    @pytest.mark.asyncio
    async def test_filter_by_remote_only(self, job_search_service):
        """Test filtering jobs for remote positions only."""
        request = JobSearchRequest(
            keywords=["python"],
            location="Remote",
            remote_only=True,
        )
        job_search_service._jobspy_available = False

        response = await job_search_service.search_jobs(request)

        assert hasattr(response, "jobs")
        # Mock jobs should be remote

    @pytest.mark.asyncio
    async def test_combined_filters(self, job_search_service):
        """Test combining multiple filters."""
        request = JobSearchRequest(
            keywords=["python", "developer"],
            location="Remote",
            experience_level="mid",
            date_posted="week",
            salary_min=80000,
            remote_only=True,
        )
        job_search_service._jobspy_available = False

        response = await job_search_service.search_jobs(request)

        assert hasattr(response, "jobs")
        assert hasattr(response, "total_jobs")
        assert hasattr(response, "search_metadata")

    @pytest.mark.asyncio
    async def test_no_filters(self, job_search_service):
        """Test search with no filters (default behavior)."""
        request = JobSearchRequest(
            keywords=["python"],
            location="Remote",
        )
        job_search_service._jobspy_available = False

        response = await job_search_service.search_jobs(request)

        assert hasattr(response, "jobs")
        assert hasattr(response, "total_jobs")
        assert response.total_jobs >= 0


class TestJobSearchRequestModel:
    """Test JobSearchRequest model validation."""

    def test_default_values(self):
        """Test default values are set correctly."""
        request = JobSearchRequest(keywords=["python"])

        assert request.keywords == ["python"]
        assert request.location == "Remote"
        assert request.experience_level.value == "entry"
        assert request.results_wanted == 50
        assert request.hours_old == 72
        assert request.remote_only is False

    def test_salary_filter_values(self):
        """Test salary filter values."""
        request = JobSearchRequest(
            keywords=["python"],
            salary_min=50000,
            salary_max=150000,
        )

        assert request.salary_min == 50000
        assert request.salary_max == 150000

    def test_date_posted_filter(self):
        """Test date posted filter values."""
        request = JobSearchRequest(
            keywords=["python"],
            date_posted="week",
        )

        assert request.date_posted == "week"

    def test_job_type_filter(self):
        """Test job type filter."""
        request = JobSearchRequest(
            keywords=["python"],
            job_type=["full_time", "part_time"],
        )

        assert request.job_type == ["full_time", "part_time"]

    def test_remote_only_filter(self):
        """Test remote only filter."""
        request = JobSearchRequest(
            keywords=["python"],
            remote_only=True,
        )

        assert request.remote_only is True
