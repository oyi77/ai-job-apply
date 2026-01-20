# API Endpoints: Detailed Reference

> **Comprehensive API endpoint documentation with implementation details**

This document provides complete details for all API endpoints including request/response schemas, validation rules, error handling, and implementation locations.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`
- **API Version**: `/api/v1`

## Authentication

Most endpoints require JWT authentication. Include token in Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Response Format

All responses follow this structure:

```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Success message",
  "timestamp": "2026-01-20T14:00:00Z"
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information",
  "code": "ERROR_CODE"
}
```

## Endpoints by Category

### Authentication (`/api/v1/auth`)

**Implementation**: `backend/src/api/v1/auth.py`  
**Service**: `backend/src/services/auth_service.py`

#### POST `/auth/register`

Register a new user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response** (201):
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2026-01-20T14:00:00Z"
}
```

**Errors**:
- `400`: Email already exists
- `422`: Validation error (weak password, invalid email)

---

#### POST `/auth/login`

Authenticate user and get tokens.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Errors**:
- `401`: Invalid credentials
- `403`: Account inactive

---

### Applications (`/api/v1/applications`)

**Implementation**: `backend/src/api/v1/applications.py`  
**Service**: `backend/src/services/application_service.py`  
**Repository**: `backend/src/database/repositories/application_repository.py`

#### GET `/applications`

List all applications for authenticated user.

**Query Parameters**:
- `skip` (int, default: 0): Pagination offset
- `limit` (int, default: 100): Max results
- `status` (string, optional): Filter by status
- `search` (string, optional): Search in company/position

**Response** (200):
```json
{
  "items": [
    {
      "id": "app_123",
      "company_name": "TechCorp",
      "position_title": "Senior Developer",
      "status": "submitted",
      "applied_date": "2026-01-15",
      "resume_id": "res_456",
      "cover_letter_id": "cl_789",
      "created_at": "2026-01-15T10:00:00Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 100
}
```

**curl Example**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/applications?status=submitted&limit=10"
```

---

#### POST `/applications`

Create a new application.

**Request**:
```json
{
  "company_name": "TechCorp",
  "position_title": "Senior Developer",
  "job_description": "We are looking for...",
  "status": "draft",
  "resume_id": "res_456",
  "cover_letter_id": "cl_789",
  "job_url": "https://example.com/job/123",
  "notes": "Applied through LinkedIn"
}
```

**Validation**:
- `company_name`: Required, 1-255 chars
- `position_title`: Required, 1-255 chars
- `status`: Must be valid status (draft, submitted, etc.)
- `resume_id`: Must exist and belong to user
- `job_url`: Must be valid URL if provided

**Response** (201):
```json
{
  "id": "app_123",
  "company_name": "TechCorp",
  "position_title": "Senior Developer",
  "status": "draft",
  "created_at": "2026-01-20T14:00:00Z"
}
```

**Errors**:
- `400`: Invalid status or resume not found
- `422`: Validation error

---

### Resumes (`/api/v1/resumes`)

**Implementation**: `backend/src/api/v1/resumes.py`  
**Service**: `backend/src/services/resume_service.py`

#### POST `/resumes/upload`

Upload a new resume file.

**Request** (multipart/form-data):
```
file: <resume.pdf>
title: "Senior Developer Resume"
```

**Validation**:
- File types: `.pdf`, `.docx`, `.txt`
- Max size: 10MB
- File must be readable

**Response** (201):
```json
{
  "id": "res_123",
  "filename": "resume.pdf",
  "title": "Senior Developer Resume",
  "file_size": 245678,
  "content_preview": "John Doe\nSenior Developer...",
  "skills": ["Python", "FastAPI", "React"],
  "created_at": "2026-01-20T14:00:00Z"
}
```

**curl Example**:
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@resume.pdf" \
  -F "title=My Resume" \
  http://localhost:8000/api/v1/resumes/upload
```

---

### AI Services (`/api/v1/ai`)

**Implementation**: `backend/src/api/v1/ai.py`  
**Service**: `backend/src/services/gemini_ai_service.py`

#### POST `/ai/optimize-resume`

Optimize resume for a specific job.

**Request**:
```json
{
  "resume_id": "res_123",
  "job_description": "We need a Python developer with FastAPI experience...",
  "target_role": "Senior Python Developer",
  "company_name": "TechCorp"
}
```

**Response** (200):
```json
{
  "optimized_content": "Improved resume text...",
  "suggestions": [
    "Add more FastAPI projects",
    "Highlight async programming skills"
  ],
  "confidence_score": 0.85,
  "keywords_added": ["async", "FastAPI", "microservices"],
  "ai_model": "gemini-1.5-flash"
}
```

**Errors**:
- `404`: Resume not found
- `503`: AI service unavailable (returns fallback)

---

### Job Search (`/api/v1/jobs`)

**Implementation**: `backend/src/api/v1/jobs.py`  
**Service**: `backend/src/services/job_search_service.py`

#### POST `/jobs/search`

Search for jobs across multiple platforms.

**Request**:
```json
{
  "keywords": ["python", "developer"],
  "location": "Remote",
  "experience_level": "mid",
  "job_type": "fulltime",
  "results_wanted": 20,
  "platforms": ["linkedin", "indeed"]
}
```

**Response** (200):
```json
{
  "jobs": [
    {
      "id": "job_123",
      "title": "Python Developer",
      "company": "TechCorp",
      "location": "Remote",
      "description": "We are looking for...",
      "url": "https://linkedin.com/jobs/123",
      "posted_date": "2026-01-18",
      "source": "linkedin"
    }
  ],
  "total_jobs": 45,
  "search_metadata": {
    "platforms_searched": ["linkedin", "indeed"],
    "search_time_ms": 1250
  }
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `CONFLICT` | 409 | Resource conflict (duplicate) |
| `RATE_LIMIT` | 429 | Too many requests |
| `SERVER_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | External service unavailable |

## Rate Limiting

- **Default**: 100 requests per minute per user
- **AI endpoints**: 10 requests per minute
- **File uploads**: 5 requests per minute

## Pagination

All list endpoints support pagination:

```
GET /api/v1/applications?skip=20&limit=10
```

Response includes pagination metadata:
```json
{
  "items": [...],
  "total": 100,
  "skip": 20,
  "limit": 10,
  "has_more": true
}
```

## Testing Endpoints

Use Swagger UI for interactive testing:
```
http://localhost:8000/docs
```

Or use the provided Postman collection:
```
docs/postman_collection.json
```

---

**Last Updated**: 2026-01-20  
**API Version**: v1  
**For complete implementation details, see**: [08-codebase-map.md](./08-codebase-map.md)
