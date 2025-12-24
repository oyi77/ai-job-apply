"""Integration tests for job search API endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app
from src.models.job import ExperienceLevel


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.mark.asyncio
async def test_job_search_endpoint_success(client):
    """Test successful job search."""
    request_data = {
        "keywords": ["Python", "Developer"],
        "location": "Remote",
        "experience_level": "mid"
    }
    
    response = client.post("/api/v1/jobs/search", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "jobs" in data
    assert "total_jobs" in data
    assert "search_metadata" in data
    
    # Verify jobs structure
    assert isinstance(data["jobs"], dict)
    assert data["total_jobs"] > 0
    
    # Verify metadata
    metadata = data["search_metadata"]
    assert metadata["keywords"] == request_data["keywords"]
    assert metadata["location"] == request_data["location"]
    assert "timestamp" in metadata
    assert "method" in metadata


@pytest.mark.asyncio
async def test_job_search_endpoint_fallback_indication(client):
    """Test that fallback usage is indicated in response."""
    request_data = {
        "keywords": ["Engineer"],
        "location": "San Francisco"
    }
    
    response = client.post("/api/v1/jobs/search", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check for fallback indication
    metadata = data["search_metadata"]
    if metadata.get("method") == "fallback":
        assert metadata.get("fallback_used") is True
        assert "fallback_reason" in metadata


@pytest.mark.asyncio
async def test_job_search_endpoint_error_handling(client):
    """Test error handling in job search endpoint."""
    # Test with invalid data
    invalid_data = {
        "keywords": [],  # Empty keywords should be handled
        "location": ""
    }
    
    response = client.post("/api/v1/jobs/search", json=invalid_data)
    
    # Should return 200 with empty results or error in metadata
    assert response.status_code in [200, 422]
    
    if response.status_code == 200:
        data = response.json()
        # Should have error indication in metadata if search failed
        if "error" in data.get("search_metadata", {}):
            assert data["search_metadata"]["error"] is not None


@pytest.mark.asyncio
async def test_job_search_endpoint_different_experience_levels(client):
    """Test job search with different experience levels."""
    experience_levels = ["entry", "junior", "mid", "senior", "lead"]
    
    for level in experience_levels:
        request_data = {
            "keywords": ["Developer"],
            "location": "Remote",
            "experience_level": level
        }
        
        response = client.post("/api/v1/jobs/search", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_jobs"] > 0


@pytest.mark.asyncio
async def test_get_available_sites_endpoint(client):
    """Test getting available job sites."""
    response = client.get("/api/v1/jobs/sites")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(site, str) for site in data)


@pytest.mark.asyncio
async def test_job_search_response_format(client):
    """Test that job search response has correct format."""
    request_data = {
        "keywords": ["Software Engineer"],
        "location": "Remote"
    }
    
    response = client.post("/api/v1/jobs/search", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify jobs structure
    for platform, jobs in data["jobs"].items():
        assert isinstance(platform, str)
        assert isinstance(jobs, list)
        
        for job in jobs:
            assert "title" in job
            assert "company" in job
            assert "location" in job
            assert "url" in job
            assert "portal" in job

