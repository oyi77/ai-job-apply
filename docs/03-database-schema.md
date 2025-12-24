# Database Schema Documentation

## Overview

The application uses SQLAlchemy 2.0 with async support. The database schema is designed with proper normalization, relationships, and indexing for optimal performance.

## Database Configuration

### Development
- **Database**: SQLite (`sqlite:///./job_applications.db`)
- **Location**: `backend/ai_job_assistant.db`

### Production
- **Database**: PostgreSQL
- **Connection**: Configured via `DATABASE_URL` environment variable

## Schema Diagram

```
┌──────────────┐         ┌──────────────────┐         ┌──────────────┐
│   resumes    │         │ job_applications  │         │cover_letters │
├──────────────┤         ├──────────────────┤         ├──────────────┤
│ id (PK)      │◄──┐     │ id (PK)          │     ┌──►│ id (PK)      │
│ name         │   │     │ job_id           │     │   │ job_title    │
│ file_path    │   │     │ job_title        │     │   │ company_name │
│ file_type    │   │     │ company          │     │   │ content      │
│ content      │   │     │ status           │     │   │ tone         │
│ skills       │   │     │ resume_id (FK)   ├─────┘   │ word_count   │
│ experience   │   │     │ cover_letter_id  │         │ created_at   │
│ education    │   │     │                  │         │ updated_at   │
│ certifications│  │     │ applied_date     │         └──────────────┘
│ is_default   │   │     │ notes            │
│ created_at   │   │     │ follow_up_date   │
│ updated_at   │   │     │ interview_date   │
└──────────────┘   │     │ created_at       │
                   │     │ updated_at       │
                   └─────┤                  │
                         └──────────────────┘
                                  │
                         ┌────────▼────────┐
                         │  job_searches   │
                         ├─────────────────┤
                         │ id (PK)         │
                         │ query           │
                         │ location        │
                         │ results_count   │
                         │ created_at      │
                         └─────────────────┘
```

## Tables

### resumes

Stores resume files and metadata.

**Columns**:
- `id` (String, PK): Unique identifier (UUID)
- `name` (String, 255): Resume name
- `file_path` (String, 500): Path to resume file
- `file_type` (String, 10): File type (pdf, docx, txt)
- `content` (Text, nullable): Extracted text content
- `skills` (Text, nullable): JSON array of skills
- `experience_years` (Integer, nullable): Years of experience
- `education` (Text, nullable): JSON array of education
- `certifications` (Text, nullable): JSON array of certifications
- `is_default` (Boolean, default: false): Default resume flag
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Indexes**:
- Primary key on `id`
- Index on `is_default` (for default resume queries)

**Relationships**:
- One-to-Many with `job_applications` (resume_id)

**Example**:
```python
{
  "id": "resume_123",
  "name": "John Doe Resume",
  "file_path": "/resumes/resume_123.pdf",
  "file_type": "pdf",
  "content": "John Doe\nSoftware Engineer...",
  "skills": '["Python", "React", "TypeScript"]',
  "experience_years": 5,
  "education": '[{"degree": "BS Computer Science", "school": "University", "year": 2020}]',
  "certifications": '["AWS Certified", "Python Certification"]',
  "is_default": true,
  "created_at": "2025-01-10T10:00:00Z",
  "updated_at": "2025-01-10T10:00:00Z"
}
```

### cover_letters

Stores generated cover letters.

**Columns**:
- `id` (String, PK): Unique identifier (UUID)
- `job_title` (String, 255): Job title
- `company_name` (String, 255): Company name
- `content` (Text): Cover letter content
- `tone` (String, 50): Tone (professional, friendly, formal)
- `word_count` (Integer): Word count
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Indexes**:
- Primary key on `id`
- Index on `company_name` (for filtering)

**Relationships**:
- One-to-Many with `job_applications` (cover_letter_id)

**Example**:
```python
{
  "id": "letter_123",
  "job_title": "Software Engineer",
  "company_name": "Tech Corp",
  "content": "Dear Hiring Manager,\n\nI am writing...",
  "tone": "professional",
  "word_count": 350,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

### job_applications

Tracks job applications throughout their lifecycle.

**Columns**:
- `id` (String, PK): Unique identifier (UUID)
- `job_id` (String): Associated job ID
- `job_title` (String, 255): Job title
- `company` (String, 255): Company name
- `status` (Enum): Application status
  - draft
  - submitted
  - under_review
  - interview_scheduled
  - interview_completed
  - offer_received
  - offer_accepted
  - offer_declined
  - rejected
  - withdrawn
- `resume_id` (String, FK, nullable): Associated resume
- `cover_letter_id` (String, FK, nullable): Associated cover letter
- `applied_date` (DateTime, nullable): Application submission date
- `notes` (Text, nullable): Application notes
- `follow_up_date` (DateTime, nullable): Follow-up reminder date
- `interview_date` (DateTime, nullable): Interview date
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Indexes**:
- Primary key on `id`
- Index on `status` (for filtering)
- Index on `company` (for search)
- Index on `applied_date` (for sorting)
- Foreign key on `resume_id`
- Foreign key on `cover_letter_id`

**Relationships**:
- Many-to-One with `resumes` (resume_id)
- Many-to-One with `cover_letters` (cover_letter_id)

**Example**:
```python
{
  "id": "app_123",
  "job_id": "job_456",
  "job_title": "Software Engineer",
  "company": "Tech Corp",
  "status": "under_review",
  "resume_id": "resume_123",
  "cover_letter_id": "letter_123",
  "applied_date": "2025-01-15T10:00:00Z",
  "notes": "Applied through company website",
  "follow_up_date": "2025-01-22T10:00:00Z",
  "interview_date": null,
  "created_at": "2025-01-15T09:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

### job_searches

Tracks job search history and analytics.

**Columns**:
- `id` (String, PK): Unique identifier (UUID)
- `query` (String, 500): Search query
- `location` (String, 255, nullable): Search location
- `experience_level` (String, 50, nullable): Experience level filter
- `job_type` (String, 50, nullable): Job type filter
- `results_count` (Integer): Number of results found
- `platforms_searched` (Text, nullable): JSON array of platforms
- `created_at` (DateTime): Search timestamp

**Indexes**:
- Primary key on `id`
- Index on `created_at` (for sorting)

**Example**:
```python
{
  "id": "search_123",
  "query": "Python developer",
  "location": "Remote",
  "experience_level": "mid",
  "job_type": "full-time",
  "results_count": 50,
  "platforms_searched": '["LinkedIn", "Indeed", "Glassdoor"]',
  "created_at": "2025-01-15T10:00:00Z"
}
```

### ai_activities

Tracks AI service usage and operations.

**Columns**:
- `id` (String, PK): Unique identifier (UUID)
- `operation_type` (String, 50): Type of operation
  - optimize_resume
  - generate_cover_letter
  - analyze_match
  - extract_skills
- `input_data` (Text, nullable): JSON input data
- `output_data` (Text, nullable): JSON output data
- `model_used` (String, 100, nullable): AI model used
- `response_time_ms` (Integer, nullable): Response time in milliseconds
- `success` (Boolean): Operation success status
- `error_message` (Text, nullable): Error message if failed
- `created_at` (DateTime): Operation timestamp

**Indexes**:
- Primary key on `id`
- Index on `operation_type` (for analytics)
- Index on `created_at` (for time-based queries)
- Index on `success` (for error tracking)

**Example**:
```python
{
  "id": "ai_123",
  "operation_type": "optimize_resume",
  "input_data": '{"resume_id": "resume_123", "job_description": "..."}',
  "output_data": '{"suggestions": [...], "confidence_score": 0.85}',
  "model_used": "gemini-1.5-flash",
  "response_time_ms": 2500,
  "success": true,
  "error_message": null,
  "created_at": "2025-01-15T10:00:00Z"
}
```

### file_metadata

Tracks file uploads and metadata.

**Columns**:
- `id` (String, PK): Unique identifier (UUID)
- `filename` (String, 255): Original filename
- `file_path` (String, 500): Stored file path
- `file_type` (String, 10): File type/extension
- `file_size` (Integer): File size in bytes
- `mime_type` (String, 100): MIME type
- `category` (String, 50): File category (resume, cover_letter, other)
- `uploaded_by` (String, nullable): User identifier (future)
- `created_at` (DateTime): Upload timestamp
- `updated_at` (DateTime): Last update timestamp

**Indexes**:
- Primary key on `id`
- Index on `category` (for filtering)
- Index on `created_at` (for sorting)

**Example**:
```python
{
  "id": "file_123",
  "filename": "resume.pdf",
  "file_path": "/uploads/resume_123.pdf",
  "file_type": "pdf",
  "file_size": 245760,
  "mime_type": "application/pdf",
  "category": "resume",
  "uploaded_by": null,
  "created_at": "2025-01-10T10:00:00Z",
  "updated_at": "2025-01-10T10:00:00Z"
}
```

## Relationships

### One-to-Many
- **Resume → Applications**: One resume can be used for multiple applications
- **Cover Letter → Applications**: One cover letter can be used for multiple applications

### Foreign Keys
- `job_applications.resume_id` → `resumes.id`
- `job_applications.cover_letter_id` → `cover_letters.id`

### Cascading
- **ON DELETE CASCADE**: When a resume is deleted, associated applications are updated (resume_id set to NULL)
- **ON DELETE CASCADE**: When a cover letter is deleted, associated applications are updated (cover_letter_id set to NULL)

## Data Types

### JSON Fields
Several fields store JSON data:
- `resumes.skills`: Array of skill strings
- `resumes.education`: Array of education objects
- `resumes.certifications`: Array of certification strings
- `job_searches.platforms_searched`: Array of platform strings
- `ai_activities.input_data`: JSON object
- `ai_activities.output_data`: JSON object

### Enums
- `job_applications.status`: ApplicationStatus enum (10 values)

## Migrations

### Migration Tool
- **Alembic**: Database migration management
- **Location**: `backend/alembic/versions/`
- **Initial Migration**: `3842c06f2231_initial_migration.py`

### Migration Process
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Performance Considerations

### Indexes
- All primary keys are indexed
- Foreign keys are indexed
- Frequently queried fields are indexed (status, company, created_at)

### Query Optimization
- Use `selectinload()` for relationship loading
- Avoid N+1 queries with proper joins
- Use pagination for large result sets

### Connection Pooling
- PostgreSQL: Connection pooling configured
- SQLite: Single connection (development only)

## Backup & Recovery

### Backup Strategy
- **Development**: SQLite file backup
- **Production**: PostgreSQL automated backups (future)

### Recovery
- Restore from backup file
- Re-run migrations if needed

---

**Schema Status**: Production-ready, fully normalized, optimized for performance

