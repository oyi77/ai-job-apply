"""Integration tests for protected API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from src.api.app import create_app


@pytest.fixture
async def app():
    """Create FastAPI app for testing."""
    return create_app()


@pytest.fixture
async def client(app: FastAPI):
    """Create test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def valid_token():
    """Return a valid JWT token for testing."""
    return "valid-test-token"


@pytest.fixture
def invalid_token():
    """Return an invalid JWT token for testing."""
    return "invalid-test-token"


@pytest.mark.asyncio
async def test_cover_letters_endpoint_requires_auth(client: AsyncClient):
    """Test that cover letters endpoint requires authentication."""
    response = await client.get("/api/v1/cover-letters")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_cover_letters_create_requires_auth(client: AsyncClient):
    """Test that creating cover letter requires authentication."""
    response = await client.post(
        "/api/v1/cover-letters/",
        json={"job_title": "Engineer", "company_name": "Corp"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_ai_optimize_resume_requires_auth(client: AsyncClient):
    """Test that AI optimize resume endpoint requires authentication."""
    response = await client.post(
        "/api/v1/ai/optimize-resume",
        json={"resume_id": "test", "target_role": "Engineer"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_ai_generate_cover_letter_requires_auth(client: AsyncClient):
    """Test that AI generate cover letter endpoint requires authentication."""
    response = await client.post(
        "/api/v1/ai/generate-cover-letter",
        json={"job_title": "Engineer", "company_name": "Corp"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_job_applications_apply_requires_auth(client: AsyncClient):
    """Test that job application endpoint requires authentication."""
    response = await client.post(
        "/api/v1/job-applications/apply",
        data={
            "job_id": "test",
            "resume_id": "test",
            "cover_letter": "test"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_job_applications_info_requires_auth(client: AsyncClient):
    """Test that job application info endpoint requires authentication."""
    response = await client.get("/api/v1/job-applications/info/test-job-id")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ai_health_endpoint_public(client: AsyncClient):
    """Test that AI health endpoint is public (no auth required)."""
    response = await client.get("/api/v1/ai/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_job_applications_health_endpoint_public(client: AsyncClient):
    """Test that job applications health endpoint is public."""
    response = await client.get("/api/v1/job-applications/health")
    assert response.status_code == 200

