# Architecture Documentation

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Dashboard│  │Applications│ │ Resumes │  │Job Search│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  State: Zustand + React Query                              │
│  API Client: Axios                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Backend (FastAPI)                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              API Layer (v1)                       │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐         │    │
│  │  │  Jobs    │ │Applications│ │  AI     │         │    │
│  │  └──────────┘ └──────────┘ └──────────┘         │    │
│  └────────────────────────────────────────────────────┘    │
│                       │                                     │
│  ┌────────────────────▼────────────────────────────────┐  │
│  │            Service Layer                              │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │  │
│  │  │  AI      │ │Application│ │  File   │            │  │
│  │  │ Service  │ │ Service  │ │ Service │            │  │
│  │  └──────────┘ └──────────┘ └──────────┘            │  │
│  └────────────────────┬────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼────────────────────────────────┐  │
│  │         Repository Layer                               │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │  │
│  │  │Application│ │ Resume   │ │CoverLetter│            │  │
│  │  │Repository │ │Repository│ │Repository│            │  │
│  │  └──────────┘ └──────────┘ └──────────┘            │  │
│  └────────────────────┬────────────────────────────────┘  │
└───────────────────────┼────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  PostgreSQL  │ │  File System│ │ Gemini API │
│  (Database)  │ │  (Storage)   │ │  (AI)      │
└──────────────┘ └──────────────┘ └────────────┘
```

## Backend Architecture

### Layered Architecture

#### 1. API Layer (`src/api/`)
- **Purpose**: HTTP request handling and routing
- **Responsibilities**:
  - Request validation
  - Response formatting
  - Error handling
  - Authentication/Authorization (future)
- **Pattern**: FastAPI routers with dependency injection

#### 2. Service Layer (`src/services/`)
- **Purpose**: Business logic implementation
- **Responsibilities**:
  - Business rules enforcement
  - Data transformation
  - External service integration
  - Error handling and logging
- **Pattern**: Service registry with dependency injection

#### 3. Repository Layer (`src/database/repositories/`)
- **Purpose**: Data access abstraction
- **Responsibilities**:
  - Database operations
  - Query optimization
  - Transaction management
  - Data mapping
- **Pattern**: Repository pattern with async SQLAlchemy

#### 4. Model Layer (`src/models/` + `src/database/models.py`)
- **Purpose**: Data representation
- **Responsibilities**:
  - Domain models (Pydantic)
  - Database models (SQLAlchemy)
  - Data validation
  - Serialization
- **Pattern**: Separate domain and persistence models

### Design Patterns

#### Repository Pattern
```python
class ApplicationRepository:
    async def create(self, application: JobApplication) -> JobApplication:
        # Database operations
        pass
    
    async def get_by_id(self, id: str) -> Optional[JobApplication]:
        # Query with relationships
        pass
```

#### Service Registry Pattern
```python
class ServiceRegistry:
    async def initialize(self) -> None:
        # Initialize services in dependency order
        pass
    
    async def get_ai_service(self) -> AIService:
        # Dependency injection
        pass
```

#### Dependency Injection
- Services registered in `ServiceRegistry`
- Dependencies injected through constructor
- Lifecycle management (initialize/cleanup)
- Health monitoring

## Frontend Architecture

### Component Architecture

#### Page Components (`src/pages/`)
- **Purpose**: Route-level components
- **Structure**: Container components with business logic
- **Examples**: Dashboard, Applications, Resumes

#### UI Components (`src/components/ui/`)
- **Purpose**: Reusable presentation components
- **Structure**: Stateless functional components
- **Examples**: Button, Input, Card, Modal

#### Layout Components (`src/components/layout/`)
- **Purpose**: Page structure and navigation
- **Structure**: Layout wrappers with routing
- **Examples**: Header, Sidebar, Layout

### State Management

#### Server State (React Query)
- **Purpose**: API data caching and synchronization
- **Features**:
  - Automatic caching
  - Background refetching
  - Optimistic updates
  - Error handling

#### Client State (Zustand)
- **Purpose**: UI state and preferences
- **Features**:
  - Lightweight store
  - Type-safe
  - DevTools support

### Data Flow

```
User Action
    ↓
Component Event Handler
    ↓
API Service (api.ts)
    ↓
React Query Hook
    ↓
Backend API
    ↓
Service Layer
    ↓
Repository Layer
    ↓
Database
```

## Database Architecture

### Schema Design

#### Normalization
- **3NF**: Proper normalization
- **Relationships**: Foreign keys with cascading
- **Indexes**: Strategic indexing for performance

#### Models
- **DBResume**: Resume storage with metadata
- **DBCoverLetter**: Cover letter content
- **DBJobApplication**: Application tracking
- **DBJobSearch**: Search history
- **DBAIActivity**: AI operation logs
- **DBFileMetadata**: File tracking

### Migration Strategy
- **Tool**: Alembic
- **Version Control**: Migration files in `alembic/versions/`
- **Process**: Forward-only migrations

## Service Architecture

### Service Registry

#### Core Services
1. **LocalFileService**: File operations
2. **GeminiAIService**: AI integration

#### Business Services
1. **ResumeService**: Resume management
2. **ApplicationService**: Application tracking
3. **CoverLetterService**: Cover letter operations
4. **JobSearchService**: Job search
5. **JobApplicationService**: Application workflow

### Service Lifecycle

```python
# Initialization
await service_registry.initialize()

# Usage
ai_service = await service_registry.get_ai_service()
result = await ai_service.optimize_resume(...)

# Cleanup
await service_registry.cleanup()
```

## Security Architecture

### Input Validation
- **Pydantic Models**: Request/response validation
- **Type Safety**: TypeScript + Python type hints
- **Sanitization**: File and text sanitization

### File Security
- **Type Validation**: MIME type checking
- **Size Limits**: Max file size enforcement
- **Path Sanitization**: Directory traversal prevention

### API Security
- **CORS**: Configurable origins
- **Rate Limiting**: (Future implementation)
- **Authentication**: (Future JWT implementation)

## Error Handling

### Backend Error Handling
```python
try:
    result = await service.operation()
except ValidationError as e:
    raise HTTPException(400, detail=str(e))
except NotFoundError as e:
    raise HTTPException(404, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(500, detail="Internal server error")
```

### Frontend Error Handling
- **React Query**: Automatic error handling
- **Error Boundaries**: Component-level error catching
- **User Feedback**: Toast notifications for errors

## Performance Optimization

### Backend
- **Async Operations**: Non-blocking I/O
- **Connection Pooling**: Database connection reuse
- **Query Optimization**: Efficient SQL queries
- **Caching**: (Future Redis integration)

### Frontend
- **Code Splitting**: Route-based lazy loading
- **Memoization**: React.memo and useMemo
- **Bundle Optimization**: Tree shaking and minification
- **Image Optimization**: (Future implementation)

## Deployment Architecture

### Development
- **Backend**: FastAPI dev server (port 8000)
- **Frontend**: Vite dev server (port 5173)
- **Database**: SQLite

### Production (Planned)
- **Backend**: Docker container with uvicorn
- **Frontend**: Static files served via CDN
- **Database**: PostgreSQL with connection pooling
- **Reverse Proxy**: Nginx
- **Monitoring**: (Future implementation)

## Testing Architecture

### Backend Testing
- **Unit Tests**: Service and repository tests
- **Integration Tests**: API endpoint tests
- **Fixtures**: Reusable test data
- **Mocking**: External service mocks

### Frontend Testing
- **Component Tests**: React Testing Library
- **Hook Tests**: Custom hook testing
- **Integration Tests**: API mocking with MSW
- **E2E Tests**: (Future Playwright implementation)

## Monitoring & Logging

### Logging
- **Backend**: Loguru structured logging
- **Frontend**: Console logging (production filtering)
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Health Checks
- **Application**: `/health` endpoint
- **Services**: Service registry health checks
- **Database**: Connection health monitoring

---

**Architecture Status**: Production-ready with clear separation of concerns

