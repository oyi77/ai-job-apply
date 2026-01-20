# 🤖 AGENTS.md: Core Service Interfaces

## OVERVIEW
Abstract base classes (ABCs) defining service contracts for the application's business logic.

## STRUCTURE
N/A

## WHERE TO LOOK
| File | Purpose |
|------|---------|
| `ai_service.py` | AI service interface contract for optimization and generation |
| `application_service.py` | Application tracking interface for lifecycle management |
| `resume_service.py` | Resume management interface for file processing and metadata |
| `file_service.py` | File operations interface for secure storage and validation |

## CONVENTIONS
- All interfaces use `@abstractmethod` decorators to enforce implementation.
- Async method signatures only (`async def`) to support modern I/O.
- Typed exceptions defined per interface for consistent error handling.
- Comprehensive docstrings for all interface methods.
- Full type hint coverage for parameters and return values.

## ANTI-PATTERNS
- **Never implement interfaces directly in this directory.**
- **No business logic allowed.** This directory must only contain abstractions.
- Avoid adding concrete helper methods; keep them in utility or implementation layers.

## NOTES
- Concrete implementations live in `backend/src/services/`.
- Dependency injection is handled via the `ServiceRegistry` to maintain loose coupling.
- These interfaces follow SOLID principles, specifically Interface Segregation and Dependency Inversion.
