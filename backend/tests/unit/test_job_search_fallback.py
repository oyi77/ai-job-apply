"""Test job search service fallback scenarios."""

import pytest
from datetime import datetime
from src.services.job_search_service import JobSearchService
from src.models.job import JobSearchRequest, ExperienceLevel


@pytest.mark.asyncio
async def test_fallback_when_jobspy_unavailable():
    """Test that fallback is used when JobSpy is unavailable."""
    service = JobSearchService()
    await service.initialize()
    
    # Service should initialize even without JobSpy
    assert service._initialized is True
    
    # Create a search request
    request = JobSearchRequest(
        keywords=["Python", "Developer"],
        location="Remote",
        experience_level=ExperienceLevel.MID
    )
    
    # Search should work with fallback
    response = await service.search_jobs(request)
    
    # Verify response structure
    assert response.total_jobs > 0
    assert isinstance(response.jobs, dict)
    assert len(response.jobs) > 0
    
    # Verify fallback metadata
    assert response.search_metadata.get("method") == "fallback"
    assert response.search_metadata.get("fallback_used") is True
    assert "fallback_reason" in response.search_metadata


@pytest.mark.asyncio
async def test_fallback_generates_realistic_jobs():
    """Test that fallback generates realistic job data."""
    service = JobSearchService()
    await service.initialize()
    
    request = JobSearchRequest(
        keywords=["React", "Frontend"],
        location="San Francisco",
        experience_level=ExperienceLevel.SENIOR
    )
    
    response = await service.search_jobs(request)
    
    # Check that jobs have realistic data
    for platform, jobs in response.jobs.items():
        assert len(jobs) > 0
        for job in jobs:
            assert job.title is not None
            assert job.company is not None
            assert job.location == "San Francisco"
            assert job.experience_level == ExperienceLevel.SENIOR
            assert job.salary is not None
            assert job.description is not None
            # Check that salary matches experience level
            assert "$120,000" in job.salary or "$150,000" in job.salary or "$160,000" in job.salary


@pytest.mark.asyncio
async def test_fallback_keyword_based_titles():
    """Test that fallback generates titles based on keywords."""
    service = JobSearchService()
    await service.initialize()
    
    # Test Python keywords
    request = JobSearchRequest(
        keywords=["Python", "Backend"],
        location="Remote",
        experience_level=ExperienceLevel.MID
    )
    
    response = await service.search_jobs(request)
    
    # Check that titles match keywords
    titles = [job.title for jobs in response.jobs.values() for job in jobs]
    python_titles = [t for t in titles if "Python" in t or "Backend" in t or "Developer" in t]
    assert len(python_titles) > 0


@pytest.mark.asyncio
async def test_fallback_experience_level_salary():
    """Test that fallback adjusts salary based on experience level."""
    service = JobSearchService()
    await service.initialize()
    
    # Test entry level
    request_entry = JobSearchRequest(
        keywords=["Developer"],
        location="Remote",
        experience_level=ExperienceLevel.ENTRY
    )
    response_entry = await service.search_jobs(request_entry)
    
    # Test senior level
    request_senior = JobSearchRequest(
        keywords=["Developer"],
        location="Remote",
        experience_level=ExperienceLevel.SENIOR
    )
    response_senior = await service.search_jobs(request_senior)
    
    # Entry level should have lower salary range
    entry_salaries = [job.salary for jobs in response_entry.jobs.values() for job in jobs]
    senior_salaries = [job.salary for jobs in response_senior.jobs.values() for job in jobs]
    
    # Check that senior salaries are higher
    entry_max = max([int(s.split("-")[1].replace("$", "").replace(",", "").strip()) 
                     for s in entry_salaries if "-" in s])
    senior_max = max([int(s.split("-")[1].replace("$", "").replace(",", "").strip()) 
                      for s in senior_salaries if "-" in s])
    
    assert senior_max > entry_max


@pytest.mark.asyncio
async def test_fallback_error_handling():
    """Test that fallback handles errors gracefully."""
    service = JobSearchService()
    await service.initialize()
    
    # Create a request that might cause issues
    request = JobSearchRequest(
        keywords=[],
        location="",
        experience_level=ExperienceLevel.MID
    )
    
    # Should still return a response (even if empty)
    response = await service.search_jobs(request)
    assert response is not None
    assert "error" not in response.search_metadata or response.search_metadata.get("error") is None


@pytest.mark.asyncio
async def test_fallback_multiple_platforms():
    """Test that fallback returns jobs from multiple platforms."""
    service = JobSearchService()
    await service.initialize()
    
    request = JobSearchRequest(
        keywords=["Engineer"],
        location="Remote",
        experience_level=ExperienceLevel.MID
    )
    
    response = await service.search_jobs(request)
    
    # Should have jobs from multiple platforms
    platforms = list(response.jobs.keys())
    assert len(platforms) > 1
    assert "indeed" in platforms or "linkedin" in platforms or "glassdoor" in platforms


@pytest.mark.asyncio
async def test_fallback_metadata_includes_note():
    """Test that fallback metadata includes helpful note."""
    service = JobSearchService()
    await service.initialize()
    
    request = JobSearchRequest(
        keywords=["Developer"],
        location="Remote"
    )
    
    response = await service.search_jobs(request)
    
    # Check for note about mock data
    assert "note" in response.search_metadata
    assert "mock" in response.search_metadata["note"].lower() or "demonstration" in response.search_metadata["note"].lower()

