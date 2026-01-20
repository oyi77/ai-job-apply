# Models

**OVERVIEW**: Pydantic request/response models with validation.

## WHERE TO LOOK
| Model | Purpose |
|-------|---------|
| `UserCreate` | Registration validation |
| `ApplicationResponse` | API response format |
| `JobSearchQuery` | Search parameters |
| `ResumeUpdate` | Resume modification validation |

## CONVENTIONS
- BaseModel inheritance with strict types
- Field validators for complex logic
- Response models exclude sensitive data
- Request models for input validation

## ANTI-PATTERNS
- No database operations (use repositories)
- No business logic (use services)

## NOTES
SQLAlchemy models live in `database/models.py`, not here.
