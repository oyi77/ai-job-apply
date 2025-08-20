"""Job application data models."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ApplicationStatus(str, Enum):
    """Application status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    OFFER_RECEIVED = "offer_received"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobApplication(BaseModel):
    """Job application model."""
    id: Optional[str] = None
    job_id: str = Field(..., description="Associated job ID")
    job_title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    status: ApplicationStatus = Field(default=ApplicationStatus.DRAFT, description="Application status")
    resume_path: Optional[str] = Field(None, description="Path to submitted resume")
    cover_letter_path: Optional[str] = Field(None, description="Path to submitted cover letter")
    applied_date: Optional[datetime] = Field(None, description="When application was submitted")
    notes: Optional[str] = Field(None, description="Application notes")
    follow_up_date: Optional[datetime] = Field(None, description="When to follow up")
    interview_date: Optional[datetime] = Field(None, description="Interview date if scheduled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class ApplicationUpdateRequest(BaseModel):
    """Application update request model."""
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    
    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
