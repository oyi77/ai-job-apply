"""Database models for the AI Job Application Assistant."""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, Boolean, Integer, Float, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.database.config import Base
from src.models.application import ApplicationStatus
from src.models.resume import Resume
from src.models.cover_letter import CoverLetter
from src.models.user import User as UserModel


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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign keys
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    applications: Mapped[List["DBJobApplication"]] = relationship(
        "DBJobApplication", back_populates="resume", cascade="all, delete-orphan"
    )
    user: Mapped[Optional["DBUser"]] = relationship(
        "DBUser", back_populates="resumes", foreign_keys=[user_id]
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_resume_created_at", "created_at"),
        Index("idx_resume_is_default", "is_default"),
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign keys
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    applications: Mapped[List["DBJobApplication"]] = relationship(
        "DBJobApplication", back_populates="cover_letter", cascade="all, delete-orphan"
    )
    user: Mapped[Optional["DBUser"]] = relationship(
        "DBUser", back_populates="cover_letters", foreign_keys=[user_id]
    )
    
    def to_model(self) -> CoverLetter:
        """Convert database model to domain model."""
        return CoverLetter(
            id=self.id,
            job_title=self.job_title,
            company_name=self.company_name,
            content=self.content,
            tone=self.tone,
            word_count=self.word_count,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
    
    @classmethod
    def from_model(cls, cover_letter: CoverLetter) -> "DBCoverLetter":
        """Create database model from domain model."""
        return cls(
            id=cover_letter.id if cover_letter.id else None,
            job_title=cover_letter.job_title,
            company_name=cover_letter.company_name,
            content=cover_letter.content,
            tone=cover_letter.tone,
            word_count=cover_letter.word_count,
            created_at=cover_letter.created_at,
            updated_at=cover_letter.updated_at,
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign keys
    resume_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("resumes.id"), nullable=True)
    cover_letter_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("cover_letters.id"), nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    resume: Mapped[Optional[DBResume]] = relationship(
        "DBResume", back_populates="applications", foreign_keys=[resume_id]
    )
    cover_letter: Mapped[Optional[DBCoverLetter]] = relationship(
        "DBCoverLetter", back_populates="applications", foreign_keys=[cover_letter_id]
    )
    user: Mapped[Optional["DBUser"]] = relationship(
        "DBUser", back_populates="applications", foreign_keys=[user_id]
    )
    
    # Indexes for performance optimization
    __table_args__ = (
        Index("idx_application_status", "status"),
        Index("idx_application_company", "company"),
        Index("idx_application_created_at", "created_at"),
        Index("idx_application_updated_at", "updated_at"),
        Index("idx_application_applied_date", "applied_date"),
        Index("idx_application_follow_up_date", "follow_up_date"),
        Index("idx_application_resume_id", "resume_id"),
        Index("idx_application_company_status", "company", "status"),  # Composite index for common queries
    )
    
    def to_model(self) -> "JobApplication":
        """Convert database model to domain model."""
        from src.models.application import JobApplication
        
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
            id=application.id if application.id else None,
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
    search_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Foreign keys
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    user: Mapped[Optional["DBUser"]] = relationship(
        "DBUser", back_populates="job_searches", foreign_keys=[user_id]
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_job_search_date", "search_date"),
        Index("idx_job_search_location", "location"),
        Index("idx_job_search_user_id", "user_id"),
    )
    
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
    user_id: Mapped[Optional[str]] = mapped_column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user: Mapped[Optional["DBUser"]] = relationship(
        "DBUser", back_populates="ai_activities", foreign_keys=[user_id]
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_ai_activity_type", "activity_type"),
        Index("idx_ai_activity_created_at", "created_at"),
        Index("idx_ai_activity_success", "success"),
        Index("idx_ai_activity_user_id", "user_id"),
    )
    
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
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Foreign keys
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    user: Mapped[Optional["DBUser"]] = relationship(
        "DBUser", back_populates="file_metadata", foreign_keys=[user_id]
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_file_metadata_path", "file_path"),
        Index("idx_file_metadata_type", "file_type"),
        Index("idx_file_metadata_uploaded_at", "uploaded_at"),
        Index("idx_file_metadata_is_active", "is_active"),
        Index("idx_file_metadata_md5", "md5_hash"),
        Index("idx_file_metadata_user_id", "user_id"),
    )
    
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


class DBUser(Base):
    """Database model for users."""
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    password_reset_token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    account_locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    applications: Mapped[List["DBJobApplication"]] = relationship(
        "DBJobApplication", back_populates="user", cascade="all, delete-orphan"
    )
    resumes: Mapped[List["DBResume"]] = relationship(
        "DBResume", back_populates="user", cascade="all, delete-orphan"
    )
    cover_letters: Mapped[List["DBCoverLetter"]] = relationship(
        "DBCoverLetter", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[List["DBUserSession"]] = relationship(
        "DBUserSession", back_populates="user", cascade="all, delete-orphan"
    )
    job_searches: Mapped[List["DBJobSearch"]] = relationship(
        "DBJobSearch", back_populates="user", cascade="all, delete-orphan"
    )
    ai_activities: Mapped[List["DBAIActivity"]] = relationship(
        "DBAIActivity", back_populates="user", cascade="all, delete-orphan"
    )
    file_metadata: Mapped[List["DBFileMetadata"]] = relationship(
        "DBFileMetadata", back_populates="user", cascade="all, delete-orphan"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_created_at", "created_at"),
        Index("idx_user_is_active", "is_active"),
    )
    
    def to_model(self) -> UserModel:
        """Convert database model to domain model."""
        return UserModel(
            id=self.id,
            email=self.email,
            password_hash=self.password_hash,
            name=self.name,
            password_reset_token=self.password_reset_token,
            password_reset_token_expires=self.password_reset_token_expires,
            is_active=self.is_active,
            failed_login_attempts=self.failed_login_attempts or 0,
            account_locked_until=self.account_locked_until,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
    
    @classmethod
    def from_model(cls, user: UserModel) -> "DBUser":
        """Create database model from domain model."""
        return cls(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            name=user.name,
            is_active=user.is_active,
            failed_login_attempts=user.failed_login_attempts or 0,
            account_locked_until=user.account_locked_until,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class DBUserSession(Base):
    """Database model for user sessions (refresh tokens)."""
    
    __tablename__ = "user_sessions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    user: Mapped["DBUser"] = relationship("DBUser", back_populates="sessions")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_session_user_id", "user_id"),
        Index("idx_session_refresh_token", "refresh_token"),
        Index("idx_session_expires_at", "expires_at"),
        Index("idx_session_is_active", "is_active"),
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "last_used_at": self.last_used_at.isoformat(),
            "is_active": self.is_active,
        }


class DBPerformanceMetric(Base):
    """Database model for performance metrics."""
    
    __tablename__ = "performance_metrics"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_metric_name_timestamp", "metric_name", "timestamp"),
        Index("idx_metric_timestamp", "timestamp"),
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        import json
        
        return {
            "id": self.id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "tags": json.loads(self.tags) if self.tags else {},
            "timestamp": self.timestamp.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


class DBErrorLog(Base):
    """Database model for error logs."""
    
    __tablename__ = "error_logs"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    error_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    http_method: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # error, warning, critical
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_error_type_severity", "error_type", "severity"),
        Index("idx_error_created_at", "created_at"),
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "request_path": self.request_path,
            "http_method": self.http_method,
            "user_id": self.user_id,
            "severity": self.severity,
            "created_at": self.created_at.isoformat(),
        }


class DBAlertRule(Base):
    """Database model for alert rules."""
    
    __tablename__ = "alert_rules"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    condition: Mapped[str] = mapped_column(String(20), nullable=False)  # gt, gte, lt, lte, eq
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=300)  # 5 minutes default
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_alert_rule_metric_enabled", "metric_name", "enabled"),
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "rule_name": self.rule_name,
            "metric_name": self.metric_name,
            "threshold": self.threshold,
            "condition": self.condition,
            "enabled": self.enabled,
            "cooldown_seconds": self.cooldown_seconds,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class DBAlertHistory(Base):
    """Database model for alert history."""
    
    __tablename__ = "alert_history"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_rule_id: Mapped[str] = mapped_column(String, ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class DBConfig(Base):
    """Database model for application configuration (key-value store)."""
    
    __tablename__ = "configs"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
