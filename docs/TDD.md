# Technical Design Document (TDD)
## AI Job Application Assistant

**Version**: 1.0.0  
**Last Updated**: 2025-01-21  
**Status**: Production Ready

---

## 1. Document Overview

### 1.1 Purpose
This document provides comprehensive technical specifications for the AI Job Application Assistant, including system architecture, component design, data models, API specifications, and implementation details.

### 1.2 Scope
This TDD covers:
- System architecture and design patterns
- Component specifications
- Database schema and data models
- API endpoints and contracts
- Service layer architecture
- Security implementation
- Performance considerations
- Testing strategy

### 1.3 Audience
- Software engineers
- System architects
- DevOps engineers
- QA engineers
- Technical leads

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  React   │  │ TypeScript│  │ Tailwind  │  │  Zustand  │  │
│  │  19      │  │   5.8     │  │    CSS   │  │  + React  │  │
│  │          │  │           │  │   3.4    │  │  Query   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  Port: 5173 (Dev) | Static Build (Production)              │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
                       │ JWT Authentication
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Backend Layer (FastAPI)                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │              API Layer (v1)                        │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐         │    │
│  │  │  Auth    │ │Applications│ │   AI     │         │    │
│  │  │  Jobs    │ │ Resumes   │ │CoverLetter│         │    │
│  │  └──────────┘ └──────────┘ └──────────┘         │    │
│  └────────────────────────────────────────────────────┘    │
│                       │                                     │
│  ┌────────────────────▼────────────────────────────────┐  │
│  │            Service Layer                             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │
│  │  │  AI      │ │Application│ │  File    │          │  │
│  │  │  Auth    │ │ Resume    │ │  Job     │          │  │
│  │  │ Service  │ │ Service   │ │  Search  │          │  │
│  │  └──────────┘ └──────────┘ └──────────┘          │  │
│  └────────────────────┬────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼────────────────────────────────┐  │
│  │         Repository Layer                             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │
│  │  │Application│ │ Resume   │ │CoverLetter│          │  │
│  │  │User      │ │ User     │ │  File    │          │  │
│  │  │Repository│ │Repository│ │Repository│          │  │
│  │  └──────────┘ └──────────┘ └──────────┘          │  │
│  └────────────────────┬────────────────────────────────┘  │
│                       │                                     │
│  Port: 8000 (Dev) | Uvicorn (Production)                   │
└───────────────────────┼─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  PostgreSQL  │ │  File System│ │ Gemini API │
│  (Database)  │ │  (Storage)  │ │  (AI)      │
│              │ │             │ │            │
│  SQLite      │ │  Local      │ │  JobSpy    │
│  (Dev/Test)  │ │  Storage    │ │  (Jobs)    │
└──────────────┘ └─────────────┘ └────────────┘
```

### 2.2 Architecture Patterns

#### 2.2.1 Layered Architecture
- **API Layer**: Request/response handling, validation, routing
- **Service Layer**: Business logic, orchestration, external integrations
- **Repository Layer**: Data access, query optimization, transaction management
- **Model Layer**: Domain models (Pydantic) and persistence models (SQLAlchemy)

#### 2.2.2 Design Patterns
- **Repository Pattern**: Data access abstraction
- **Service Registry Pattern**: Dependency injection and lifecycle management
- **Dependency Injection**: Loose coupling through constructor injection
- **Factory Pattern**: Service and repository creation
- **Strategy Pattern**: AI provider selection

---

## 3. Component Specifications

### 3.1 Backend Components

#### 3.1.1 API Layer (`backend/src/api/`)

**FastAPI Application** (`app.py`):
```python
# Key responsibilities:
- Application factory pattern
- CORS middleware configuration
- Router registration
- Health check endpoints
- Static file serving
- Startup/shutdown event handlers
```

**API Routers** (`v1/`):
- `auth.py`: Authentication endpoints (register, login, refresh, logout, profile)
- `applications.py`: Application CRUD operations
- `resumes.py`: Resume upload and management
- `cover_letters.py`: Cover letter operations
- `ai.py`: AI service endpoints (optimize, generate, analyze)
- `jobs.py`: Job search endpoints
- `job_applications.py`: Job application workflow

**Dependencies** (`dependencies.py`):
- `get_current_user`: JWT token validation and user extraction
- `get_optional_user`: Optional authentication for public endpoints

---

#### 3.1.2 Service Layer (`backend/src/services/`)

**Service Registry** (`service_registry.py`):
```python
class ServiceRegistry:
    """Centralized service management with dependency injection."""
    
    async def initialize() -> None
    async def get_ai_service() -> AIService
    async def get_auth_service() -> AuthService
    async def get_resume_service() -> ResumeService
    async def get_application_service() -> ApplicationService
    async def health_check() -> Dict[str, Any]
    async def cleanup() -> None
```

**Core Services**:

1. **AuthService** (`auth_service.py`):
   - User registration and authentication
   - JWT token generation and validation
   - Password hashing (bcrypt)
   - Token refresh mechanism
   - User profile management

2. **GeminiAIService** (`gemini_ai_service.py`):
   - Resume optimization
   - Cover letter generation
   - Job match analysis
   - Skills extraction
   - Graceful fallback when unavailable

3. **ResumeService** (`resume_service.py`):
   - Resume upload and processing
   - Text extraction (PDF, DOCX, TXT)
   - Skills and experience extraction
   - Default resume management

4. **ApplicationService** (`application_service.py`):
   - Application lifecycle management
   - Status tracking and transitions
   - Statistics and analytics
   - Follow-up scheduling

5. **JobSearchService** (`job_search_service.py`):
   - Multi-platform job search
   - JobSpy integration
   - Fallback implementations
   - Retry logic and error handling

6. **LocalFileService** (`local_file_service.py`):
   - Secure file operations
   - File validation and sanitization
   - Directory management
   - File metadata tracking

---

#### 3.1.3 Repository Layer (`backend/src/database/repositories/`)

**Repository Pattern**:
```python
class ApplicationRepository:
    """Data access for job applications."""
    
    async def create(application: JobApplication) -> JobApplication
    async def get_by_id(id: str) -> Optional[JobApplication]
    async def get_all() -> List[JobApplication]
    async def get_by_status(status: ApplicationStatus) -> List[JobApplication]
    async def update(id: str, updates: Dict) -> Optional[JobApplication]
    async def delete(id: str) -> bool
    async def get_statistics() -> Dict[str, Any]
```

**Repositories**:
- `application_repository.py`: Application data access
- `resume_repository.py`: Resume data access
- `cover_letter_repository.py`: Cover letter data access
- `user_repository.py`: User data access
- `user_session_repository.py`: Session data access
- `file_repository.py`: File metadata access

**Query Performance**:
- All repository methods decorated with `@monitor_query_performance`
- Strategic database indexes
- Efficient relationship loading with `selectinload`

---

#### 3.1.4 Database Models (`backend/src/database/models.py`)

**SQLAlchemy Models**:
- `DBUser`: User accounts and authentication
- `DBUserSession`: Refresh token sessions
- `DBResume`: Resume storage and metadata
- `DBCoverLetter`: Cover letter content
- `DBJobApplication`: Application tracking
- `DBJobSearch`: Search history
- `DBAIActivity`: AI operation logs
- `DBFileMetadata`: File tracking

**Relationships**:
- Users → Applications (One-to-Many)
- Users → Resumes (One-to-Many)
- Users → Cover Letters (One-to-Many)
- Users → Sessions (One-to-Many)
- Applications → Resumes (Many-to-One)
- Applications → Cover Letters (Many-to-One)

**Indexes**:
- Primary keys on all tables
- Foreign key indexes
- Composite indexes for common queries
- Status and date indexes for filtering

---

#### 3.1.5 Domain Models (`backend/src/models/`)

**Pydantic Models**:
- `user.py`: User, UserProfile, UserRegister, UserLogin, TokenResponse
- `application.py`: JobApplication, ApplicationStatus, ApplicationUpdateRequest
- `resume.py`: Resume, ResumeOptimizationRequest, ResumeOptimizationResponse
- `cover_letter.py`: CoverLetter, CoverLetterRequest, CoverLetterResponse
- `job.py`: Job, JobSearchRequest, JobSearchResponse

**Validation**:
- Email validation (EmailStr)
- Password strength validation
- File type and size validation
- Date and datetime validation

---

### 3.2 Frontend Components

#### 3.2.1 Application Structure

**Pages** (`frontend/src/pages/`):
- `Dashboard.tsx`: Overview and statistics
- `Applications.tsx`: Application list and management
- `Resumes.tsx`: Resume upload and management
- `CoverLetters.tsx`: Cover letter management
- `JobSearch.tsx`: Job search interface
- `AIServices.tsx`: AI feature access
- `Analytics.tsx`: Analytics and reporting
- `Settings.tsx`: User settings
- `Login.tsx`: User login
- `Register.tsx`: User registration
- `NotFound.tsx`: 404 page

**Components** (`frontend/src/components/`):
- `ui/`: Base UI components (Button, Input, Card, Modal, etc.)
- `forms/`: Form components (Form, FormField)
- `layout/`: Layout components (Header, Sidebar, Layout)
- `auth/`: Authentication components (ProtectedRoute)

**State Management**:
- `stores/appStore.ts`: Zustand store for client state
- React Query: Server state and caching
- Local state: Component-specific state

**Services**:
- `services/api.ts`: Axios-based API client with interceptors

---

#### 3.2.2 API Client Architecture

**Axios Configuration**:
```typescript
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

// Request interceptor: Add JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: Token refresh on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Token refresh logic
    // Queue failed requests
    // Retry with new token
  }
);
```

**Service Methods**:
- `authService`: Authentication operations
- `applicationService`: Application CRUD
- `resumeService`: Resume operations
- `coverLetterService`: Cover letter operations
- `aiService`: AI feature access
- `jobSearchService`: Job search operations
- `fileService`: File operations

---

## 4. Database Design

### 4.1 Schema Overview

**Tables**:
1. `users`: User accounts
2. `user_sessions`: Refresh token sessions
3. `resumes`: Resume storage
4. `cover_letters`: Cover letter content
5. `job_applications`: Application tracking
6. `job_searches`: Search history
7. `ai_activities`: AI operation logs
8. `file_metadata`: File tracking

### 4.2 Entity Relationships

```
users (1) ──< (N) job_applications
users (1) ──< (N) resumes
users (1) ──< (N) cover_letters
users (1) ──< (N) user_sessions

job_applications (N) ──> (1) resumes
job_applications (N) ──> (1) cover_letters
```

### 4.3 Key Constraints

- **Foreign Keys**: CASCADE delete for user relationships
- **Unique Constraints**: Email addresses, refresh tokens
- **Indexes**: Performance optimization for common queries
- **Timestamps**: Automatic created_at/updated_at management

---

## 5. API Specifications

### 5.1 Authentication Endpoints

**POST `/api/v1/auth/register`**:
```json
Request: {
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}

Response: {
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**POST `/api/v1/auth/login`**:
```json
Request: {
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response: {
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**POST `/api/v1/auth/refresh`**:
```json
Request: {
  "refresh_token": "eyJ..."
}

Response: {
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**GET `/api/v1/auth/me`**:
```json
Response: {
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

---

### 5.2 Application Endpoints

**GET `/api/v1/applications`**:
- Query params: `status`, `company`, `page`, `limit`
- Response: Paginated list of applications
- Authentication: Required

**POST `/api/v1/applications`**:
- Request: Job information dictionary
- Response: Created application
- Authentication: Required

**GET `/api/v1/applications/{id}`**:
- Response: Application details
- Authentication: Required

**PUT `/api/v1/applications/{id}`**:
- Request: ApplicationUpdateRequest
- Response: Updated application
- Authentication: Required

**DELETE `/api/v1/applications/{id}`**:
- Response: Success message
- Authentication: Required

**GET `/api/v1/applications/stats`**:
- Response: Application statistics
- Authentication: Required

---

### 5.3 Resume Endpoints

**GET `/api/v1/resumes`**:
- Response: List of resumes
- Authentication: Required

**POST `/api/v1/resumes/upload`**:
- Request: Multipart form data (file, name)
- Response: Created resume
- Authentication: Required

**GET `/api/v1/resumes/{id}`**:
- Response: Resume details
- Authentication: Required

**PUT `/api/v1/resumes/{id}`**:
- Request: Resume updates
- Response: Updated resume
- Authentication: Required

**DELETE `/api/v1/resumes/{id}`**:
- Response: Success message
- Authentication: Required

---

### 5.4 AI Service Endpoints

**POST `/api/v1/ai/optimize-resume`**:
```json
Request: {
  "resume_id": "resume_123",
  "job_description": "Software Engineer position...",
  "optimization_type": "all"
}

Response: {
  "optimized_content": "...",
  "suggestions": ["Add Python experience", "..."],
  "skills_gap": ["Docker", "Kubernetes"],
  "confidence_score": 0.85
}
```

**POST `/api/v1/ai/generate-cover-letter`**:
```json
Request: {
  "job_title": "Software Engineer",
  "company": "Tech Corp",
  "job_description": "...",
  "resume_id": "resume_123",
  "tone": "professional"
}

Response: {
  "cover_letter": "...",
  "suggestions": ["..."],
  "confidence_score": 0.90
}
```

---

### 5.5 Job Search Endpoints

**POST `/api/v1/jobs/search`**:
```json
Request: {
  "keywords": ["software engineer", "python"],
  "location": "Remote",
  "experience_level": "mid",
  "job_type": "full_time",
  "is_remote": true
}

Response: {
  "jobs": {
    "linkedin": [...],
    "indeed": [...],
    "glassdoor": [...]
  },
  "total": 150,
  "sources": ["linkedin", "indeed", "glassdoor"]
}
```

---

## 6. Security Design

### 6.1 Authentication & Authorization

**JWT Implementation**:
- **Algorithm**: HS256
- **Access Token**: 30 minutes expiration
- **Refresh Token**: 7 days expiration
- **Storage**: localStorage (frontend)
- **Validation**: Token signature and expiration checks

**Password Security**:
- **Hashing**: bcrypt with salt rounds
- **Strength Requirements**: Min 8 chars, uppercase, lowercase, digit
- **Storage**: Never stored in plain text

**Session Management**:
- Refresh tokens stored in database
- Session invalidation on logout
- Automatic session cleanup for expired tokens

---

### 6.2 API Security

**Input Validation**:
- Pydantic models for all requests
- Type validation and sanitization
- File type and size validation

**CORS Configuration**:
- Configurable allowed origins
- Credentials support
- Preflight handling

**Rate Limiting** (Future):
- Per-endpoint rate limits
- Per-user rate limits
- IP-based rate limiting

---

### 6.3 Data Security

**Database Security**:
- Parameterized queries (ORM)
- SQL injection prevention
- Connection encryption (production)

**File Security**:
- File type validation
- Size limits (10MB)
- Path sanitization
- Content scanning (future)

---

## 7. Performance Design

### 7.1 Backend Performance

**Database Optimization**:
- Strategic indexes on frequently queried columns
- Composite indexes for common query patterns
- Query performance monitoring
- Connection pooling

**Caching Strategy**:
- In-memory cache for query results (SimpleCache)
- TTL-based expiration
- Cache invalidation on updates

**Async Operations**:
- All I/O operations are async
- Non-blocking database queries
- Concurrent request handling

---

### 7.2 Frontend Performance

**Code Splitting**:
- Route-based lazy loading
- Component-level code splitting
- Dynamic imports

**Bundle Optimization**:
- Tree shaking
- Minification
- Gzip compression
- Asset optimization

**Caching**:
- React Query caching (5 minutes stale time)
- Service worker for offline support (PWA)
- Browser caching for static assets

---

## 8. Error Handling

### 8.1 Backend Error Handling

**Error Types**:
- `ValidationError`: Input validation failures
- `NotFoundError`: Resource not found
- `AuthenticationError`: Authentication failures
- `AuthorizationError`: Permission denied
- `ServiceError`: External service failures

**Error Response Format**:
```json
{
  "success": false,
  "error": "Error message",
  "details": {
    "field": "validation error"
  },
  "timestamp": "2025-01-21T00:00:00Z"
}
```

**Logging**:
- Structured logging with Loguru
- Error context and stack traces
- Performance metrics

---

### 8.2 Frontend Error Handling

**Error Boundaries**:
- React ErrorBoundary component
- Graceful error display
- Error reporting

**API Error Handling**:
- Axios interceptors for error handling
- User-friendly error messages
- Retry logic for transient failures

**User Feedback**:
- Toast notifications for errors
- Loading states
- Success confirmations

---

## 9. Testing Strategy

### 9.1 Backend Testing

**Unit Tests**:
- Service layer tests
- Repository tests
- Model tests
- Utility function tests

**Integration Tests**:
- API endpoint tests
- Database integration tests
- Service interaction tests

**Test Coverage**:
- Target: 95%+ for business logic
- Framework: pytest with pytest-asyncio
- Mocking: External dependencies

---

### 9.2 Frontend Testing

**Component Tests**:
- React Testing Library
- Component rendering tests
- User interaction tests
- Accessibility tests

**Integration Tests**:
- API mocking with MSW
- User flow tests
- State management tests

**E2E Tests** (Future):
- Playwright for end-to-end testing
- Critical user journeys

---

## 10. Deployment Architecture

### 10.1 Development Environment

**Backend**:
- FastAPI dev server (uvicorn)
- Hot reload enabled
- SQLite database
- Port 8000

**Frontend**:
- Vite dev server
- Hot module replacement
- Port 5173
- Proxy to backend API

---

### 10.2 Production Environment

**Backend Deployment**:
- Docker containerization
- Uvicorn ASGI server
- Gunicorn with multiple workers (optional)
- PostgreSQL database
- Environment-based configuration

**Frontend Deployment**:
- Static build (Vite)
- CDN distribution
- Nginx reverse proxy
- Environment variables injection

**Infrastructure**:
- Load balancer (future)
- Database replication (future)
- Redis caching (future)
- Monitoring and logging (future)

---

## 11. Monitoring & Observability

### 11.1 Logging

**Backend Logging**:
- Structured logging with Loguru
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- File rotation
- Contextual information

**Frontend Logging**:
- Console logging (development)
- Error tracking (future: Sentry)
- Performance monitoring

---

### 11.2 Health Checks

**Endpoints**:
- `GET /health`: Application health
- `GET /api/v1/ai/health`: AI service health
- Service registry health checks

**Metrics** (Future):
- Response times
- Error rates
- Database query performance
- Service availability

---

## 12. Configuration Management

### 12.1 Environment Variables

**Backend** (`.env`):
```bash
# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# AI Services
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-1.5-flash

# Security
JWT_SECRET_KEY=your_secret_key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:5173,https://app.example.com
```

**Frontend** (`.env`):
```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## 13. Data Flow Diagrams

### 13.1 Application Creation Flow

```
User Action (Frontend)
    ↓
API Service Call (api.ts)
    ↓
React Query Mutation
    ↓
POST /api/v1/applications
    ↓
FastAPI Router (applications.py)
    ↓
Authentication Check (get_current_user)
    ↓
ApplicationService.create_application()
    ↓
ApplicationRepository.create()
    ↓
Database (SQLAlchemy)
    ↓
Response → Frontend
```

### 13.2 Resume Optimization Flow

```
User Action (Frontend)
    ↓
POST /api/v1/ai/optimize-resume
    ↓
AIService.optimize_resume()
    ↓
GeminiAIService.generate_content()
    ↓
Google Gemini API
    ↓
Response Processing
    ↓
Return Optimized Content
    ↓
Frontend Display
```

---

## 14. Technology Stack

### 14.1 Backend Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | 0.104+ |
| Language | Python | 3.10+ |
| Database | SQLAlchemy | 2.0 |
| ORM | SQLAlchemy Async | 2.0 |
| Validation | Pydantic | v2 |
| AI | Google Gemini | 1.5-flash |
| Job Search | JobSpy | Latest |
| Testing | pytest | Latest |
| Logging | Loguru | Latest |
| Auth | python-jose | 3.3+ |
| Password | passlib | 1.7+ |

### 14.2 Frontend Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 19 |
| Language | TypeScript | 5.8 |
| Build Tool | Vite | 7 |
| Styling | Tailwind CSS | 3.4 |
| State (Client) | Zustand | Latest |
| State (Server) | React Query | Latest |
| Forms | React Hook Form | Latest |
| Routing | React Router | v7 |
| HTTP Client | Axios | Latest |
| Testing | Vitest | Latest |
| UI Components | Headless UI | Latest |
| Icons | Heroicons | Latest |

---

## 15. API Response Standards

### 15.1 Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### 15.2 Error Response

```json
{
  "success": false,
  "error": "Error message",
  "details": { ... }
}
```

### 15.3 Paginated Response

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "total_pages": 10
  }
}
```

---

## 16. Code Quality Standards

### 16.1 Backend Standards

- **Type Hints**: 100% coverage required
- **Docstrings**: Google-style for all public APIs
- **Line Limits**: Functions (20), Classes (200), Modules (500)
- **Formatting**: Black (line length 88)
- **Linting**: flake8, mypy (strict mode)
- **Testing**: 95%+ coverage for business logic

### 16.2 Frontend Standards

- **TypeScript**: Strict mode enabled
- **Component Size**: Max 50 lines per component
- **State Management**: Clear separation (client vs server)
- **Performance**: Code splitting, memoization
- **Accessibility**: WCAG 2.1 AA compliance
- **Testing**: 90%+ coverage for components

---

## 17. Future Enhancements

### 17.1 Planned Features
- Email notifications
- Advanced analytics with ML
- Mobile application
- ATS integrations
- Performance monitoring dashboard
- Rate limiting
- CSRF protection
- Password reset flow

### 17.2 Scalability Improvements
- Redis caching
- Database read replicas
- CDN for static assets
- Horizontal scaling
- Message queue for async tasks

---

## 18. Appendices

### 18.1 API Endpoint Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | No | User registration |
| POST | `/api/v1/auth/login` | No | User login |
| POST | `/api/v1/auth/refresh` | No | Token refresh |
| POST | `/api/v1/auth/logout` | Yes | User logout |
| GET | `/api/v1/auth/me` | Yes | Get user profile |
| PUT | `/api/v1/auth/me` | Yes | Update profile |
| POST | `/api/v1/auth/change-password` | Yes | Change password |
| GET | `/api/v1/applications` | Yes | List applications |
| POST | `/api/v1/applications` | Yes | Create application |
| GET | `/api/v1/applications/{id}` | Yes | Get application |
| PUT | `/api/v1/applications/{id}` | Yes | Update application |
| DELETE | `/api/v1/applications/{id}` | Yes | Delete application |
| GET | `/api/v1/applications/stats` | Yes | Get statistics |
| GET | `/api/v1/resumes` | Yes | List resumes |
| POST | `/api/v1/resumes/upload` | Yes | Upload resume |
| GET | `/api/v1/resumes/{id}` | Yes | Get resume |
| PUT | `/api/v1/resumes/{id}` | Yes | Update resume |
| DELETE | `/api/v1/resumes/{id}` | Yes | Delete resume |
| POST | `/api/v1/ai/optimize-resume` | Yes | Optimize resume |
| POST | `/api/v1/ai/generate-cover-letter` | Yes | Generate cover letter |
| POST | `/api/v1/jobs/search` | No | Search jobs |
| GET | `/health` | No | Health check |

### 18.2 Database Schema Summary

| Table | Primary Key | Foreign Keys | Indexes |
|-------|------------|--------------|---------|
| users | id | - | email, created_at, is_active |
| user_sessions | id | user_id | user_id, refresh_token, expires_at |
| resumes | id | user_id | created_at, is_default, user_id |
| cover_letters | id | user_id | created_at, user_id |
| job_applications | id | user_id, resume_id, cover_letter_id | status, company, created_at, user_id |
| job_searches | id | user_id | search_date, location, user_id |
| ai_activities | id | user_id | activity_type, created_at, user_id |
| file_metadata | id | user_id | file_path, file_type, user_id |

---

**Document Status**: Active  
**Next Review**: 2025-02-21  
**Owner**: Engineering Team

