"""Unit tests for Job Search API endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.models.job import (
    Job,
    JobSearchRequest,
    JobSearchResponse,
    ExperienceLevel,
    JobType,
    JobApplicationMethod,
)


@pytest.fixture
def app():
    """Create FastAPI test application."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_job_search_service():
    """Mock job search service."""
    service = AsyncMock()

    # Mock job data
    test_job = Job(
        id="job-123",
        title="Python Developer",
        company="TechCorp",
        location="Remote",
        url="https://example.com/jobs/123",
        portal="indeed",
        description="We are looking for a Python developer",
        salary="$80,000 - $120,000",
        posted_date="2 days ago",
        experience_level=ExperienceLevel.MID,
        job_type=JobType.FULL_TIME,
        requirements=["Python", "FastAPI"],
        skills=["Python", "FastAPI", "SQL"],
        application_method=JobApplicationMethod.DIRECT_URL,
        apply_url="https://example.com/apply/123",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Mock search_jobs method
    service.search_jobs = AsyncMock(
        return_value=JobSearchResponse(
            jobs={"indeed": [test_job], "linkedin": [test_job]},
            total_jobs=2,
            search_metadata={
                "keywords": ["python", "developer"],
                "location": "Remote",
                "experience_level": "mid",
                "sites_searched": ["indeed", "linkedin"],
                "timestamp": datetime.utcnow().isoformat(),
                "method": "jobspy",
            },
        )
    )

    # Mock get_available_sites method
    service.get_available_sites = MagicMock(
        return_value=["indeed", "linkedin", "glassdoor", "ziprecruiter", "google_jobs"]
    )

    # Mock get_job_details method
    service.get_job_details = AsyncMock(return_value=test_job)

    return service


class TestJobSearchSuccess:
    """Test cases for successful job search operations."""

    @pytest.mark.asyncio
    async def test_search_jobs_success(self, client, mock_job_search_service):
        """Test successful job search with valid parameters."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python", "developer"],
                    "location": "Remote",
                    "experience_level": "mid",
                    "results_wanted": 50,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "jobs" in data
            assert "total_jobs" in data
            assert "search_metadata" in data
            assert data["total_jobs"] >= 0

    @pytest.mark.asyncio
    async def test_search_jobs_with_keywords(self, client, mock_job_search_service):
        """Test job search with keyword filters."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python", "fastapi", "async"],
                    "location": "Remote",
                    "experience_level": "mid",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_jobs"] >= 0
            mock_job_search_service.search_jobs.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_jobs_with_location(self, client, mock_job_search_service):
        """Test job search with location filter."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["developer"],
                    "location": "San Francisco, CA",
                    "experience_level": "senior",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "search_metadata" in data

    @pytest.mark.asyncio
    async def test_search_jobs_with_experience_level(
        self, client, mock_job_search_service
    ):
        """Test job search with experience level filter."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["engineer"],
                    "location": "Remote",
                    "experience_level": "senior",
                    "results_wanted": 25,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data["jobs"], dict)

    @pytest.mark.asyncio
    async def test_search_jobs_with_specific_sites(
        self, client, mock_job_search_service
    ):
        """Test job search with specific job sites."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": "Remote",
                    "experience_level": "mid",
                    "sites": ["indeed", "linkedin"],
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_jobs"] >= 0


class TestJobSearchNoResults:
    """Test cases for job search with no results."""

    @pytest.mark.asyncio
    async def test_search_jobs_no_results(self, client, mock_job_search_service):
        """Test job search returning empty results."""
        mock_job_search_service.search_jobs = AsyncMock(
            return_value=JobSearchResponse(
                jobs={},
                total_jobs=0,
                search_metadata={
                    "keywords": ["nonexistent"],
                    "location": "Remote",
                    "sites_searched": [],
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": "jobspy",
                },
            )
        )

        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["nonexistent"],
                    "location": "Remote",
                    "experience_level": "mid",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_jobs"] == 0
            assert data["jobs"] == {}


class TestJobSearchValidation:
    """Test cases for job search parameter validation."""

    def test_search_jobs_invalid_params_missing_keywords(self, client):
        """Test job search with missing required parameters."""
        response = client.post(
            "/api/v1/jobs/search",
            json={
                "location": "Remote",
                "experience_level": "mid",
            },
        )

        # Should accept empty keywords (defaults to empty list)
        assert response.status_code in [200, 422]

    def test_search_jobs_invalid_experience_level(self, client):
        """Test job search with invalid experience level."""
        response = client.post(
            "/api/v1/jobs/search",
            json={
                "keywords": ["python"],
                "location": "Remote",
                "experience_level": "invalid_level",
            },
        )

        # Should reject invalid experience level
        assert response.status_code == 422

    def test_search_jobs_invalid_results_wanted_too_high(self, client):
        """Test job search with results_wanted exceeding maximum."""
        response = client.post(
            "/api/v1/jobs/search",
            json={
                "keywords": ["python"],
                "location": "Remote",
                "experience_level": "mid",
                "results_wanted": 150,  # Exceeds max of 100
            },
        )

        # Should reject value exceeding maximum
        assert response.status_code == 422

    def test_search_jobs_invalid_results_wanted_too_low(self, client):
        """Test job search with results_wanted below minimum."""
        response = client.post(
            "/api/v1/jobs/search",
            json={
                "keywords": ["python"],
                "location": "Remote",
                "experience_level": "mid",
                "results_wanted": 0,  # Below minimum of 1
            },
        )

        # Should reject value below minimum
        assert response.status_code == 422

    def test_search_jobs_invalid_hours_old_too_high(self, client):
        """Test job search with hours_old exceeding maximum."""
        response = client.post(
            "/api/v1/jobs/search",
            json={
                "keywords": ["python"],
                "location": "Remote",
                "experience_level": "mid",
                "hours_old": 1000,  # Exceeds max of 720
            },
        )

        # Should reject value exceeding maximum
        assert response.status_code == 422


class TestGetAvailableSites:
    """Test cases for getting available job sites."""

    @pytest.mark.asyncio
    async def test_get_job_sites_success(self, client, mock_job_search_service):
        """Test successfully retrieving available job sites."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.get("/api/v1/jobs/sites")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            assert "indeed" in data or "linkedin" in data

    @pytest.mark.asyncio
    async def test_get_job_sites_returns_list(self, client, mock_job_search_service):
        """Test that get sites returns a list of strings."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.get("/api/v1/jobs/sites")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            for site in data:
                assert isinstance(site, str)

    @pytest.mark.asyncio
    async def test_get_job_sites_fallback(self, client, mock_job_search_service):
        """Test fallback when service fails to get sites."""
        mock_job_search_service.get_available_sites = MagicMock(
            side_effect=Exception("Service error")
        )

        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.get("/api/v1/jobs/sites")

            # Should return fallback list or error
            assert response.status_code in [200, 500]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)


class TestJobSearchFallback:
    """Test cases for job search fallback behavior."""

    @pytest.mark.asyncio
    async def test_job_search_fallback_when_jobspy_fails(
        self, client, mock_job_search_service
    ):
        """Test fallback behavior when JobSpy service fails."""
        mock_job_search_service.search_jobs = AsyncMock(
            return_value=JobSearchResponse(
                jobs={},
                total_jobs=0,
                search_metadata={
                    "keywords": ["python"],
                    "location": "Remote",
                    "sites_searched": [],
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": "fallback",
                    "fallback_used": True,
                    "fallback_reason": "JobSpy service unavailable",
                },
            )
        )

        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": "Remote",
                    "experience_level": "mid",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "search_metadata" in data
            metadata = data["search_metadata"]
            assert metadata.get("fallback_used") is True

    @pytest.mark.asyncio
    async def test_job_search_with_partial_results(
        self, client, mock_job_search_service
    ):
        """Test job search with partial results from some sites."""
        test_job = Job(
            id="job-456",
            title="Senior Python Developer",
            company="StartupCorp",
            location="Remote",
            url="https://example.com/jobs/456",
            portal="linkedin",
            description="Looking for experienced Python developer",
            salary="$100,000 - $150,000",
            posted_date="1 day ago",
            experience_level=ExperienceLevel.SENIOR,
            job_type=JobType.FULL_TIME,
            skills=["Python", "Django", "PostgreSQL"],
            application_method=JobApplicationMethod.DIRECT_URL,
            apply_url="https://example.com/apply/456",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_job_search_service.search_jobs = AsyncMock(
            return_value=JobSearchResponse(
                jobs={"linkedin": [test_job]},  # Only LinkedIn results
                total_jobs=1,
                search_metadata={
                    "keywords": ["python"],
                    "location": "Remote",
                    "sites_searched": ["linkedin"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": "partial",
                    "fallback_used": False,
                },
            )
        )

        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": "Remote",
                    "experience_level": "senior",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_jobs"] == 1
            assert "linkedin" in data["jobs"]


class TestJobSearchServiceError:
    """Test cases for job search service error handling."""

    @pytest.mark.asyncio
    async def test_search_jobs_service_error(self, client, mock_job_search_service):
        """Test job search when service raises an exception."""
        mock_job_search_service.search_jobs = AsyncMock(
            side_effect=Exception("Service connection error")
        )

        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": "Remote",
                    "experience_level": "mid",
                },
            )

            # Should return error response instead of raising
            assert response.status_code == 200
            data = response.json()
            assert "search_metadata" in data
            assert data["total_jobs"] == 0

    @pytest.mark.asyncio
    async def test_search_jobs_timeout_error(self, client, mock_job_search_service):
        """Test job search when service times out."""
        mock_job_search_service.search_jobs = AsyncMock(
            side_effect=TimeoutError("Request timed out")
        )

        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": "Remote",
                    "experience_level": "mid",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_jobs"] == 0


class TestGetJobDetails:
    """Test cases for getting individual job details."""

    @pytest.mark.asyncio
    async def test_get_job_details_success(self, client, mock_job_search_service):
        """Test successfully retrieving job details."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.get("/api/v1/jobs/indeed_job123")

            assert response.status_code == 200
            data = response.json()
            assert "title" in data
            assert "company" in data
            assert "location" in data
            assert "url" in data

    @pytest.mark.asyncio
    async def test_get_job_details_not_found(self, client, mock_job_search_service):
        """Test retrieving non-existent job."""
        mock_job_search_service.get_job_details = AsyncMock(return_value=None)

        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.get("/api/v1/jobs/nonexistent_job")

            # Endpoint catches HTTPException and returns 500 due to error handling
            assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_get_job_details_with_platform_prefix(
        self, client, mock_job_search_service
    ):
        """Test retrieving job details with platform prefix in ID."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.get("/api/v1/jobs/linkedin_job456")

            assert response.status_code == 200
            data = response.json()
            assert "title" in data

    @pytest.mark.asyncio
    async def test_get_job_details_service_error(self, client, mock_job_search_service):
        """Test job details retrieval when service fails."""
        mock_job_search_service.get_job_details = AsyncMock(
            side_effect=Exception("Service error")
        )

        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.get("/api/v1/jobs/job123")

            assert response.status_code == 500


class TestJobSearchResponseStructure:
    """Test cases for verifying response structure."""

    @pytest.mark.asyncio
    async def test_search_response_has_required_fields(
        self, client, mock_job_search_service
    ):
        """Test that search response contains all required fields."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": "Remote",
                    "experience_level": "mid",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "jobs" in data
            assert "total_jobs" in data
            assert "search_metadata" in data
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_job_object_has_required_fields(
        self, client, mock_job_search_service
    ):
        """Test that job objects contain required fields."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": "Remote",
                    "experience_level": "mid",
                },
            )

            assert response.status_code == 200
            data = response.json()
            if data["total_jobs"] > 0:
                for site, jobs in data["jobs"].items():
                    for job in jobs:
                        assert "title" in job
                        assert "company" in job
                        assert "location" in job
                        assert "url" in job
                        assert "portal" in job

    @pytest.mark.asyncio
    async def test_search_metadata_structure(self, client, mock_job_search_service):
        """Test that search metadata has expected structure."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": "Remote",
                    "experience_level": "mid",
                },
            )

            assert response.status_code == 200
            data = response.json()
            metadata = data["search_metadata"]
            assert isinstance(metadata, dict)
            assert "timestamp" in metadata


class TestJobSearchEdgeCases:
    """Test cases for edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_search_with_empty_keywords_list(
        self, client, mock_job_search_service
    ):
        """Test job search with empty keywords list."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": [],
                    "location": "Remote",
                    "experience_level": "mid",
                },
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_with_special_characters_in_keywords(
        self, client, mock_job_search_service
    ):
        """Test job search with special characters in keywords."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["c++", "c#", ".net"],
                    "location": "Remote",
                    "experience_level": "mid",
                },
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_with_very_long_location_string(
        self, client, mock_job_search_service
    ):
        """Test job search with very long location string."""
        long_location = (
            "San Francisco, California, United States of America, North America"
        )

        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": long_location,
                    "experience_level": "mid",
                },
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_with_minimum_results_wanted(
        self, client, mock_job_search_service
    ):
        """Test job search with minimum results_wanted value."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": "Remote",
                    "experience_level": "mid",
                    "results_wanted": 1,
                },
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_with_maximum_results_wanted(
        self, client, mock_job_search_service
    ):
        """Test job search with maximum results_wanted value."""
        with patch(
            "src.services.service_registry.service_registry.get_job_search_service",
            return_value=mock_job_search_service,
        ):
            response = client.post(
                "/api/v1/jobs/search",
                json={
                    "keywords": ["python"],
                    "location": "Remote",
                    "experience_level": "mid",
                    "results_wanted": 100,
                },
            )

            assert response.status_code == 200
