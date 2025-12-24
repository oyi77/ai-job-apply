# Project Context

## Purpose

**AI Job Application Assistant** is an enterprise-grade, full-stack web application that helps users manage their job search process through AI-powered features. The system provides:

- **Intelligent Job Search**: Multi-platform job search with AI-powered filtering and matching
- **Resume Optimization**: AI-driven resume analysis and improvement suggestions using Google Gemini
- **Cover Letter Generation**: Personalized cover letters tailored to specific job postings
- **Application Tracking**: Comprehensive lifecycle management from draft to offer with analytics
- **File Management**: Secure handling of resumes and documents in multiple formats (PDF, DOCX, TXT)

The project follows **SOLID principles**, **DRY methodology**, and maintains **zero technical debt** through strict quality gates and automated tooling.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: SQLAlchemy 2.0 with async support
  - Production: PostgreSQL
  - Development/Testing: SQLite
- **ORM**: SQLAlchemy async with repository pattern
- **Data Validation**: Pydantic v2
- **AI Integration**: Google Gemini API (gemini-1.5-flash)
- **Job Search**: JobSpy library + custom portal implementations
- **File Processing**: python-docx, pdf processing libraries
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: Black, isort, flake8, mypy

### Frontend
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS 3.4
- **State Management**: 
  - Zustand (client state)
  - React Query / TanStack Query (server state)
- **Forms**: React Hook Form
- **Routing**: React Router v7
- **UI Components**: Headless UI, Heroicons
- **HTTP Client**: Axios
- **Testing**: Vitest, React Testing Library

### Infrastructure
- **Database Migrations**: Alembic
- **Development**: Hot reload for both frontend and backend
- **Deployment**: Docker-ready, production configuration support

## Project Conventions

### Code Style

#### Python (Backend)
- **Formatter**: Black (line length: 88)
- **Import Sorting**: isort (Black-compatible profile)
- **Linter**: flake8 (max line length: 88, ignore E203, W503)
- **Type Checking**: mypy (strict mode enabled)
- **Naming**:
  - Classes: `PascalCase` (e.g., `JobApplication`, `ResumeService`)
  - Functions/Methods: `snake_case` (e.g., `create_application`, `optimize_resume`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_FILE_SIZE`)
  - Private: `_leading_underscore` for internal methods
- **Type Hints**: Required for all function parameters and return values
- **Docstrings**: Google-style docstrings for all public APIs
- **Line Limits**: 
  - Functions: Max 20 lines
  - Classes: Max 200 lines
  - Modules: Max 500 lines

#### TypeScript (Frontend)
- **Formatter**: Prettier (integrated with ESLint)
- **Linter**: ESLint with TypeScript plugin
- **Type Checking**: TypeScript strict mode
- **Naming**:
  - Components: `PascalCase` (e.g., `JobCard`, `ApplicationForm`)
  - Functions/Variables: `camelCase` (e.g., `handleSubmit`, `applicationData`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)
  - Types/Interfaces: `PascalCase` (e.g., `JobApplication`, `ResumeData`)
- **Component Structure**: Functional components with hooks only
- **File Organization**: One component per file, co-located with tests

### Architecture Patterns

#### Backend Architecture
```
src/
├── core/                    # Abstract base classes (interfaces)
│   ├── ai_service.py       # AI service interface
│   ├── resume_service.py   # Resume service interface
│   ├── application_service.py
│   └── file_service.py
├── models/                  # Pydantic data models
│   ├── job.py
│   ├── resume.py
│   ├── application.py
│   └── cover_letter.py
├── services/               # Concrete service implementations
│   ├── gemini_ai_service.py
│   ├── file_based_resume_service.py
│   ├── memory_based_application_service.py
│   └── service_registry.py
├── database/               # Database layer
│   ├── models.py          # SQLAlchemy ORM models
│   ├── config.py          # Database configuration
│   └── repositories/      # Repository pattern implementations
├── api/                    # FastAPI application
│   └── v1/                # API version 1 endpoints
└── utils/                  # Utility functions
```

**Key Patterns**:
- **Repository Pattern**: All data access through repositories
- **Service Layer**: Business logic in services, not controllers
- **Dependency Injection**: Service registry for loose coupling
- **Interface Segregation**: Abstract base classes for all services
- **Async/Await**: All I/O operations are async

#### Frontend Architecture
```
src/
├── components/             # Reusable UI components
│   ├── ui/                # Base components (Button, Input, etc.)
│   ├── forms/             # Form components
│   └── layout/            # Layout components
├── pages/                 # Page components (routes)
├── services/             # API service functions
├── stores/               # Zustand stores
├── hooks/                # Custom React hooks
├── types/                # TypeScript type definitions
└── utils/                # Utility functions
```

**Key Patterns**:
- **Component Composition**: Small, focused components
- **Custom Hooks**: Extract reusable logic
- **Server State**: React Query for API data
- **Client State**: Zustand for UI state
- **Code Splitting**: Lazy loading for routes

### Testing Strategy

#### Backend Testing
- **Framework**: pytest with pytest-asyncio
- **Coverage Target**: 95%+ for business logic
- **Test Structure**:
  - `tests/unit/`: Unit tests for services, repositories, utilities
  - `tests/integration/`: API endpoint tests, database integration
  - `tests/fixtures/`: Reusable test data
- **Mocking**: Mock external dependencies (AI services, file system)
- **Database**: Test database with fixtures, isolated test transactions
- **Running**: `pytest tests/ -v --cov=src`

#### Frontend Testing
- **Framework**: Vitest with React Testing Library
- **Coverage Target**: 90%+ for components and hooks
- **Test Types**:
  - Component unit tests
  - Hook tests
  - Integration tests (API mocking with MSW)
- **Running**: `npm test` (watch mode) or `npm run test:run`

#### Quality Gates
- All tests must pass before merge
- Coverage must be maintained or improved
- No new linting errors
- No new type errors

### Git Workflow

#### Branching Strategy
- **Main Branch**: `main` (production-ready code)
- **Feature Branches**: `feature/feature-name`
- **Bug Fixes**: `fix/bug-description`
- **Hotfixes**: `hotfix/critical-issue`

#### Commit Conventions
- **Format**: Conventional commits
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation changes
  - `style:` Code style changes (formatting)
  - `refactor:` Code refactoring
  - `test:` Adding or updating tests
  - `chore:` Maintenance tasks
- **Example**: `feat: add resume optimization endpoint`

#### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Run quality checks: `make check-quality`
4. Ensure all tests pass: `make test`
5. Create pull request with description
6. Code review required
7. Merge after approval

## Domain Context

### Core Entities

#### Job Application
- **Lifecycle**: Draft → Submitted → Under Review → Interview → Offer → Rejected
- **Statuses**: 10 different application statuses with valid transitions
- **Tracking**: Created date, updated date, follow-up dates, notes
- **Analytics**: Success rates, response times, interview performance

#### Resume
- **Formats**: PDF, DOCX, TXT
- **Processing**: Text extraction, skills identification, experience parsing
- **Optimization**: AI-powered suggestions for specific job postings
- **Management**: Version control, default resume selection

#### Cover Letter
- **Generation**: AI-generated based on job description and resume
- **Customization**: Tone, length, focus areas
- **Templates**: Reusable templates for different job types
- **Storage**: Linked to specific job applications

#### Job Search
- **Platforms**: LinkedIn, Indeed, Glassdoor, Google Jobs, ZipRecruiter
- **Search Parameters**: Keywords, location, experience level, salary range
- **Matching**: AI-powered job-resume compatibility analysis
- **History**: Track search patterns and results

### Business Rules

1. **Application Status Transitions**: Only valid status transitions allowed
2. **File Validation**: File type, size, and content validation before processing
3. **AI Service Fallback**: Graceful degradation when AI services unavailable
4. **Data Persistence**: All operations persist to database with proper transactions
5. **Security**: Input validation, file sanitization, SQL injection prevention

### Workflows

1. **Resume Upload** → Text Extraction → Skills Identification → Storage
2. **Job Search** → Results → AI Matching Analysis → Application Creation
3. **Application Creation** → Resume Selection → Cover Letter Generation → Submission Tracking
4. **Resume Optimization** → AI Analysis → Suggestions → Resume Update

## Important Constraints

### Technical Constraints

1. **Zero Technical Debt Policy**: 
   - No quick fixes or temporary solutions
   - Immediate debt resolution required
   - Functions max 20 lines, classes max 200 lines, modules max 500 lines
   - No dead code, no commented code, no magic numbers

2. **Type Safety**: 
   - 100% type coverage required (Python + TypeScript)
   - Strict type checking enabled
   - No `any` types in TypeScript

3. **Performance Requirements**:
   - API response time: < 500ms (95th percentile)
   - Database query time: < 100ms (95th percentile)
   - Frontend load time: < 2.5s
   - Bundle size: < 500KB gzipped

4. **Code Quality**:
   - All code must pass Black, isort, flake8, mypy
   - Pre-commit hooks enforce quality
   - CI/CD pipeline validates all checks

5. **Testing Requirements**:
   - 95%+ test coverage for backend business logic
   - 90%+ test coverage for frontend components
   - All tests must pass before merge

### Business Constraints

1. **AI Service Availability**: Must gracefully handle AI service unavailability
2. **File Size Limits**: Max 10MB per file upload
3. **Rate Limiting**: Respect external API rate limits (Gemini, job boards)
4. **Data Privacy**: Secure handling of personal information (resumes, applications)

### Regulatory Constraints

1. **Data Protection**: Secure storage and transmission of user data
2. **File Security**: Validation and sanitization of uploaded files
3. **API Security**: Input validation, CORS configuration, rate limiting

## External Dependencies

### AI Services
- **Google Gemini API**: 
  - Model: `gemini-1.5-flash`
  - Purpose: Resume optimization, cover letter generation, job matching
  - Configuration: API key via `GEMINI_API_KEY` environment variable
  - Fallback: Mock responses when service unavailable

### Job Search Services
- **JobSpy Library**: 
  - Platforms: LinkedIn, Indeed, Glassdoor, ZipRecruiter, Google Jobs
  - Purpose: Multi-platform job search
  - Fallback: Custom portal implementations when JobSpy unavailable

### Database
- **PostgreSQL**: Production database (optional, SQLite for development)
- **SQLite**: Development and testing database
- **Alembic**: Database migration management

### Development Tools
- **Black**: Python code formatter
- **isort**: Import sorting
- **flake8**: Python linter
- **mypy**: Python type checker
- **pytest**: Python testing framework
- **Vitest**: Frontend testing framework
- **ESLint**: JavaScript/TypeScript linter
- **Prettier**: Code formatter

### Runtime Dependencies
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **Pydantic**: Data validation
- **React**: UI framework
- **React Query**: Server state management
- **Zustand**: Client state management
- **Tailwind CSS**: Styling framework
- **Axios**: HTTP client

### File Processing
- **python-docx**: DOCX file processing
- **PDF libraries**: PDF text extraction
- **aiofiles**: Async file operations

---

*Last Updated: 2025-01-27*
*Project Status: Production Ready*
