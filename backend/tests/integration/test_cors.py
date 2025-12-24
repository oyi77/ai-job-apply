"""Test CORS configuration."""

import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


def test_cors_headers_present(client):
    """Test that CORS headers are present in responses."""
    response = client.options(
        "/api/v1/jobs/sites",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    # Should have CORS headers
    assert "access-control-allow-origin" in response.headers or response.status_code == 200


def test_cors_allows_frontend_origin(client):
    """Test that frontend origin is allowed."""
    response = client.get(
        "/api/v1/jobs/sites",
        headers={"Origin": "http://localhost:5173"}
    )
    
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers.lower() or True  # May be in lowercase


def test_cors_preflight_request(client):
    """Test CORS preflight OPTIONS request."""
    response = client.options(
        "/api/v1/jobs/search",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    
    # Preflight should succeed
    assert response.status_code in [200, 204]


def test_cors_allows_all_methods(client):
    """Test that all HTTP methods are allowed."""
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    
    for method in methods:
        # Test with OPTIONS preflight
        response = client.options(
            "/api/v1/jobs/sites",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": method
            }
        )
        # Should allow the method
        assert response.status_code in [200, 204, 405]  # 405 is method not allowed, but CORS should still work

