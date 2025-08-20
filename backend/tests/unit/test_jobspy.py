#!/usr/bin/env python3
"""Test JobSpy availability."""

import asyncio
from src.services.service_registry import service_registry


async def test_jobspy():
    """Test if JobSpy is available."""
    try:
        await service_registry.initialize()
        js = await service_registry.get_job_search_service()
        print(f"JobSpy available: {js._jobspy_available}")
        
        if js._jobspy_available:
            print("✅ JobSpy is working!")
            # Test a simple search
            from src.models.job import JobSearchRequest
            request = JobSearchRequest(keywords=["Software Engineer"], location="Remote")
            result = await js.search_jobs(request)
            print(f"Found {result.total_jobs} jobs")
        else:
            print("❌ JobSpy not available")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_jobspy())
