# Utils

**OVERVIEW**: Helper functions, validators, and security utilities.

## WHERE TO LOOK
| File | Purpose |
|------|---------|
| `validators/` | Auth and input validation |
| `sanitization.py` | XSS prevention, text cleaning |
| `text_processing.py` | Content extraction |
| `file_security.py` | Upload validation, path sanitization |
| `logger.py` | Structured logging setup |

## CONVENTIONS
- Pure functions where possible
- Comprehensive type hints
- Centralized logging configuration

## ANTI-PATTERNS
- No business logic
- No database operations

## NOTES
Security-critical code lives here.
