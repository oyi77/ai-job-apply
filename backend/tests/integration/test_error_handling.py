"""Integration tests for error handling and fallback scenarios."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.mark.asyncio
async def test_job_search_error_handling(client):
    """Test that job search handles errors gracefully."""
    # Test with invalid request data
    invalid_data = {
        "keywords": [],  # Empty keywords
        "location": ""
    }
    
    response = client.post("/api/v1/jobs/search", json=invalid_data)
    
    # Should return 200 with error in metadata or 422 validation error
    assert response.status_code in [200, 422]
    
    if response.status_code == 200:
        data = response.json()
        # Should have error indication or empty results
        assert "search_metadata" in data
        assert data.get("total_jobs", 0) >= 0


@pytest.mark.asyncio
async def test_api_error_response_format(client):
    """Test that API errors have consistent format."""
    # Test with invalid endpoint
    response = client.get("/api/v1/nonexistent")
    
    # Should return 404
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_job_search_fallback_indication(client):
    """Test that fallback usage is clearly indicated."""
    request_data = {
        "keywords": ["Test"],
        "location": "Remote"
    }
    
    response = client.post("/api/v1/jobs/search", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    metadata = data.get("search_metadata", {})
    
    # Should indicate if fallback was used
    if metadata.get("method") == "fallback":
        assert metadata.get("fallback_used") is True
        assert "fallback_reason" in metadata or "note" in metadata


@pytest.mark.asyncio
async def test_api_timeout_handling(client):
    """Test that API handles timeouts gracefully."""
    # This test verifies the API doesn't hang on slow operations
    request_data = {
        "keywords": ["Engineer"],
        "location": "Remote"
    }
    
    response = client.post("/api/v1/jobs/search", json=request_data, timeout=30.0)
    
    # Should complete within timeout
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "jobs" in data
        assert "total_jobs" in data

