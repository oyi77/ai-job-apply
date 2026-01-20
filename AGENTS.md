# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-20 09:22 AM (Asia/Jakarta)
**Branch:** (run `git branch --show-current`)
**Commit:** (run `git rev-parse HEAD`)

## OVERVIEW
AI-powered job application management system with FastAPI backend and React/TypeScript frontend.

## STRUCTURE
```
./
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── api/v1/        # REST endpoints (routers)
│   │   ├── core/          # Interface contracts (ABCs)
│   │   ├── database/      # SQLAlchemy models + repositories
│   │   ├── models/        # Pydantic schemas
│   │   ├── services/      # Business logic implementations
│   │   ├── middleware/    # Security + metrics
│   │   └── utils/         # Helpers, validators, sanitization
│   └── tests/             # Pytest (unit, integration, performance)
├── frontend/               # React 18 + TypeScript
│   ├── src/
│   │   ├── components/ui/ # Custom UI component library
│   │   ├── pages/         # Route-based page components
│   │   ├── services/      # API client layer
│   │   ├── stores/        # Zustand global state
│   │   ├── hooks/         # Custom React hooks
│   │   └── types/         # TypeScript definitions
│   └── tests/             # Vitest + Playwright
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── openspec/              # Spec-driven development system
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add API endpoint | `backend/src/api/v1/` | Create router, add to app.py |
| Add AI feature | `backend/src/services/` + `backend/src/core/` | Interface in core, impl in services |
| Add UI component | `frontend/src/components/ui/` | Follow component patterns |
| Add page | `frontend/src/pages/` + `frontend/src/App.tsx` | Lazy-loaded with React.lazy |
| Add database model | `backend/src/models/` (Pydantic) + `backend/src/database/` (SQLAlchemy) |
| Add service logic | `backend/src/services/` | Use dependency injection |
| Write tests | `backend/tests/` or `frontend/src/__tests__/` | Follow test conventions |

## CODE MAP
| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| `ServiceRegistry` | class | `backend/src/services/service_registry.py` | 8 | DI container |
| `ApplicationService` | class | `backend/src/services/memory_based_application_service.py` | 6 | App tracking |
| `GeminiAIService` | class | `backend/src/services/gemini_ai_service.py` | 5 | AI operations |
| `AppStore` | class | `frontend/src/stores/appStore.ts` | 4 | Global state |
| `useQuery` | hook | `frontend/src/services/api.ts` | 15+ | Data fetching |

## CONVENTIONS (DEVIATIONS FROM STANDARD)

### Backend (Python)
- **Line length**: 88 chars (Black)
- **Type checking**: Strict mypy (`disallow_untyped_defs = true`)
- **Testing**: 95% coverage threshold, AsyncMock for async tests
- **Imports**: Absolute from project root (`from src.x import y`)
- **Async**: All I/O operations must be async

### Frontend (React)
- **State**: React Query (server) + Zustand (client)
- **Styling**: Tailwind CSS with custom color palette
- **Components**: Headless UI for accessibility
- **Testing**: Vitest (unit) + Playwright (E2E)

### Project-Wide
- **Linting**: ESLint + Prettier (frontend), Black + Flake8 (backend)
- **Commits**: Conventional commits enforced
- **Secrets**: detect-secrets pre-commit hook

## ANTI-PATTERNS (THIS PROJECT)

### Never Do
- ❌ Synchronous I/O in async functions
- ❌ Direct database access in API routers (use repositories)
- ❌ Business logic in UI components (delegate to services)
- ❌ Business logic in API routers (delegate to services)
- ❌ Use `cn`/`clsx` for class merging (use template literals)
- ❌ Local state for server data (use React Query)
- ❌ Direct API calls in pages (use services layer)

### Always Do
- ✅ Abstract interfaces in `core/`, implementations in `services/`
- ✅ Use `async with session.begin()` for transactions
- ✅ Memoize Tailwind classes with `useMemo`
- ✅ Lazy-load pages with `React.lazy()`
- ✅ Validate with Pydantic models

## UNIQUE STYLES

### Backend Architecture
- **Repository Pattern**: Clean separation of data access
- **Service Layer**: Dependency injection via `ServiceRegistry`
- **Fallback Strategy**: Graceful degradation when AI services unavailable

### Frontend Architecture
- **Custom UI Library**: 17+ components built from scratch (no shadcn/ui)
- **Sub-component Pattern**: `Card` exports `CardHeader`, `CardBody`, `CardFooter`
- **Notification System**: Internal hook (`useNotifications`) with global container

### CI/CD
- **Quality Gates**: Pre-commit hooks enforce linting, secrets detection
- **E2E Testing**: Playwright spawns both frontend and backend automatically
- **Database Isolation**: E2E tests use SQLite (override via env)

## COMMANDS

```bash
# Backend
cd backend && python -m pytest tests/ -v --cov=src
cd backend && python -m pytest tests/unit/ -k "test_auth"

# Frontend  
cd frontend && npm test
cd frontend && npm run test:e2e

# Full stack
cd frontend && npm run dev &  # Starts on :5173
cd backend && python main.py  # Starts on :8000

# Linting
cd backend && black . && flake8 . && mypy src/
cd frontend && npm run lint
```

## NOTES

- **Gemini API**: Key in `.env` (`GEMINI_API_KEY`)
- **Database**: PostgreSQL (prod) / SQLite (dev/E2E)
- **Environment**: Docker Compose for full stack (`docker-compose up -d`)
- **OpenSpec**: Use for feature changes (`openspec/` directory)
- **Import Conflicts**: Run from root only (`python main.py`, NOT `python src/main.py`)

## GIT RULES
- Feature branches from `main`
- Conventional commit messages
- PR required for merge
- Squash before merging
