# API v1 Routers

**OVERVIEW**: FastAPI routers for all REST endpoints.

## STRUCTURE
- `applications.py` - CRUD for job applications
- `resumes.py` - Resume upload and management
- `ai.py` - AI optimization and generation endpoints
- `jobs.py` - Job search endpoints
- `cover_letters.py` - Cover letter management

## WHERE TO LOOK
| Endpoint | Purpose |
|----------|---------|
| `GET /applications` | List all applications |
| `POST /applications` | Create application |
| `POST /ai/optimize-resume` | AI resume optimization |
| `GET /jobs/search` | Job search across platforms |

## CONVENTIONS
- **Validation**: Pydantic models for request/response validation
- **Injection**: Dependency injection for services
- **Errors**: Consistent error responses with `ErrorResponse` model

## ANTI-PATTERNS
- **Business Logic**: No business logic in routers (delegate to services)
- **Database**: No direct database queries (use repositories)

## NOTES
- All routes in this directory are prefixed with `/api/v1/`.
