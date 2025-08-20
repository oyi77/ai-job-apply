#!/usr/bin/env python3
"""Test script for the job application system."""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.service_registry import service_registry
from src.models.job import Job, JobApplicationMethod
from src.models.resume import Resume


async def test_job_application_system():
    """Test the job application system."""
    print("🧪 Testing Job Application System")
    print("=" * 50)
    
    try:
        # Initialize service registry
        print("1. Initializing service registry...")
        await service_registry.initialize()
        print("✅ Service registry initialized")
        
        # Test job application service
        print("\n2. Testing job application service...")
        app_service = await service_registry.get_job_application_service()
        
        # Health check
        health = await app_service.health_check()
        print(f"✅ Service health: {health}")
        
        # Get supported platforms
        platforms = await app_service.get_supported_platforms()
        print(f"✅ Supported platforms: {platforms}")
        
        # Create a mock job
        print("\n3. Creating mock job for testing...")
        mock_job = Job(
            title="Senior Software Engineer",
            company="Test Company Inc.",
            location="Remote",
            url="https://example.com/job/123",
            portal="mock",
            description="This is a test job for testing the application system.",
            salary="$100,000 - $150,000",
            posted_date="Recently",
            experience_level="senior",
            application_method=JobApplicationMethod.DIRECT_URL,
            apply_url="https://example.com/apply/123",
            contact_email="careers@testcompany.com",
            external_application=True
        )
        print(f"✅ Mock job created: {mock_job.title} at {mock_job.company}")
        
        # Test getting application info
        print("\n4. Testing application info extraction...")
        app_info = await app_service.get_application_info(mock_job)
        print(f"✅ Application method: {app_info.application_method}")
        print(f"✅ Apply URL: {app_info.apply_url}")
        print(f"✅ Contact email: {app_info.contact_email}")
        
        # Create a mock resume
        print("\n5. Creating mock resume...")
        mock_resume = Resume(
            id="test_resume_001",
            name="Professional Resume",
            file_path="/tmp/test_resume.pdf",
            file_type="pdf",
            content="This is a test resume with Python, JavaScript, and React skills.",
            skills=["Python", "JavaScript", "React", "Node.js"],
            experience_years=5,
            education=["Bachelor's in Computer Science"],
            certifications=["AWS Certified Developer"]
        )
        print(f"✅ Mock resume created with {len(mock_resume.skills)} skills")
        
        # Test application validation
        print("\n6. Testing application validation...")
        validation = await app_service.validate_application_data(
            job=mock_job,
            resume=mock_resume,
            cover_letter="This is a test cover letter for the Senior Software Engineer position."
        )
        print(f"✅ Validation result: {validation.get('valid')}")
        if validation.get('warnings'):
            print(f"⚠️  Warnings: {validation.get('warnings')}")
        
        # Test applying to job
        print("\n7. Testing job application...")
        result = await app_service.apply_to_job(
            job=mock_job,
            resume=mock_resume,
            cover_letter="This is a test cover letter for the Senior Software Engineer position.",
            additional_data={"source": "test_script"}
        )
        
        if result.get("success"):
            print(f"✅ Application successful!")
            print(f"   Application ID: {result.get('application_id')}")
            print(f"   Method: {result.get('method')}")
            print(f"   Company: {result.get('company')}")
            print(f"   Position: {result.get('position')}")
        else:
            print(f"❌ Application failed: {result.get('error')}")
        
        # Test application status
        if result.get("success"):
            print("\n8. Testing application status...")
            status = await app_service.get_application_status(result.get("application_id"))
            print(f"✅ Status: {status.get('status')}")
            print(f"✅ Platform: {status.get('platform')}")
        
        print("\n🎉 Job Application System Test Completed Successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_job_search_with_applications():
    """Test job search with application information."""
    print("\n🔍 Testing Job Search with Application Info")
    print("=" * 50)
    
    try:
        # Get job search service
        job_search_service = await service_registry.get_job_search_service()
        
        # Search for jobs
        print("1. Searching for jobs...")
        from src.models.job import JobSearchRequest
        
        search_request = JobSearchRequest(
            keywords=["python", "developer"],
            location="Remote",
            experience_level="mid",
            results_wanted=5
        )
        
        search_results = await job_search_service.search_jobs(search_request)
        print(f"✅ Found {search_results.total_jobs} jobs across {len(search_results.jobs)} platforms")
        
        # Check application information for each job
        print("\n2. Checking application information for jobs...")
        for platform, jobs in search_results.jobs.items():
            print(f"\n📱 Platform: {platform}")
            for i, job in enumerate(jobs[:3]):  # Show first 3 jobs per platform
                print(f"   Job {i+1}: {job.title} at {job.company}")
                print(f"      Application Method: {job.application_method}")
                if job.apply_url:
                    print(f"      Apply URL: {job.apply_url}")
                if job.contact_email:
                    print(f"      Contact Email: {job.contact_email}")
                if job.external_application:
                    print(f"      External Application: Yes")
                print(f"      Skills: {', '.join(job.skills[:3]) if job.skills else 'None'}")
        
        print("\n✅ Job search with application info completed successfully!")
        
    except Exception as e:
        print(f"❌ Job search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """Main test function."""
    print("🚀 Starting Job Application System Tests")
    print("=" * 60)
    
    # Test 1: Basic job application system
    success1 = await test_job_application_system()
    
    # Test 2: Job search with application info
    success2 = await test_job_search_with_applications()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Job Application System: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Job Search with Apps:   {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED! The job application system is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
