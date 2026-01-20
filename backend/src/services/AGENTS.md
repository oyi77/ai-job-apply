# Services

**OVERVIEW**: Service implementations with AI, file, and application logic.

## WHERE TO LOOK
| File | Purpose |
|------|---------|
| `service_registry.py` | Dependency injection container |
| `gemini_ai_service.py` | AI resume/cover letter generation |
| `memory_based_application_service.py` | Application tracking |
| `local_file_service.py` | Secure file operations |
| `file_based_resume_service.py` | Resume processing |

## CONVENTIONS
- Async methods with `AsyncMock` for testing
- Dependency injection via constructor
- Graceful fallbacks when external services unavailable

## ANTI-PATTERNS
- No synchronous I/O operations
- No direct database access in services (use repositories)

## NOTES
Services are instantiated via `ServiceRegistry` with lifecycle management.
