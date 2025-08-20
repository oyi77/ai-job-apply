"""Database models for the AI Job Application Assistant."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, Boolean, Integer, Float, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .config import Base
from ..models.application import ApplicationStatus
from ..models.resume import Resume
from ..models.cover_letter import CoverLetter


class DBResume(Base):
    """Database model for resumes."""
    
    __tablename__ = "resumes"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    experience_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    education: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    certifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications: Mapped[List["DBJobApplication"]] = relationship(
        "DBJobApplication", back_populates="resume", cascade="all, delete-orphan"
    )
    
    def to_model(self) -> Resume:
        """Convert database model to domain model."""
        import json
        
        skills = json.loads(self.skills) if self.skills else None
        education = json.loads(self.education) if self.education else None
        certifications = json.loads(self.certifications) if self.certifications else None
        
        return Resume(
            id=self.id,
            name=self.name,
            file_path=self.file_path,
            file_type=self.file_type,
            content=self.content,
            skills=skills,
            experience_years=self.experience_years,
            education=education,
            certifications=certifications,
            is_default=self.is_default,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
    
    @classmethod
    def from_model(cls, resume: Resume) -> "DBResume":
        """Create database model from domain model."""
        import json
        
        return cls(
            id=resume.id if resume.id else None,
            name=resume.name,
            file_path=resume.file_path,
            file_type=resume.file_type,
            content=resume.content,
            skills=json.dumps(resume.skills) if resume.skills else None,
            experience_years=resume.experience_years,
            education=json.dumps(resume.education) if resume.education else None,
            certifications=json.dumps(resume.certifications) if resume.certifications else None,
            is_default=resume.is_default,
            created_at=resume.created_at,
            updated_at=resume.updated_at,
        )


class DBCoverLetter(Base):
    """Database model for cover letters."""
    
    __tablename__ = "cover_letters"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str] = mapped_column(String(50), nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications: Mapped[List["DBJobApplication"]] = relationship(
        "DBJobApplication", back_populates="cover_letter", cascade="all, delete-orphan"
    )
    
    def to_model(self) -> CoverLetter:
        """Convert database model to domain model."""
        return CoverLetter(
            job_title=self.job_title,
            company_name=self.company_name,
            content=self.content,
            tone=self.tone,
            word_count=self.word_count,
        )
    
    @classmethod
    def from_model(cls, cover_letter: CoverLetter) -> "DBCoverLetter":
        """Create database model from domain model."""
        return cls(
            job_title=cover_letter.job_title,
            company_name=cover_letter.company_name,
            content=cover_letter.content,
            tone=cover_letter.tone,
            word_count=cover_letter.word_count,
        )


class DBJobApplication(Base):
    """Database model for job applications."""
    
    __tablename__ = "job_applications"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(SQLEnum(ApplicationStatus), nullable=False)
    resume_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_letter_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    applied_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    interview_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    follow_up_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    resume_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("resumes.id"), nullable=True)
    cover_letter_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("cover_letters.id"), nullable=True)
    
    # Relationships
    resume: Mapped[Optional[DBResume]] = relationship(
        "DBResume", back_populates="applications", foreign_keys=[resume_id]
    )
    cover_letter: Mapped[Optional[DBCoverLetter]] = relationship(
        "DBCoverLetter", back_populates="applications", foreign_keys=[cover_letter_id]
    )
    
    def to_model(self) -> "JobApplication":
        """Convert database model to domain model."""
        from ..models.application import JobApplication
        
        return JobApplication(
            id=self.id,
            job_id=self.job_id,
            job_title=self.job_title,
            company=self.company,
            status=self.status,
            resume_path=self.resume_path,
            cover_letter_path=self.cover_letter_path,
            applied_date=self.applied_date,
            interview_date=self.interview_date,
            follow_up_date=self.follow_up_date,
            notes=self.notes,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
    
    @classmethod
    def from_model(cls, application: "JobApplication") -> "DBJobApplication":
        """Create database model from domain model."""
        return cls(
            id=application.id,
            job_id=application.job_id,
            job_title=application.job_title,
            company=application.company,
            status=application.status,
            resume_path=application.resume_path,
            cover_letter_path=application.cover_letter_path,
            applied_date=application.applied_date,
            interview_date=application.interview_date,
            follow_up_date=application.follow_up_date,
            notes=application.notes,
            created_at=application.created_at,
            updated_at=application.updated_at,
        )


class DBJobSearch(Base):
    """Database model for job search history."""
    
    __tablename__ = "job_searches"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    keywords: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    experience_level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    search_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        import json
        
        return {
            "id": self.id,
            "keywords": json.loads(self.keywords) if self.keywords else [],
            "location": self.location,
            "experience_level": self.experience_level,
            "results_count": self.results_count,
            "search_date": self.search_date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


class DBAIActivity(Base):
    """Database model for AI activity tracking."""
    
    __tablename__ = "ai_activities"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)  # optimize_resume, generate_cover_letter, etc.
    input_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    output_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        import json
        
        return {
            "id": self.id,
            "activity_type": self.activity_type,
            "input_data": json.loads(self.input_data) if self.input_data else None,
            "output_data": json.loads(self.output_data) if self.output_data else None,
            "success": self.success,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "confidence_score": self.confidence_score,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
        }


class DBFileMetadata(Base):
    """Database model for file metadata."""
    
    __tablename__ = "file_metadata"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    md5_hash: Mapped[str] = mapped_column(String(32), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "mime_type": self.mime_type,
            "md5_hash": self.md5_hash,
            "uploaded_at": self.uploaded_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "is_active": self.is_active,
        }
