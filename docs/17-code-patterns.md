# Code Patterns: Reusable Implementation Patterns

> **Common code patterns and best practices**

## Backend Patterns

### 1. Repository Pattern

**When to use**: All database operations

**Implementation**:

```python
# Step 1: Define interface (src/core/)
from abc import ABC, abstractmethod

class IApplicationRepository(ABC):
    @abstractmethod
    async def create(self, data: ApplicationCreate) -> Application:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Application]:
        pass

# Step 2: Implement repository (src/database/repositories/)
class ApplicationRepository(IApplicationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: ApplicationCreate) -> Application:
        application = Application(**data.model_dump())
        self.session.add(application)
        await self.session.commit()
        await self.session.refresh(application)
        return application

# Step 3: Use in service
class ApplicationService:
    def __init__(self, repo: IApplicationRepository):
        self.repo = repo
    
    async def create_application(self, data: ApplicationCreate) -> Application:
        return await self.repo.create(data)
```

---

### 2. Service Pattern

**When to use**: Business logic implementation

**Implementation**:

```python
# Service with dependency injection
class ApplicationService(IApplicationService):
    def __init__(
        self,
        repository: IApplicationRepository,
        resume_repo: IResumeRepository,
        logger: Logger
    ):
        self.repository = repository
        self.resume_repo = resume_repo
        self.logger = logger
    
    async def create_application(
        self,
        data: ApplicationCreate,
        user_id: str
    ) -> ApplicationResponse:
        # Validation
        if data.resume_id:
            resume = await self.resume_repo.get_by_id(data.resume_id)
            if not resume or resume.user_id != user_id:
                raise ValueError("Invalid resume")
        
        # Business logic
        application = await self.repository.create(data, user_id)
        
        # Logging
        self.logger.info(f"Application created: {application.id}")
        
        return ApplicationResponse.model_validate(application)
```

---

### 3. API Endpoint Pattern

**When to use**: Creating new API endpoints

**Implementation**:

```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/applications", tags=["applications"])

# Dependency injection
def get_service() -> ApplicationService:
    registry = get_service_registry()
    return registry.get_service("application")

# List endpoint
@router.get("/", response_model=List[ApplicationResponse])
async def list_applications(
    skip: int = 0,
    limit: int = 100,
    service: ApplicationService = Depends(get_service)
):
    """List all applications"""
    return await service.list_applications(skip=skip, limit=limit)

# Get endpoint
@router.get("/{id}", response_model=ApplicationResponse)
async def get_application(
    id: str,
    service: ApplicationService = Depends(get_service)
):
    """Get application by ID"""
    application = await service.get_application(id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    return application

# Create endpoint
@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreate,
    service: ApplicationService = Depends(get_service)
):
    """Create a new application"""
    return await service.create_application(data)
```

---

### 4. Error Handling Pattern

**When to use**: All service methods

**Implementation**:

```python
from src.utils.logger import logger

async def risky_operation(self, data: Any) -> Result:
    """Operation with comprehensive error handling"""
    try:
        # Validate
        self._validate_input(data)
        
        # Execute
        result = await self._execute(data)
        
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

---

### 5. Async/Await Pattern

**When to use**: All I/O operations

**Implementation**:

```python
# Async database operations
async def get_applications(self, user_id: str) -> List[Application]:
    result = await self.session.execute(
        select(Application).where(Application.user_id == user_id)
    )
    return list(result.scalars().all())

# Async external API calls
async def call_ai_service(self, prompt: str) -> str:
    response = await self.model.generate_content_async(prompt)
    return response.text

# Concurrent operations
async def process_multiple(self, items: List[str]) -> List[Result]:
    tasks = [self.process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Frontend Patterns

### 1. React Component Pattern

**When to use**: All UI components

**Implementation**:

```typescript
import React, { useState, useEffect } from 'react';

interface ComponentProps {
  title: string;
  onAction?: () => void;
  className?: string;
}

export const MyComponent: React.FC<ComponentProps> = ({
  title,
  onAction,
  className = ''
}) => {
  const [state, setState] = useState<string>('');
  
  useEffect(() => {
    // Component mount logic
    return () => {
      // Cleanup
    };
  }, []);
  
  const handleClick = () => {
    onAction?.();
  };
  
  return (
    <div className={`component ${className}`}>
      <h2>{title}</h2>
      <button onClick={handleClick}>Action</button>
    </div>
  );
};
```

---

### 2. Form Handling Pattern

**When to use**: All forms

**Implementation**:

```typescript
import { useForm } from 'react-hook-form';

interface FormData {
  company_name: string;
  position_title: string;
}

export const ApplicationForm: React.FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();
  
  const onSubmit = async (data: FormData) => {
    try {
      await api.createApplication(data);
      // Success handling
    } catch (error) {
      // Error handling
    }
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('company_name', { 
          required: 'Company name is required',
          minLength: { value: 1, message: 'Too short' }
        })}
        placeholder="Company Name"
      />
      {errors.company_name && <span>{errors.company_name.message}</span>}
      
      <button type="submit">Submit</button>
    </form>
  );
};
```

---

### 3. State Management Pattern

**When to use**: Global application state

**Implementation**:

```typescript
// Zustand store
import create from 'zustand';

interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  isAuthenticated: false,
  
  setUser: (user) => set({ user, isAuthenticated: true }),
  
  logout: () => set({ user: null, isAuthenticated: false }),
}));

// Usage in component
const { user, setUser, logout } = useAppStore();
```

---

### 4. API Integration Pattern

**When to use**: All API calls

**Implementation**:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const ApplicationsList: React.FC = () => {
  const queryClient = useQueryClient();
  
  // Fetch data
  const { data, isLoading, error } = useQuery({
    queryKey: ['applications'],
    queryFn: () => api.getApplications()
  });
  
  // Mutation
  const createMutation = useMutation({
    mutationFn: (data: ApplicationCreate) => api.createApplication(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    }
  });
  
  if (isLoading) return <Loading />;
  if (error) return <Error message={error.message} />;
  
  return (
    <div>
      {data?.map(app => (
        <ApplicationCard key={app.id} application={app} />
      ))}
      <button onClick={() => createMutation.mutate(newData)}>
        Create
      </button>
    </div>
  );
};
```

---

### 5. Custom Hook Pattern

**When to use**: Reusable logic

**Implementation**:

```typescript
export const useAuth = () => {
  const { user, setUser, logout: storeLogout } = useAppStore();
  const navigate = useNavigate();
  
  const login = async (email: string, password: string) => {
    const response = await api.login(email, password);
    localStorage.setItem('token', response.access_token);
    const userData = await api.getCurrentUser();
    setUser(userData);
    navigate('/dashboard');
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    storeLogout();
    navigate('/login');
  };
  
  return { user, login, logout, isAuthenticated: !!user };
};

// Usage
const { user, login, logout } = useAuth();
```

---

## Testing Patterns

### Backend Unit Test Pattern

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_service_method():
    # Arrange
    mock_repo = Mock()
    mock_repo.method = AsyncMock(return_value=expected_result)
    service = Service(mock_repo)
    
    # Act
    result = await service.method(input_data)
    
    # Assert
    assert result == expected_result
    mock_repo.method.assert_called_once_with(input_data)
```

### Frontend Component Test Pattern

```typescript
import { render, screen, fireEvent } from '@testing-library/react';

describe('Component', () => {
  it('renders and handles interaction', () => {
    const onAction = vi.fn();
    render(<Component onAction={onAction} />);
    
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
    
    fireEvent.click(screen.getByRole('button'));
    expect(onAction).toHaveBeenCalled();
  });
});
```

---

**Last Updated**: 2026-01-20  
**Purpose**: Reusable code patterns for consistent implementation  
**Coverage**: Backend and frontend patterns
