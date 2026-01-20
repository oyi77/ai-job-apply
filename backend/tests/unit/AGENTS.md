# Unit Tests Agent Guide

**OVERVIEW**: Unit tests mirroring src/ structure with comprehensive mocking.

## STRUCTURE
- `test_*.py` files matching src modules
- `conftest.py` at backend/tests/ root
- `fixtures/test_data.py` for sample data

## WHERE TO LOOK
| Test File | Tests |
|-----------|-------|
| `test_auth_service.py` | Authentication logic |
| `test_user_repository.py` | Database operations |
| `test_models.py` | Pydantic validation |

## CONVENTIONS
- `unittest.mock` for isolation (AsyncMock for async)
- `@pytest.mark.asyncio` for async tests
- AAA pattern (Arrange, Act, Assert)
- Fixtures from `conftest.py` for mocks

## ANTI-PATTERNS
- No integration tests (use tests/integration/)
- No real database connections in unit tests

## NOTES
- Coverage gaps in middleware and utilities.
