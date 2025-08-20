"""Job-related data models."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience level enumeration."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class JobType(str, Enum):
    """Job type enumeration."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class Job(BaseModel):
    """Job posting model."""
    id: Optional[str] = None
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    url: HttpUrl = Field(..., description="Job posting URL")
    portal: str = Field(..., description="Source portal name")
    description: Optional[str] = Field(None, description="Job description")
    salary: Optional[str] = Field(None, description="Salary information")
    posted_date: Optional[str] = Field(None, description="When job was posted")
    experience_level: Optional[ExperienceLevel] = Field(None, description="Required experience level")
    job_type: Optional[JobType] = Field(None, description="Type of employment")
    requirements: Optional[List[str]] = Field(None, description="Job requirements")
    benefits: Optional[List[str]] = Field(None, description="Job benefits")
    skills: Optional[List[str]] = Field(None, description="Required skills")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class JobSearchRequest(BaseModel):
    """Job search request model."""
    keywords: List[str] = Field(..., min_items=1, description="Search keywords")
    location: str = Field(default="Remote", description="Job location")
    experience_level: ExperienceLevel = Field(default=ExperienceLevel.ENTRY, description="Experience level")
    sites: Optional[List[str]] = Field(None, description="Specific sites to search")
    results_wanted: int = Field(default=50, ge=1, le=100, description="Number of results wanted")
    hours_old: int = Field(default=72, ge=1, le=720, description="Maximum age of job postings")
    
    model_config = {
        "use_enum_values": True
    }


class JobSearchResponse(BaseModel):
    """Job search response model."""
    jobs: Dict[str, List[Job]] = Field(..., description="Jobs grouped by portal")
    total_jobs: int = Field(..., description="Total number of jobs found")
    search_metadata: Dict[str, Any] = Field(default_factory=dict, description="Search metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
