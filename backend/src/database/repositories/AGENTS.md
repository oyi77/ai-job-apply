# 🤖 AGENTS.md: Database Repositories

## OVERVIEW
SQLAlchemy async data access layer with CRUD operations.

## STRUCTURE
N/A

## WHERE TO LOOK
| Repository | Purpose |
|------------|---------|
| `user_repository.py` | User CRUD operations |
| `application_repository.py` | Application tracking |
| `resume_repository.py` | Resume data access |
| `cover_letter_repository.py` | Cover letter management |
| `monitoring_repository.py` | System and AI activity monitoring |
| `file_repository.py` | File metadata and storage tracking |
| `config_repository.py` | System configuration persistence |

## CONVENTIONS
- **Async First**: All data access methods must be `async`.
- **Transaction Management**: Use `async with session.begin()` for write operations to ensure ACID compliance.
- **Efficient Loading**: Use `selectinload` (or `joinedload` where appropriate) for relationship loading to avoid N+1 problems.
- **Error Handling**: Raise typed exceptions (e.g., `EntityNotFoundError`, `DuplicateEntryError`) for data errors instead of returning `None` or letting SQLAlchemy errors leak.
- **Repository Pattern**: Maintain clear boundaries between the data access layer and the service layer.
- **Type Safety**: Use Pydantic models or SQLAlchemy models for return types with full type hint coverage.

## ANTI-PATTERNS
- **No Business Logic**: Repositories should only handle data persistence. Complex logic belongs in the service layer.
- **No HTTP Handling**: Never reference request objects, status codes, or web framework components here.
- **No Direct Session Leakage**: Avoid returning raw SQLAlchemy Query objects; return materialized results or scalars.
- **Avoid Lazy Loading**: Do not rely on lazy loading in an async environment as it can lead to `MissingGreenlet` errors.

## NOTES
- **Dependency Injection**: Database sessions are injected via the constructor, typically managed by a service registry or DI container.
- **Base Repository**: Common CRUD operations may be abstracted into a base class to reduce boilerplate while maintaining type safety.
- **SQLAlchemy 2.0**: Strictly follow SQLAlchemy 2.0 style (using `select()`, `update()`, `delete()` constructs).
