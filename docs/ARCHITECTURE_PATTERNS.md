# Architecture & Design Patterns

## ✅ Implemented Design Patterns

This project implements **standard enterprise system design patterns** including:

1. **Provider Pattern** - Service abstraction and implementation
2. **Dependency Injection** - Loose coupling via service registry
3. **Repository Pattern** - Data access abstraction
4. **Strategy Pattern** - Multiple AI provider implementations
5. **Factory Pattern** - Service and repository creation

---

## 1. Provider Pattern

### Service Provider Interface

```python
# backend/src/services/service_registry.py
class ServiceProvider(ABC):
    """Abstract base class for service providers."""
    
    @abstractmethod
    def get_service(self) -> Any:
        """Get the service instance."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up the service."""
        pass
```

### Provider Implementations

Each service has a dedicated provider that manages its lifecycle:

- `LocalFileServiceProvider` - File operations
- `UnifiedAIServiceProvider` - AI services with multiple providers
- `ResumeServiceProvider` - Resume management (depends on FileService)
- `ApplicationServiceProvider` - Application tracking (depends on FileService)
- `CoverLetterServiceProvider` - Cover letters (depends on AIService)
- `JobSearchServiceProvider` - Job search
- `JWTAuthServiceProvider` - Authentication
- `MonitoringServiceProvider` - System monitoring
- `ExportServiceProvider` - Data export

### AI Provider Pattern

Separate provider pattern for AI services:

```python
# backend/src/core/ai_provider.py
class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the AI provider."""
        pass
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text using the AI provider."""
        pass

# Implementations:
# - OpenAIProvider
# - CursorProvider
# - OpenRouterProvider
# - LocalAIProvider
```

**Benefits:**
- ✅ Easy to swap implementations
- ✅ Clear separation of concerns
- ✅ Lifecycle management
- ✅ Testability

---

## 2. Dependency Injection (DI)

### Service Registry

The `ServiceRegistry` acts as a **dependency injection container**:

```python
# backend/src/services/service_registry.py
class ServiceRegistry:
    """Unified service registry with dependency injection and lifecycle management."""
    
    def __init__(self):
        self._services: Dict[str, ServiceProvider] = {}
        self._instances: Dict[str, Any] = {}
    
    def register_service(self, name: str, provider: ServiceProvider) -> None:
        """Register a service provider."""
        self._services[name] = provider
    
    async def get_service(self, name: str) -> Any:
        """Get a service instance by name."""
        return self._instances[name]
    
    # Type-safe convenience methods
    async def get_ai_service(self) -> AIService:
        return await self.get_service('ai_service')
    
    async def get_file_service(self) -> FileService:
        return await self.get_service('file_service')
```

### Dependency Resolution

Dependencies are injected via constructor:

```python
# Example: ResumeServiceProvider receives FileService dependency
class ResumeServiceProvider(ServiceProvider):
    def __init__(self, file_service: FileService):
        self.file_service = file_service  # ✅ Dependency injected
    
    async def initialize(self) -> None:
        # Use injected dependency
        self._service = ResumeService(self.file_service, repository)

# Usage in registry:
resume_provider = ResumeServiceProvider(
    self._instances['file_service']  # ✅ Dependency injected
)
```

### Initialization Order

Services are initialized in **dependency order**:

```python
async def _initialize_core_services(self) -> None:
    # 1. Core services (no dependencies)
    await self._initialize_auth_service()
    await self._initialize_file_service()
    await self._initialize_ai_service()
    
async def _initialize_business_services(self) -> None:
    # 2. Business services (depend on core services)
    resume_provider = ResumeServiceProvider(
        self._instances['file_service']  # ✅ Uses already initialized service
    )
```

**Benefits:**
- ✅ Loose coupling - services don't know about each other
- ✅ Easy testing - can inject mocks
- ✅ Single responsibility - each service has one job
- ✅ Centralized configuration

---

## 3. Repository Pattern

### Repository Interface

```python
# backend/src/database/repositories/
class ApplicationRepository:
    """Repository for application data access."""
    
    async def create(self, application: JobApplication) -> JobApplication:
        """Create a new application."""
        pass
    
    async def get_by_id(self, id: str) -> Optional[JobApplication]:
        """Get application by ID."""
        pass
    
    async def update(self, application: JobApplication) -> JobApplication:
        """Update an application."""
        pass
```

### Repository Factory

```python
# backend/src/services/repository_factory.py
class RepositoryFactory:
    """Factory for creating repositories."""
    
    async def create_repository(self, repo_class: Type) -> Any:
        """Create a repository instance."""
        async with database_config.get_session() as session:
            return repo_class(session)
```

**Benefits:**
- ✅ Data access abstraction
- ✅ Easy to swap data sources (database, in-memory, API)
- ✅ Testability - can mock repositories
- ✅ Separation of concerns

---

## 4. Strategy Pattern (AI Providers)

### Multiple Provider Implementations

```python
# backend/src/services/ai_provider_manager.py
class AIProviderManager:
    """Manages multiple AI providers with fallback support."""
    
    async def _create_provider(self, config: AIProviderConfig) -> Optional[AIProvider]:
        """Create provider based on configuration."""
        if config.provider_name == "openai":
            return OpenAIProvider(config)
        elif config.provider_name == "cursor":
            return CursorProvider(config)
        elif config.provider_name == "openrouter":
            return OpenRouterProvider(config)
        # ... more providers
    
    async def get_available_provider(self) -> Optional[AIProvider]:
        """Get first available provider (fallback strategy)."""
        for provider_name in self.provider_order:
            provider = self.providers.get(provider_name)
            if provider and await provider.is_available():
                return provider
        return None
```

**Benefits:**
- ✅ Multiple implementations of same interface
- ✅ Automatic fallback when one provider fails
- ✅ Easy to add new providers
- ✅ Runtime provider selection

---

## 5. Factory Pattern

### Service Factory

The `ServiceRegistry` acts as a factory for services:

```python
# Services are created by their providers
file_provider = LocalFileServiceProvider()
await file_provider.initialize()
service = file_provider.get_service()  # ✅ Factory creates service
```

### Repository Factory

```python
# backend/src/services/repository_factory.py
repository = await repository_factory.create_repository(ResumeRepository)
```

**Benefits:**
- ✅ Centralized object creation
- ✅ Hides creation complexity
- ✅ Consistent initialization

---

## Architecture Layers

```
┌─────────────────────────────────────────┐
│         API Layer (FastAPI)             │
│  - Endpoints                            │
│  - Request/Response handling            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Service Layer (Business Logic)    │
│  - ServiceRegistry (DI Container)       │
│  - ServiceProvider implementations      │
│  - Business logic services              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Repository Layer (Data Access)     │
│  - RepositoryFactory                    │
│  - Repository implementations           │
│  - Data access abstraction              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Database Layer (SQLAlchemy)        │
│  - Models                                │
│  - Database configuration                │
└─────────────────────────────────────────┘
```

---

## SOLID Principles

### ✅ Single Responsibility Principle (SRP)
- Each service has one clear responsibility
- Providers only manage service lifecycle
- Repositories only handle data access

### ✅ Open/Closed Principle (OCP)
- Services are open for extension via providers
- Closed for modification (interface-based)

### ✅ Liskov Substitution Principle (LSP)
- Any provider can replace another if they implement the interface
- AI providers are interchangeable

### ✅ Interface Segregation Principle (ISP)
- Small, focused interfaces (AIService, FileService, etc.)
- Clients only depend on methods they use

### ✅ Dependency Inversion Principle (DIP)
- High-level modules depend on abstractions (interfaces)
- Low-level modules implement abstractions
- ServiceRegistry injects dependencies

---

## Design Pattern Summary

| Pattern | Implementation | Location |
|---------|---------------|----------|
| **Provider Pattern** | ServiceProvider, AIProvider | `services/service_registry.py`, `core/ai_provider.py` |
| **Dependency Injection** | ServiceRegistry | `services/service_registry.py` |
| **Repository Pattern** | Repository classes | `database/repositories/` |
| **Factory Pattern** | RepositoryFactory, ServiceRegistry | `services/repository_factory.py`, `services/service_registry.py` |
| **Strategy Pattern** | AIProviderManager | `services/ai_provider_manager.py` |
| **Abstract Factory** | ServiceProvider implementations | `services/service_registry.py` |

---

## Benefits of This Architecture

1. **Testability** - Easy to mock dependencies
2. **Maintainability** - Clear separation of concerns
3. **Extensibility** - Easy to add new services/providers
4. **Flexibility** - Swap implementations without changing code
5. **Scalability** - Services can be scaled independently
6. **Type Safety** - Strong typing with interfaces
7. **Lifecycle Management** - Proper initialization and cleanup

---

## Usage Example

```python
# Get service from registry (DI)
ai_service = await service_registry.get_ai_service()

# Use service (doesn't know about implementation)
result = await ai_service.optimize_resume(request)

# Service internally uses AIProviderManager (Strategy Pattern)
# Which selects available provider (OpenAI, Cursor, etc.)
```

---

**Status**: ✅ **All standard enterprise patterns are fully implemented!**

This architecture follows industry best practices and is production-ready.

