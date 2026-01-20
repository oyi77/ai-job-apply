# Service Layer: Architecture and Implementation

> **Service layer design patterns and implementations**

## Service Architecture Overview

The service layer implements business logic using dependency injection and the repository pattern.

**Architecture**:
```
API Layer (FastAPI) → Service Layer → Repository Layer → Database
```

## Service Registry

**File**: `backend/src/services/service_registry.py`

Centralized service management with dependency injection.

```python
class ServiceRegistry:
    """Manages service lifecycle and dependencies"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self._services: Dict[str, Any] = {}
    
    async def initialize(self):
        """Initialize all services"""
        await self._initialize_repositories()
        await self._initialize_services()
    
    def get_service(self, name: str) -> Any:
        """Get service by name"""
        return self._services.get(name)
```

## Core Services

### AI Service

**Interface**: `src/core/ai_service.py`  
**Implementation**: `src/services/gemini_ai_service.py`

```python
class IAIService(ABC):
    """AI service interface"""
    
    @abstractmethod
    async def optimize_resume(
        self, 
        resume_text: str, 
        job_description: str
    ) -> Dict[str, Any]:
        """Optimize resume for job"""
        pass
    
    @abstractmethod
    async def generate_cover_letter(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        resume_summary: str
    ) -> Dict[str, Any]:
        """Generate cover letter"""
        pass
```

**Usage**:
```python
# In API endpoint
from src.services.service_registry import get_service_registry

def get_ai_service() -> IAIService:
    registry = get_service_registry()
    return registry.get_service("ai")

@router.post("/optimize-resume")
async def optimize_resume(
    data: ResumeOptimizeRequest,
    service: IAIService = Depends(get_ai_service)
):
    result = await service.optimize_resume(
        data.resume_text,
        data.job_description
    )
    return result
```

---

### Application Service

**Interface**: `src/core/application_service.py`  
**Implementation**: `src/services/application_service.py`

Handles application business logic including validation and workflow.

```python
class ApplicationService(IApplicationService):
    """Application business logic"""
    
    def __init__(self, repository: IApplicationRepository):
        self.repository = repository
    
    async def create_application(
        self,
        data: ApplicationCreate,
        user_id: str
    ) -> ApplicationResponse:
        """Create application with validation"""
        # Validate resume exists
        if data.resume_id:
            resume = await self.resume_repo.get_by_id(data.resume_id)
            if not resume or resume.user_id != user_id:
                raise ValueError("Invalid resume")
        
        # Create application
        application = await self.repository.create(data, user_id)
        
        # Log activity
        await self.log_activity("application_created", application.id)
        
        return ApplicationResponse.model_validate(application)
```

---

### Authentication Service

**Interface**: `src/core/auth_service.py`  
**Implementation**: `src/services/auth_service.py`

Handles user authentication, JWT tokens, and password management.

```python
class AuthService(IAuthService):
    """Authentication business logic"""
    
    async def register_user(
        self,
        data: UserCreate
    ) -> UserResponse:
        """Register new user"""
        # Check if email exists
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")
        
        # Hash password
        password_hash = self.hash_password(data.password)
        
        # Create user
        user = await self.user_repo.create({
            **data.model_dump(exclude={'password'}),
            'password_hash': password_hash
        })
        
        return UserResponse.model_validate(user)
    
    async def login(
        self,
        email: str,
        password: str
    ) -> TokenResponse:
        """Authenticate user and return tokens"""
        # Get user
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        # Generate tokens
        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
```

---

## Service Patterns

### Error Handling Pattern

```python
from src.utils.logger import logger

class YourService:
    async def risky_operation(self, data: Any) -> Result:
        """Operation with comprehensive error handling"""
        try:
            # Validate input
            self._validate_input(data)
            
            # Perform operation
            result = await self._perform_operation(data)
            
            # Log success
            logger.info(f"Operation successful: {result.id}")
            
            return result
            
        except ValidationError as e:
            logger.warning(f"Validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
            
        except DatabaseError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
            
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal error")
```

### Fallback Pattern

```python
class AIService:
    async def optimize_resume(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """AI operation with fallback"""
        try:
            # Try primary AI service
            result = await self._call_gemini_api(resume_text, job_description)
            return result
            
        except ServiceUnavailableError:
            logger.warning("AI service unavailable, using fallback")
            
            # Return fallback response
            return {
                "success": True,
                "optimized_content": resume_text,
                "suggestions": [
                    "AI service temporarily unavailable",
                    "Please try again later"
                ],
                "fallback": True
            }
```

### Caching Pattern

```python
from functools import lru_cache
from typing import Optional

class ConfigService:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    async def get_config(self, key: str) -> Optional[Any]:
        """Get config with caching"""
        # Check cache
        if key in self._cache:
            logger.debug(f"Config cache hit: {key}")
            return self._cache[key]
        
        # Fetch from database
        config = await self.repository.get_by_key(key)
        
        # Cache result
        if config:
            self._cache[key] = config.value
        
        return config.value if config else None
    
    def clear_cache(self):
        """Clear config cache"""
        self._cache.clear()
        logger.info("Config cache cleared")
```

---

## Testing Services

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, AsyncMock
from src.services.application_service import ApplicationService

@pytest.mark.asyncio
async def test_create_application_success():
    """Test successful application creation"""
    # Arrange
    mock_repo = Mock()
    mock_repo.create = AsyncMock(return_value=Mock(
        id="app_123",
        company_name="TechCorp",
        status="draft"
    ))
    
    service = ApplicationService(mock_repo)
    data = ApplicationCreate(
        company_name="TechCorp",
        position_title="Developer"
    )
    
    # Act
    result = await service.create_application(data, "user_123")
    
    # Assert
    assert result.id == "app_123"
    assert result.company_name == "TechCorp"
    mock_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_application_validation_error():
    """Test validation error handling"""
    # Arrange
    mock_repo = Mock()
    service = ApplicationService(mock_repo)
    data = ApplicationCreate(
        company_name="",  # Invalid: empty
        position_title="Developer"
    )
    
    # Act & Assert
    with pytest.raises(ValueError):
        await service.create_application(data, "user_123")
```

---

**Last Updated**: 2026-01-20  
**Pattern**: Service layer with dependency injection  
**For complete service list, see**: [08-codebase-map.md](./08-codebase-map.md)
