# LLM Guide: AI Job Application Assistant

> **Primary entry point for AI agents working with this codebase**

## Quick Facts

- **Project**: AI Job Application Assistant
- **Type**: Full-stack web application
- **Backend**: FastAPI (Python 3.10+), SQLAlchemy async, PostgreSQL/SQLite
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **AI**: Google Gemini API (gemini-1.5-flash)
- **Architecture**: Clean architecture with SOLID principles, repository pattern, service layer
- **Status**: Production ready, zero technical debt policy

## Critical Constraints

⚠️ **MUST FOLLOW**:
1. **Zero Technical Debt**: No quick fixes, no commented code, no magic numbers
2. **Type Safety**: 100% type coverage (Python type hints + TypeScript strict mode)
3. **Code Limits**: Functions ≤20 lines, Classes ≤200 lines, Modules ≤500 lines
4. **Testing**: 95%+ backend coverage, 90%+ frontend coverage
5. **Absolute Imports**: Python uses absolute imports only (e.g., `from src.core import module`)

## Project Structure Overview

```
ai-job-apply/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── api/v1/            # API endpoints (21 files)
│   │   ├── core/              # Abstract interfaces (17 files)
│   │   ├── database/          # ORM models + repositories
│   │   ├── models/            # Pydantic schemas (10 files)
│   │   ├── services/          # Business logic (29 files)
│   │   ├── utils/             # Helpers (11 files)
│   │   └── config.py          # Configuration
│   ├── tests/                 # pytest test suite
│   ├── alembic/               # Database migrations
│   └── main.py                # Application entry point
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/             # Route pages (15 files)
│   │   ├── components/        # UI components (39 files)
│   │   ├── services/          # API client
│   │   ├── stores/            # Zustand state
│   │   └── types/             # TypeScript types
│   └── package.json
├── docs/                       # Documentation (17+ files)
├── scripts/                    # Automation scripts
└── openspec/                   # OpenSpec proposals
```

## Quick Navigation

### For Common Tasks
→ See [09-common-tasks.md](./09-common-tasks.md)

### For Architecture Understanding
→ See [01-architecture.md](./01-architecture.md) and [08-codebase-map.md](./08-codebase-map.md)

### For API Details
→ See [02-api-reference.md](./02-api-reference.md) and [11-api-endpoints-detailed.md](./11-api-endpoints-detailed.md)

### For Database Schema
→ See [03-database-schema.md](./03-database-schema.md) and [12-database-operations.md](./12-database-operations.md)

### For Troubleshooting
→ See [10-troubleshooting.md](./10-troubleshooting.md)

## Decision Trees

### "I need to add a new feature"

```
1. Is it a new API endpoint?
   YES → Read: 09-common-tasks.md → "Adding a new API endpoint"
   NO  → Continue

2. Is it a new database model?
   YES → Read: 09-common-tasks.md → "Creating a new database model"
   NO  → Continue

3. Is it a new service?
   YES → Read: 09-common-tasks.md → "Adding a new service"
   NO  → Continue

4. Is it a new UI component?
   YES → Read: 09-common-tasks.md → "Creating a new React component"
   NO  → Read: 04-development-guide.md → "Adding New Features"
```

### "I need to understand existing code"

```
1. What are you looking for?
   
   API endpoint → 11-api-endpoints-detailed.md
   Database table → 03-database-schema.md
   Service → 13-service-layer.md
   Component → 14-frontend-components.md
   File location → 08-codebase-map.md
```

### "Something is broken"

```
1. What's the error?
   
   Database connection → 10-troubleshooting.md → "Database Issues"
   AI service failure → 10-troubleshooting.md → "AI Service Issues"
   CORS error → 10-troubleshooting.md → "CORS Errors"
   Build failure → 10-troubleshooting.md → "Build Issues"
   Test failure → 15-testing-guide.md → "Debugging Test Failures"
```

## Environment Setup Checklist

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp config.env.example .env
# Edit .env with GEMINI_API_KEY
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
cd backend
python setup-database.py  # Initialize database
alembic upgrade head      # Run migrations
```

## Key Architectural Patterns

### Backend: Repository Pattern
```python
# 1. Define interface in src/core/
class IApplicationRepository(ABC):
    @abstractmethod
    async def create(self, data: ApplicationCreate) -> Application:
        pass

# 2. Implement in src/database/repositories/
class ApplicationRepository(IApplicationRepository):
    async def create(self, data: ApplicationCreate) -> Application:
        # Implementation
        pass

# 3. Use in service
class ApplicationService:
    def __init__(self, repo: IApplicationRepository):
        self.repo = repo
```

### Backend: Service Layer
```python
# Services handle business logic
# Located in: src/services/

class ApplicationService:
    def __init__(self, repo: IApplicationRepository):
        self.repo = repo
    
    async def create_application(self, data: ApplicationCreate) -> Application:
        # Validation
        # Business logic
        # Repository call
        return await self.repo.create(data)
```

### Frontend: Component Pattern
```typescript
// Functional components with hooks
// Located in: src/components/ or src/pages/

interface Props {
  applicationId: string;
}

export const ApplicationCard: React.FC<Props> = ({ applicationId }) => {
  const [data, setData] = useState<Application | null>(null);
  
  useEffect(() => {
    // Fetch data
  }, [applicationId]);
  
  return <div>{/* JSX */}</div>;
};
```

## File Naming Conventions

### Backend (Python)
- **Modules**: `snake_case.py` (e.g., `application_service.py`)
- **Classes**: `PascalCase` (e.g., `ApplicationService`)
- **Functions**: `snake_case` (e.g., `create_application`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_FILE_SIZE`)

### Frontend (TypeScript)
- **Components**: `PascalCase.tsx` (e.g., `ApplicationCard.tsx`)
- **Utilities**: `camelCase.ts` (e.g., `apiClient.ts`)
- **Types**: `PascalCase` (e.g., `Application`, `ResumeData`)
- **Functions**: `camelCase` (e.g., `handleSubmit`)

## Common File Locations

### Backend
- **API Endpoints**: `backend/src/api/v1/*.py`
- **Services**: `backend/src/services/*.py`
- **Repositories**: `backend/src/database/repositories/*.py`
- **Models (ORM)**: `backend/src/database/models.py`
- **Schemas (Pydantic)**: `backend/src/models/*.py`
- **Tests**: `backend/tests/`

### Frontend
- **Pages**: `frontend/src/pages/*.tsx`
- **Components**: `frontend/src/components/**/*.tsx`
- **API Client**: `frontend/src/services/api.ts`
- **State**: `frontend/src/stores/appStore.ts`
- **Types**: `frontend/src/types/index.ts`

## Testing Commands

```bash
# Backend tests
cd backend
pytest tests/ -v                    # Run all tests
pytest tests/ -v --cov=src          # With coverage
pytest tests/unit/                  # Unit tests only
pytest tests/integration/           # Integration tests only

# Frontend tests
cd frontend
npm test                            # Watch mode
npm run test:run                    # Single run
npm run test:coverage               # With coverage
```

## Running the Application

```bash
# Development (from project root)
./start-dev.sh                      # Linux/Mac
# Or manually:
# Terminal 1: cd backend && python main.py
# Terminal 2: cd frontend && npm run dev

# Access:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Core Entities

1. **Application** - Job application tracking
   - Status: Draft → Submitted → Interview → Offer/Rejected
   - Fields: company, position, status, dates, notes
   - Relations: Resume (many-to-one), CoverLetter (many-to-one)

2. **Resume** - Resume management
   - Formats: PDF, DOCX, TXT
   - Fields: filename, content, skills, is_default
   - Relations: Applications (one-to-many)

3. **CoverLetter** - Cover letter generation
   - Fields: job_title, company, content, tone
   - Relations: Applications (one-to-many)

4. **User** - User authentication
   - Fields: email, password_hash, is_active, is_admin
   - Relations: Applications, Resumes, CoverLetters

## Important URLs

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:5173

## Next Steps

1. **New to the project?** → Read [00-project-state.md](./00-project-state.md)
2. **Need to add a feature?** → Read [09-common-tasks.md](./09-common-tasks.md)
3. **Need architecture details?** → Read [01-architecture.md](./01-architecture.md)
4. **Need to understand a file?** → Read [08-codebase-map.md](./08-codebase-map.md)
5. **Something broken?** → Read [10-troubleshooting.md](./10-troubleshooting.md)

---

**Last Updated**: 2026-01-20  
**For**: LLM agents (Claude, GPT, Gemini, etc.)  
**Purpose**: Quick orientation and task execution
