"""Test data fixtures for the AI Job Application Assistant."""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid


def sample_resume_data() -> Dict[str, Any]:
    """Generate sample resume data for testing."""
    return {
        "id": str(uuid.uuid4()),
        "name": "John Doe Resume",
        "file_path": "/test/resumes/john_doe_resume.pdf",
        "file_type": "pdf",
        "content": "John Doe\nSoftware Engineer\n\nExperience:\n- 5 years of Python development\n- 3 years of React development",
        "skills": ["Python", "JavaScript", "React", "FastAPI", "PostgreSQL"],
        "experience_years": 5,
        "education": ["Bachelor of Science in Computer Science"],
        "certifications": ["AWS Certified Developer"],
        "is_default": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


def sample_application_data() -> Dict[str, Any]:
    """Generate sample application data for testing."""
    return {
        "id": str(uuid.uuid4()),
        "job_id": str(uuid.uuid4()),
        "job_title": "Senior Software Engineer",
        "company": "Tech Corp",
        "location": "San Francisco, CA",
        "job_url": "https://techcorp.com/careers/senior-software-engineer",
        "portal": "LinkedIn",
        "description": "We are looking for a senior software engineer with 5+ years of experience...",
        "requirements": ["Python", "JavaScript", "React", "AWS"],
        "salary_range": "$120,000 - $160,000",
        "status": "applied",
        "applied_date": datetime.utcnow() - timedelta(days=3),
        "follow_up_date": datetime.utcnow() + timedelta(days=7),
        "notes": "Great company culture, interesting technical challenges",
        "resume_id": str(uuid.uuid4()),
        "cover_letter_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


def sample_job_data() -> Dict[str, Any]:
    """Generate sample job data for testing."""
    return {
        "id": str(uuid.uuid4()),
        "title": "Software Engineer",
        "company": "Tech Startup",
        "location": "Remote",
        "url": "https://techstartup.com/careers/software-engineer",
        "portal": "Indeed",
        "description": "Join our innovative team building the next generation of web applications...",
        "requirements": ["Python", "Django", "PostgreSQL", "Docker"],
        "salary": "$90,000 - $120,000",
        "posted_date": "2024-01-15",
        "experience_level": "mid",
        "job_type": "full_time",
        "is_remote": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


def sample_cover_letter_data() -> Dict[str, Any]:
    """Generate sample cover letter data for testing."""
    return {
        "id": str(uuid.uuid4()),
        "job_title": "Software Engineer",
        "company_name": "Tech Startup",
        "content": """Dear Hiring Manager,

I am writing to express my interest in the Software Engineer position at Tech Startup. 
With my 5 years of experience in Python development and passion for innovative 
technology solutions, I am confident I would be a valuable addition to your team.

My background includes extensive work with Python, Django, and PostgreSQL, 
which aligns perfectly with your requirements. I am particularly excited about 
the opportunity to work on next-generation web applications.

I would welcome the opportunity to discuss how my skills and experience can 
contribute to Tech Startup's continued success.

Sincerely,
John Doe""",
        "tone": "professional",
        "template_used": "ai_generated",
        "job_description": "Join our innovative team building the next generation of web applications...",
        "resume_summary": "5 years of Python development experience with expertise in web applications",
        "word_count": 150,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


def sample_job_search_request() -> Dict[str, Any]:
    """Generate sample job search request data for testing."""
    return {
        "keywords": ["software engineer", "python"],
        "location": "San Francisco, CA",
        "experience_level": "mid",
        "job_type": "full_time",
        "is_remote": False,
        "salary_min": 80000,
        "salary_max": 120000
    }


def sample_job_search_response() -> Dict[str, Any]:
    """Generate sample job search response data for testing."""
    return {
        "jobs": {
            "linkedin": [sample_job_data(), sample_job_data()],
            "indeed": [sample_job_data()]
        },
        "total_jobs": 3,
        "search_metadata": {
            "keywords": ["software engineer", "python"],
            "location": "San Francisco, CA",
            "experience_level": "mid",
            "sites_searched": ["linkedin", "indeed"],
            "timestamp": datetime.utcnow()
        }
    }


def create_multiple_resumes(count: int = 3) -> List[Dict[str, Any]]:
    """Create multiple resume samples for testing."""
    resumes = []
    for i in range(count):
        resume = sample_resume_data()
        resume["name"] = f"Resume {i+1}"
        resume["is_default"] = (i == 0)  # First resume is default
        resumes.append(resume)
    return resumes


def create_multiple_applications(count: int = 5) -> List[Dict[str, Any]]:
    """Create multiple application samples for testing."""
    applications = []
    statuses = ["draft", "applied", "interview", "offer", "rejected"]
    
    for i in range(count):
        application = sample_application_data()
        application["job_title"] = f"Position {i+1}"
        application["company"] = f"Company {i+1}"
        application["status"] = statuses[i % len(statuses)]
        applications.append(application)
    
    return applications


def create_multiple_jobs(count: int = 10) -> List[Dict[str, Any]]:
    """Create multiple job samples for testing."""
    jobs = []
    titles = ["Software Engineer", "Senior Developer", "Full Stack Developer", 
              "Backend Engineer", "Frontend Developer"]
    companies = ["Tech Corp", "StartupXYZ", "BigTech Inc", "Innovation Labs", "DevCorp"]
    
    for i in range(count):
        job = sample_job_data()
        job["title"] = titles[i % len(titles)]
        job["company"] = companies[i % len(companies)]
        jobs.append(job)
    
    return jobs
