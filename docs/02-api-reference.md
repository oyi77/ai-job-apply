# API Reference Documentation

**Base URL**: `http://localhost:8000` (development)  
**API Version**: v1  
**Documentation**: `/docs` (Swagger UI when DEBUG=true)

## Authentication

Currently, the API does not require authentication. Future versions will implement JWT-based authentication.

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... }
}
```

## Endpoints

### Health & Status

#### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

#### GET /api/v1/ai/health
AI service health check.

**Response**:
```json
{
  "status": "healthy",
  "available": true,
  "model": "gemini-1.5-flash"
}
```

---

### Applications

#### GET /api/v1/applications
List all job applications.

**Query Parameters**:
- `status` (string, optional): Filter by status
- `company` (string, optional): Filter by company
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 10)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "app_123",
      "job_id": "job_456",
      "job_title": "Software Engineer",
      "company": "Tech Corp",
      "status": "under_review",
      "applied_date": "2025-01-15T10:00:00Z",
      "created_at": "2025-01-15T09:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 10
}
```

#### GET /api/v1/applications/{id}
Get a specific application.

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "app_123",
    "job_id": "job_456",
    "job_title": "Software Engineer",
    "company": "Tech Corp",
    "status": "under_review",
    "resume_path": "/resumes/resume_123.pdf",
    "cover_letter_path": "/cover-letters/letter_123.txt",
    "notes": "Applied through company website",
    "applied_date": "2025-01-15T10:00:00Z",
    "follow_up_date": "2025-01-22T10:00:00Z",
    "interview_date": null,
    "created_at": "2025-01-15T09:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
}
```

#### POST /api/v1/applications
Create a new application.

**Request Body**:
```json
{
  "job_id": "job_456",
  "job_title": "Software Engineer",
  "company": "Tech Corp",
  "status": "draft",
  "notes": "Initial application"
}
```

**Response**: Application object (same as GET)

#### PUT /api/v1/applications/{id}
Update an application.

**Request Body**:
```json
{
  "status": "submitted",
  "notes": "Updated notes",
  "applied_date": "2025-01-15T10:00:00Z"
}
```

**Response**: Updated application object

#### DELETE /api/v1/applications/{id}
Delete an application.

**Response**:
```json
{
  "success": true,
  "message": "Application deleted successfully"
}
```

#### GET /api/v1/applications/stats
Get application statistics.

**Response**:
```json
{
  "success": true,
  "data": {
    "total": 10,
    "by_status": {
      "draft": 2,
      "submitted": 3,
      "under_review": 2,
      "interview_scheduled": 1,
      "offer_received": 1,
      "rejected": 1
    },
    "success_rate": 0.1,
    "average_response_time": 5.5
  }
}
```

---

### Resumes

#### GET /api/v1/resumes
List all resumes.

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "resume_123",
      "name": "John Doe Resume",
      "file_path": "/resumes/resume_123.pdf",
      "file_type": "pdf",
      "is_default": true,
      "skills": ["Python", "React", "TypeScript"],
      "experience_years": 5,
      "created_at": "2025-01-10T10:00:00Z",
      "updated_at": "2025-01-10T10:00:00Z"
    }
  ]
}
```

#### GET /api/v1/resumes/{id}
Get a specific resume.

**Response**: Resume object (same structure as list)

#### POST /api/v1/resumes/upload
Upload a new resume.

**Request**: `multipart/form-data`
- `file` (file, required): Resume file (PDF, DOCX, or TXT)
- `metadata` (string, optional): JSON metadata

**Response**: Created resume object

#### PUT /api/v1/resumes/{id}
Update resume metadata.

**Request Body**:
```json
{
  "name": "Updated Resume Name",
  "skills": ["Python", "React", "TypeScript", "Node.js"]
}
```

**Response**: Updated resume object

#### DELETE /api/v1/resumes/{id}
Delete a resume.

**Response**:
```json
{
  "success": true,
  "message": "Resume deleted successfully"
}
```

#### PATCH /api/v1/resumes/{id}/default
Set resume as default.

**Response**: Updated resume object with `is_default: true`

---

### Cover Letters

#### GET /api/v1/cover-letters
List all cover letters.

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "letter_123",
      "job_title": "Software Engineer",
      "company_name": "Tech Corp",
      "content": "Dear Hiring Manager...",
      "tone": "professional",
      "word_count": 350,
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

#### GET /api/v1/cover-letters/{id}
Get a specific cover letter.

**Response**: Cover letter object

#### POST /api/v1/cover-letters
Create a new cover letter.

**Request Body**:
```json
{
  "job_title": "Software Engineer",
  "company_name": "Tech Corp",
  "content": "Dear Hiring Manager...",
  "tone": "professional",
  "word_count": 350
}
```

**Response**: Created cover letter object

#### PUT /api/v1/cover-letters/{id}
Update a cover letter.

**Request Body**:
```json
{
  "content": "Updated content...",
  "word_count": 400
}
```

**Response**: Updated cover letter object

#### DELETE /api/v1/cover-letters/{id}
Delete a cover letter.

**Response**:
```json
{
  "success": true,
  "message": "Cover letter deleted successfully"
}
```

---

### AI Services

#### POST /api/v1/ai/optimize-resume
Optimize resume for a specific job.

**Request Body**:
```json
{
  "resume_id": "resume_123",
  "job_description": "We are looking for a Python developer...",
  "target_role": "Senior Python Developer",
  "company_name": "Tech Corp"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "optimized_content": "Optimized resume content...",
    "suggestions": [
      "Add more Python-specific projects",
      "Highlight leadership experience",
      "Include relevant certifications"
    ],
    "confidence_score": 0.85,
    "improvements": {
      "skills_match": 0.9,
      "experience_match": 0.8,
      "overall_match": 0.85
    }
  }
}
```

#### POST /api/v1/ai/generate-cover-letter
Generate a cover letter using AI.

**Request Body**:
```json
{
  "job_title": "Software Engineer",
  "company_name": "Tech Corp",
  "job_description": "We are looking for...",
  "resume_summary": "Experienced Python developer...",
  "tone": "professional"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "content": "Dear Hiring Manager...",
    "word_count": 350,
    "tone": "professional",
    "generated_at": "2025-01-15T10:00:00Z"
  }
}
```

#### POST /api/v1/ai/analyze-match
Analyze job-resume compatibility.

**Request Body**:
```json
{
  "resume_id": "resume_123",
  "job_description": "We are looking for..."
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "match_score": 0.85,
    "suggestions": [
      "Add more relevant experience",
      "Highlight specific skills"
    ],
    "strengths": [
      "Strong Python experience",
      "Relevant certifications"
    ],
    "weaknesses": [
      "Limited leadership experience",
      "Missing specific technology"
    ]
  }
}
```

#### POST /api/v1/ai/extract-skills
Extract skills from text.

**Request Body**:
```json
{
  "text": "Experienced Python developer with React and TypeScript..."
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "skills": ["Python", "React", "TypeScript"],
    "confidence": 0.9
  }
}
```

---

### Job Search

#### POST /api/v1/jobs/search
Search for jobs across multiple platforms.

**Request Body**:
```json
{
  "keywords": ["Python", "developer"],
  "location": "Remote",
  "experience_level": "mid",
  "job_type": "full-time",
  "is_remote": true,
  "results_wanted": 20,
  "sort_by": "relevance",
  "sort_order": "desc"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "total_jobs": 50,
    "jobs": {
      "linkedin": [
        {
          "id": "job_123",
          "title": "Python Developer",
          "company": "Tech Corp",
          "location": "Remote",
          "url": "https://linkedin.com/jobs/123",
          "description": "Job description...",
          "posted_date": "2025-01-15T10:00:00Z"
        }
      ],
      "indeed": [ ... ],
      "glassdoor": [ ... ]
    }
  }
}
```

#### GET /api/v1/jobs/{id}
Get job details.

**Query Parameters**:
- `platform` (string, optional): Job platform

**Response**: Job object with full details

#### GET /api/v1/jobs/sources
Get available job search sources.

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "name": "LinkedIn",
      "available": true
    },
    {
      "name": "Indeed",
      "available": true
    }
  ]
}
```

---

## Error Codes

### HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "details": {
    "field": "Specific error details"
  }
}
```

## Rate Limiting

Currently, there is no rate limiting. Future versions will implement rate limiting per API key.

## Pagination

List endpoints support pagination:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)

Response includes:
- `total`: Total number of items
- `page`: Current page number
- `limit`: Items per page

---

**API Status**: Production-ready, all endpoints functional

