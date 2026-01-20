# Codebase Map: Complete File and Module Reference

> **Comprehensive mapping of all files, modules, and their purposes**

## Table of Contents
- [Backend Structure](#backend-structure)
- [Frontend Structure](#frontend-structure)
- [Configuration Files](#configuration-files)
- [Scripts and Tools](#scripts-and-tools)

---

## Backend Structure

### Root Level (`backend/`)

```
backend/
├── main.py                     # Application entry point, runs FastAPI server
├── setup-database.py           # Database initialization script
├── setup-production.py         # Production environment setup
├── seed-default-user.py        # Seed default user for testing
├── requirements.txt            # Python dependencies
├── pytest.ini                  # pytest configuration
├── alembic.ini                 # Alembic migration configuration
├── alembic/                    # Database migrations
│   ├── env.py                  # Migration environment setup
│   └── versions/               # Migration version files
├── src/                        # Source code (see below)
└── tests/                      # Test suite (see below)
```

### API Layer (`backend/src/api/`)

**Purpose**: FastAPI application and route handlers

```
src/api/
├── __init__.py                 # Package initialization
├── app.py                      # FastAPI app factory, CORS, middleware setup
└── v1/                         # API version 1 endpoints
    ├── __init__.py             # Router registration
    ├── ai.py                   # AI service endpoints
    │   Routes: /api/v1/ai/*
    │   - POST /optimize-resume
    │   - POST /generate-cover-letter
    │   - POST /analyze-match
    │   - POST /extract-skills
    │   - GET /health
    │
    ├── ai_config.py            # AI configuration endpoints
    │   Routes: /api/v1/ai-config/*
    │   - GET /providers
    │   - POST /providers
    │   - PUT /providers/{id}
    │
    ├── analytics.py            # Analytics endpoints
    │   Routes: /api/v1/analytics/*
    │   - GET /overview
    │   - GET /trends
    │   - GET /success-rate
    │
    ├── analytics_export.py     # Analytics export endpoints
    │   Routes: /api/v1/analytics/export/*
    │   - POST /csv
    │   - POST /pdf
    │
    ├── analytics_insights_endpoint.py  # Analytics insights
    │   Routes: /api/v1/analytics/insights/*
    │
    ├── applications.py         # Application management
    │   Routes: /api/v1/applications/*
    │   - GET / (list)
    │   - GET /{id}
    │   - POST /
    │   - PUT /{id}
    │   - DELETE /{id}
    │   - GET /stats
    │
    ├── auth.py                 # Authentication endpoints
    │   Routes: /api/v1/auth/*
    │   - POST /register
    │   - POST /login
    │   - POST /logout
    │   - POST /refresh
    │   - POST /password-reset-request
    │   - POST /password-reset
    │
    ├── automation.py           # Browser automation endpoints
    │   Routes: /api/v1/automation/*
    │   - POST /apply
    │   - GET /status/{task_id}
    │
    ├── cache.py                # Cache management endpoints
    │   Routes: /api/v1/cache/*
    │   - DELETE /clear
    │   - GET /stats
    │
    ├── config.py               # Configuration endpoints
    │   Routes: /api/v1/config/*
    │   - GET /
    │   - PUT /
    │
    ├── cover_letters.py        # Cover letter management
    │   Routes: /api/v1/cover-letters/*
    │   - GET / (list)
    │   - GET /{id}
    │   - POST /
    │   - PUT /{id}
    │   - DELETE /{id}
    │
    ├── exports.py              # Data export endpoints
    │   Routes: /api/v1/exports/*
    │   - POST /applications/csv
    │   - POST /applications/pdf
    │   - POST /resumes/zip
    │
    ├── files.py                # File management endpoints
    │   Routes: /api/v1/files/*
    │   - POST /upload
    │   - GET /{id}
    │   - DELETE /{id}
    │
    ├── job_applications.py     # Job application workflow
    │   Routes: /api/v1/job-applications/*
    │   - GET / (list)
    │   - GET /{id}
    │   - POST /
    │   - PUT /{id}/status
    │   - DELETE /{id}
    │
    ├── jobs.py                 # Job search endpoints
    │   Routes: /api/v1/jobs/*
    │   - POST /search
    │   - GET /{id}
    │   - GET /sources
    │
    ├── monitoring.py           # Monitoring endpoints
    │   Routes: /api/v1/monitoring/*
    │   - GET /health
    │   - GET /metrics
    │   - GET /logs
    │
    ├── resume_builder.py       # Resume builder endpoints
    │   Routes: /api/v1/resume-builder/*
    │   - POST /generate
    │   - POST /templates
    │
    ├── resumes.py              # Resume management
    │   Routes: /api/v1/resumes/*
    │   - GET / (list)
    │   - GET /{id}
    │   - POST /upload
    │   - PUT /{id}
    │   - DELETE /{id}
    │   - PATCH /{id}/default
    │
    └── scheduler.py            # Scheduler endpoints
        Routes: /api/v1/scheduler/*
        - GET /jobs
        - POST /jobs
        - DELETE /jobs/{id}
```

### Core Layer (`backend/src/core/`)

**Purpose**: Abstract base classes (interfaces) for services

```
src/core/
├── __init__.py
├── ai_service.py               # IAIService interface
├── application_service.py      # IApplicationService interface
├── cover_letter_service.py     # ICoverLetterService interface
├── file_service.py             # IFileService interface
├── job_application.py          # IJobApplicationService interface
├── job_search.py               # IJobSearchService interface
├── resume_service.py           # IResumeService interface
├── analytics_service.py        # IAnalyticsService interface
├── auth_service.py             # IAuthService interface
├── config_service.py           # IConfigService interface
├── email_service.py            # IEmailService interface
├── export_service.py           # IExportService interface
├── monitoring_service.py       # IMonitoringService interface
├── notification_service.py     # INotificationService interface
├── resume_builder_service.py   # IResumeBuilderService interface
├── scheduler_service.py        # ISchedulerService interface
└── security_service.py         # ISecurityService interface
```

### Database Layer (`backend/src/database/`)

**Purpose**: ORM models, repositories, database configuration

```
src/database/
├── __init__.py
├── config.py                   # Database connection, session management
├── models.py                   # SQLAlchemy ORM models
│   Models:
│   - User
│   - Resume
│   - CoverLetter
│   - JobApplication
│   - JobSearch
│   - AIActivity
│   - FileMetadata
│   - UserSession
│   - Config
│   - MonitoringMetric
│
└── repositories/               # Repository implementations
    ├── __init__.py
    ├── application_repository.py   # ApplicationRepository
    ├── config_repository.py        # ConfigRepository
    ├── cover_letter_repository.py  # CoverLetterRepository
    ├── file_repository.py          # FileRepository
    ├── monitoring_repository.py    # MonitoringRepository
    ├── resume_repository.py        # ResumeRepository
    └── user_repository.py          # UserRepository
```

### Models Layer (`backend/src/models/`)

**Purpose**: Pydantic schemas for request/response validation

```
src/models/
├── __init__.py
├── application.py              # Application schemas
│   - ApplicationBase
│   - ApplicationCreate
│   - ApplicationUpdate
│   - ApplicationResponse
│
├── cover_letter.py             # Cover letter schemas
│   - CoverLetterBase
│   - CoverLetterCreate
│   - CoverLetterUpdate
│   - CoverLetterResponse
│
├── job.py                      # Job schemas
│   - JobBase
│   - JobSearchRequest
│   - JobSearchResponse
│   - JobDetails
│
├── resume.py                   # Resume schemas
│   - ResumeBase
│   - ResumeCreate
│   - ResumeUpdate
│   - ResumeResponse
│
├── user.py                     # User schemas
│   - UserBase
│   - UserCreate
│   - UserLogin
│   - UserResponse
│   - TokenResponse
│
├── analytics.py                # Analytics schemas
├── config.py                   # Config schemas
├── export.py                   # Export schemas
└── monitoring.py               # Monitoring schemas
```

### Services Layer (`backend/src/services/`)

**Purpose**: Business logic implementations

```
src/services/
├── __init__.py
├── service_registry.py         # Service dependency injection container
├── repository_factory.py       # Repository factory
│
├── ai_service.py               # AI service implementation
├── ai_provider_manager.py      # AI provider management
├── gemini_ai_service.py        # Google Gemini AI implementation
├── unified_ai_service.py       # Unified AI service
│
├── application_service.py      # Application business logic
├── cover_letter_service.py     # Cover letter business logic
├── resume_service.py           # Resume business logic
├── job_application_service.py  # Job application workflow
├── job_search_service.py       # Job search logic
│
├── auth_service.py             # Authentication logic
├── security_service.py         # Security utilities
│
├── local_file_service.py       # File operations
├── export_service.py           # Data export logic
│
├── analytics_service.py        # Analytics calculations
├── analytics_insights_service.py  # Analytics insights
├── analytics_exporter.py       # Analytics export
│
├── config_service.py           # Configuration management
├── email_service.py            # Email sending
├── email_templates.py          # Email templates
├── notification_service.py     # Notifications
│
├── monitoring_service.py       # Monitoring and metrics
├── scheduler_service.py        # Task scheduling
│
├── browser_automation_service.py  # Browser automation
├── platform_handlers.py        # Platform-specific handlers
├── resume_builder_service.py   # Resume generation
│
└── providers/                  # AI provider implementations
    ├── __init__.py
    ├── base_provider.py        # Base AI provider
    ├── gemini_provider.py      # Gemini provider
    ├── openai_provider.py      # OpenAI provider
    └── anthropic_provider.py   # Anthropic provider
```

### Utilities (`backend/src/utils/`)

**Purpose**: Helper functions and utilities

```
src/utils/
├── __init__.py
├── logger.py                   # Logging configuration
├── response_wrapper.py         # API response formatting
├── validators.py               # Input validation
├── text_processing.py          # Text analysis utilities
├── file_helpers.py             # File operations
├── date_helpers.py             # Date/time utilities
├── email_helpers.py            # Email utilities
├── encryption.py               # Encryption utilities
├── pdf_generator.py            # PDF generation
└── csv_generator.py            # CSV generation
```

### Middleware (`backend/src/middleware/`)

**Purpose**: Request/response middleware

```
src/middleware/
├── __init__.py
├── auth_middleware.py          # Authentication middleware
├── cors_middleware.py          # CORS configuration
├── error_handler.py            # Global error handling
├── logging_middleware.py       # Request logging
└── rate_limiter.py             # Rate limiting
```

### Validators (`backend/src/validators/`)

**Purpose**: Custom validators

```
src/validators/
├── __init__.py
└── custom_validators.py        # Custom Pydantic validators
```

### Tests (`backend/tests/`)

**Purpose**: Test suite

```
tests/
├── __init__.py
├── conftest.py                 # pytest fixtures and configuration
├── test_auth.test.py           # Authentication tests
│
├── unit/                       # Unit tests
│   ├── test_services.py
│   ├── test_repositories.py
│   ├── test_models.py
│   └── test_utils.py
│
└── integration/                # Integration tests
    ├── test_api.py
    ├── test_database.py
    └── test_e2e.py
```

---

## Frontend Structure

### Root Level (`frontend/`)

```
frontend/
├── index.html                  # HTML entry point
├── package.json                # npm dependencies
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite build configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── postcss.config.js           # PostCSS configuration
├── .eslintrc.cjs               # ESLint configuration
└── src/                        # Source code (see below)
```

### Source (`frontend/src/`)

```
src/
├── main.tsx                    # React entry point
├── App.tsx                     # Root component, routing
├── App.css                     # Global styles
├── index.css                   # Tailwind imports
├── i18n.ts                     # Internationalization setup
├── vite-env.d.ts               # Vite type definitions
│
├── pages/                      # Route pages (see below)
├── components/                 # UI components (see below)
├── services/                   # API client (see below)
├── stores/                     # State management (see below)
├── types/                      # TypeScript types (see below)
├── hooks/                      # Custom hooks (see below)
├── utils/                      # Utilities (see below)
├── styles/                     # Additional styles
├── locales/                    # Translation files
│   ├── en/
│   │   └── translation.json
│   └── id/
│       └── translation.json
│
└── test/                       # Test setup
    └── setup.ts
```

### Pages (`frontend/src/pages/`)

**Purpose**: Route components

```
pages/
├── Dashboard.tsx               # Main dashboard (/)
│   Shows: Application stats, recent activity, quick actions
│
├── Applications.tsx            # Applications list (/applications)
│   Shows: All applications, filtering, sorting
│
├── Resumes.tsx                 # Resume management (/resumes)
│   Shows: Resume list, upload, edit, delete
│
├── CoverLetters.tsx            # Cover letters (/cover-letters)
│   Shows: Cover letter list, generate, edit
│
├── JobSearch.tsx               # Job search (/jobs)
│   Shows: Search form, results, save jobs
│
├── AIServices.tsx              # AI services (/ai-services)
│   Shows: Resume optimization, cover letter generation
│
├── Analytics.tsx               # Analytics (/analytics)
│   Shows: Charts, trends, insights
│
├── Settings.tsx                # User settings (/settings)
│   Shows: Profile, preferences, AI config
│
├── AdminSettings.tsx           # Admin settings (/admin)
│   Shows: System config, user management
│
├── Login.tsx                   # Login page (/login)
├── Register.tsx                # Registration (/register)
├── PasswordReset.tsx           # Password reset (/reset-password)
├── PasswordResetRequest.tsx    # Password reset request
│
├── NotFound.tsx                # 404 page
│
└── __tests__/                  # Page tests
    ├── Dashboard.test.tsx
    ├── Applications.test.tsx
    ├── Resumes.test.tsx
    ├── CoverLetters.test.tsx
    ├── JobSearch.test.tsx
    └── AIServices.test.tsx
```

### Components (`frontend/src/components/`)

**Purpose**: Reusable UI components

```
components/
├── index.ts                    # Component exports
│
├── ui/                         # Base UI components
│   ├── Button.tsx              # Button component
│   ├── Input.tsx               # Input field
│   ├── Select.tsx              # Select dropdown
│   ├── Textarea.tsx            # Textarea
│   ├── Checkbox.tsx            # Checkbox
│   ├── Radio.tsx               # Radio button
│   ├── Modal.tsx               # Modal dialog
│   ├── Card.tsx                # Card container
│   ├── Badge.tsx               # Badge/tag
│   ├── Alert.tsx               # Alert message
│   ├── Loading.tsx             # Loading spinner
│   ├── Pagination.tsx          # Pagination
│   ├── Table.tsx               # Table
│   ├── Tabs.tsx                # Tab navigation
│   ├── Tooltip.tsx             # Tooltip
│   ├── Dropdown.tsx            # Dropdown menu
│   ├── FileUpload.tsx          # File upload
│   ├── DatePicker.tsx          # Date picker
│   ├── SearchBar.tsx           # Search input
│   ├── ProgressBar.tsx         # Progress bar
│   ├── Skeleton.tsx            # Skeleton loader
│   ├── Toast.tsx               # Toast notification
│   ├── Breadcrumb.tsx          # Breadcrumb navigation
│   ├── Accordion.tsx           # Accordion
│   └── Stepper.tsx             # Step indicator
│
├── layout/                     # Layout components
│   ├── Header.tsx              # App header
│   ├── Sidebar.tsx             # Sidebar navigation
│   └── Footer.tsx              # App footer
│
├── forms/                      # Form components
│   ├── ApplicationForm.tsx     # Application form
│   ├── ResumeUploadForm.tsx    # Resume upload
│   └── CoverLetterForm.tsx     # Cover letter form
│
├── auth/                       # Auth components
│   ├── LoginForm.tsx           # Login form
│   └── RegisterForm.tsx        # Registration form
│
├── analytics/                  # Analytics components
│   └── AnalyticsChart.tsx      # Chart component
│
├── ErrorBoundary.tsx           # Error boundary
├── ExportModal.tsx             # Export modal
│
└── __tests__/                  # Component tests
    └── Button.test.tsx
```

### Services (`frontend/src/services/`)

**Purpose**: API client and service functions

```
services/
└── api.ts                      # Complete API client
    Functions:
    - Auth: login(), register(), logout(), refreshToken()
    - Applications: getApplications(), createApplication(), etc.
    - Resumes: getResumes(), uploadResume(), etc.
    - Cover Letters: getCoverLetters(), generateCoverLetter(), etc.
    - AI: optimizeResume(), analyzejobMatch(), etc.
    - Jobs: searchJobs(), getJobDetails(), etc.
    - Analytics: getAnalytics(), exportData(), etc.
```

### Stores (`frontend/src/stores/`)

**Purpose**: Zustand state management

```
stores/
└── appStore.ts                 # Global application state
    State:
    - user: User | null
    - isAuthenticated: boolean
    - theme: 'light' | 'dark'
    - notifications: Notification[]
    Actions:
    - setUser()
    - logout()
    - setTheme()
    - addNotification()
```

### Types (`frontend/src/types/`)

**Purpose**: TypeScript type definitions

```
types/
└── index.ts                    # All type definitions
    Types:
    - Application
    - Resume
    - CoverLetter
    - Job
    - User
    - APIResponse
    - PaginatedResponse
    - etc.
```

### Hooks (`frontend/src/hooks/`)

**Purpose**: Custom React hooks

```
hooks/
└── useAuth.ts                  # Authentication hook
```

### Utils (`frontend/src/utils/`)

**Purpose**: Utility functions

```
utils/
└── icons.ts                    # Icon utilities
```

---

## Configuration Files

### Root Level

```
.
├── .gitignore                  # Git ignore rules
├── .gitattributes              # Git attributes
├── .pre-commit-config.yaml     # Pre-commit hooks
├── docker-compose.yml          # Docker development setup
├── docker-compose.prod.yml     # Docker production setup
├── Makefile                    # Build commands
├── start-dev.sh                # Development startup script
├── stop-dev.sh                 # Development stop script
├── package.json                # Root npm config (workspaces)
├── package-lock.json           # npm lock file
└── README.md                   # Project README
```

### Documentation (`docs/`)

```
docs/
├── README.md                   # Documentation index
├── LLM-GUIDE.md                # LLM quick guide (this is new!)
├── 00-project-state.md         # Current project state
├── 01-architecture.md          # Architecture overview
├── 02-api-reference.md         # API reference
├── 03-database-schema.md       # Database schema
├── 04-development-guide.md     # Development guide
├── 05-project-proposals.md     # OpenSpec proposals
├── 06-api-versioning.md        # API versioning
├── 07-security-guide.md        # Security guide
├── 08-codebase-map.md          # This file!
├── PRD.md                      # Product requirements
├── TDD.md                      # Technical design
├── HLD.md                      # High-level design
├── ARCHITECTURE_PATTERNS.md    # Architecture patterns
├── deployment.md               # Deployment guide
└── postman_collection.json     # Postman API collection
```

---

## Scripts and Tools

### Scripts (`scripts/`)

```
scripts/
├── auto-create-vibe-tasks.py       # Auto-create tasks
├── auto-sync-openspec-to-vibe.py   # Sync OpenSpec
├── technical-debt-monitor.py       # Monitor technical debt
└── workflow-orchestrator.py        # Workflow automation
```

### Backend Scripts (`backend/scripts/`)

```
backend/scripts/
├── backup_database.py          # Database backup
├── check_coverage.py           # Test coverage check
└── seed_default_configs.py     # Seed default configs
```

---

## Import Path Examples

### Backend

```python
# Absolute imports (REQUIRED)
from src.core.ai_service import IAIService
from src.services.gemini_ai_service import GeminiAIService
from src.database.models import Application, Resume
from src.database.repositories.application_repository import ApplicationRepository
from src.models.application import ApplicationCreate, ApplicationResponse
from src.api.v1.applications import router
from src.utils.logger import logger
from src.config import settings
```

### Frontend

```typescript
// Relative imports
import { Application, Resume } from '@/types';
import { api } from '@/services/api';
import { useAppStore } from '@/stores/appStore';
import { Button } from '@/components/ui/Button';
import { ApplicationForm } from '@/components/forms/ApplicationForm';
```

---

**Last Updated**: 2026-01-20  
**Purpose**: Complete file and module reference for LLM agents  
**Coverage**: 100% of project files documented
