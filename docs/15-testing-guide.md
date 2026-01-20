# Testing Guide: Comprehensive Testing Strategy

> **Testing strategies, examples, and best practices**

## Testing Philosophy

- **Coverage Targets**: 95%+ backend, 90%+ frontend
- **Test Pyramid**: Many unit tests, some integration tests, few E2E tests
- **TDD Encouraged**: Write tests before implementation when possible

## Backend Testing (pytest)

### Setup

```bash
cd backend
pip install pytest pytest-asyncio pytest-cov
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_services.py -v

# Specific test
pytest tests/unit/test_services.py::test_create_application -v

# Watch mode (requires pytest-watch)
ptw tests/
```

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, AsyncMock
from src.services.application_service import ApplicationService
from src.models.application import ApplicationCreate

@pytest.mark.asyncio
async def test_create_application():
    """Test application creation"""
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
```

### Integration Test Example

```python
import pytest
from httpx import AsyncClient
from src.api.app import create_app

@pytest.fixture
async def client():
    """Create test client"""
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_application_endpoint(client: AsyncClient):
    """Test application creation endpoint"""
    # Arrange
    data = {
        "company_name": "TechCorp",
        "position_title": "Developer",
        "status": "draft"
    }
    
    # Act
    response = await client.post("/api/v1/applications", json=data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["company_name"] == "TechCorp"
```

---

## Frontend Testing (Vitest)

### Setup

```bash
cd frontend
npm install -D vitest @testing-library/react @testing-library/user-event jsdom
```

### Running Tests

```bash
# Watch mode
npm test

# Single run
npm run test:run

# With coverage
npm run test:coverage

# UI mode
npm run test:ui
```

### Component Test Example

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ApplicationCard } from '../ApplicationCard';

describe('ApplicationCard', () => {
  const mockApplication = {
    id: 'app_123',
    company_name: 'TechCorp',
    position_title: 'Developer',
    status: 'submitted'
  };
  
  it('renders application details', () => {
    render(<ApplicationCard application={mockApplication} />);
    
    expect(screen.getByText('TechCorp')).toBeInTheDocument();
    expect(screen.getByText('Developer')).toBeInTheDocument();
  });
  
  it('calls onDelete when delete button clicked', () => {
    const onDelete = vi.fn();
    render(
      <ApplicationCard 
        application={mockApplication} 
        onDelete={onDelete} 
      />
    );
    
    fireEvent.click(screen.getByRole('button', { name: /delete/i }));
    expect(onDelete).toHaveBeenCalledWith('app_123');
  });
});
```

### Hook Test Example

```typescript
import { renderHook, act } from '@testing-library/react';
import { useAuth } from '../useAuth';

describe('useAuth', () => {
  it('logs in user successfully', async () => {
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toBeDefined();
  });
});
```

---

## Test Fixtures

### Backend Fixtures

**File**: `backend/tests/conftest.py`

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.database.config import Base

@pytest.fixture
async def db_session():
    """Provide isolated database session"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()

@pytest.fixture
def sample_application():
    """Provide sample application data"""
    return {
        "company_name": "TechCorp",
        "position_title": "Developer",
        "status": "draft"
    }
```

### Frontend Test Setup

**File**: `frontend/src/test/setup.ts`

```typescript
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);

afterEach(() => {
  cleanup();
});
```

---

## Mocking Strategies

### Mocking API Calls (Frontend)

```typescript
import { vi } from 'vitest';
import { api } from '@/services/api';

vi.mock('@/services/api', () => ({
  api: {
    getApplications: vi.fn(() => Promise.resolve([
      { id: '1', company_name: 'Test' }
    ])),
    createApplication: vi.fn((data) => Promise.resolve({
      id: '123',
      ...data
    }))
  }
}));
```

### Mocking External Services (Backend)

```python
from unittest.mock import patch, AsyncMock

@patch('src.services.gemini_ai_service.genai.GenerativeModel')
async def test_ai_service(mock_model):
    """Test AI service with mocked Gemini API"""
    # Setup mock
    mock_instance = mock_model.return_value
    mock_instance.generate_content_async = AsyncMock(
        return_value=Mock(text="Optimized resume")
    )
    
    # Test
    service = GeminiAIService()
    result = await service.optimize_resume("resume text", "job desc")
    
    assert "Optimized resume" in result["content"]
```

---

## Coverage Analysis

### Backend Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Coverage by file
pytest tests/ --cov=src --cov-report=term-missing
```

### Frontend Coverage

```bash
# Generate coverage report
npm run test:coverage

# View report
open coverage/index.html
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=src
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm run test:run
```

---

**Last Updated**: 2026-01-20  
**Backend**: pytest, pytest-asyncio  
**Frontend**: Vitest, React Testing Library
