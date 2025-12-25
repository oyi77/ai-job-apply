"""Job-related data models."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
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


class JobApplicationMethod(str, Enum):
    """Job application method enumeration."""
    DIRECT_URL = "direct_url"
    EMAIL = "email"
    EXTERNAL_SITE = "external_site"
    PHONE = "phone"
    IN_PERSON = "in_person"
    FORM = "form"
    UNKNOWN = "unknown"


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
    
    # Application-related fields
    application_method: JobApplicationMethod = Field(default=JobApplicationMethod.UNKNOWN, description="How to apply")
    apply_url: Optional[HttpUrl] = Field(None, description="Direct application URL")
    contact_email: Optional[str] = Field(None, description="Application contact email")
    contact_phone: Optional[str] = Field(None, description="Application contact phone")
    external_application: bool = Field(False, description="If application is external to this platform")
    application_deadline: Optional[str] = Field(None, description="Application deadline")
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class ApplicationForm(BaseModel):
    """Job application form information."""
    form_url: Optional[HttpUrl] = Field(None, description="Application form URL")
    form_fields: List[Dict[str, Any]] = Field(default_factory=list, description="Form field definitions")
    required_fields: List[str] = Field(default_factory=list, description="Required form fields")
    optional_fields: List[str] = Field(default_factory=list, description="Optional form fields")
    file_uploads: List[str] = Field(default_factory=list, description="File upload field names")
    form_type: str = Field(default="standard", description="Type of application form")


class ApplicationInfo(BaseModel):
    """Complete job application information."""
    job: Job
    application_method: JobApplicationMethod
    apply_url: Optional[HttpUrl] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    application_form: Optional[ApplicationForm] = None
    instructions: Optional[str] = None
    requirements: Optional[List[str]] = None
    deadline: Optional[str] = None
    external_site: Optional[bool] = None


class JobSearchRequest(BaseModel):
    """Job search request model."""
    keywords: List[str] = Field(default_factory=list, description="Search keywords")
    location: str = Field(default="Remote", description="Job location")
    experience_level: ExperienceLevel = Field(default=ExperienceLevel.ENTRY, description="Experience level")
    sites: Optional[List[str]] = Field(None, description="Specific sites to search")
    results_wanted: int = Field(default=50, ge=1, le=100, description="Number of results wanted")
    hours_old: int = Field(default=72, ge=1, le=720, description="Maximum age of job postings")
    
    model_config = ConfigDict(
        use_enum_values=True
    )


class JobSearchResponse(BaseModel):
    """Job search response model."""
    jobs: Dict[str, List[Job]] = Field(..., description="Jobs grouped by portal")
    total_jobs: int = Field(..., description="Total number of jobs found")
    search_metadata: Dict[str, Any] = Field(default_factory=dict, description="Search metadata")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(
        populate_by_name=True
    )
