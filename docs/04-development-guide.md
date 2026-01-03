# Development Guide

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (optional, SQLite for development)
- Git

### Initial Setup

#### 1. Clone Repository
```bash
git clone <repository-url>
cd ai-job-apply
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp config.env.example .env
# Edit .env with your configuration:
# - GEMINI_API_KEY (for AI features)
# - SECRET_KEY (for JWT tokens - use a strong random string)
# - JWT_SECRET_KEY (for JWT signing - use a strong random string)
# - DATABASE_URL (defaults to SQLite for development)

# Initialize database
alembic upgrade head

# Start backend
python main.py
```

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 4. Automated Setup (Recommended)
```bash
# From project root
./start-dev.sh
```

## Development Workflow

### Code Style

#### Python (Backend)
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/
```

#### TypeScript (Frontend)
```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run type-check
```

### Running Tests

#### Backend Tests
```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_application_service.py -v
```

#### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run tests in watch mode
npm test -- --watch
```

### Database Management

#### Create Migration
```bash
cd backend
alembic revision --autogenerate -m "description"
```

#### Apply Migrations
```bash
alembic upgrade head
```

#### Rollback Migration
```bash
alembic downgrade -1
```

#### Reset Database
```bash
# Delete database file (SQLite)
rm ai_job_assistant.db

# Recreate database
python setup-database.py
```

## Project Structure

### Backend Structure
```
backend/
├── src/
│   ├── api/              # API endpoints
│   ├── core/             # Business logic interfaces
│   ├── database/         # Database models and repositories
│   ├── models/           # Pydantic data models
│   ├── services/         # Service implementations
│   └── utils/            # Utility functions
├── tests/                # Test suite
├── alembic/              # Database migrations
├── templates/            # Cover letter templates
├── resumes/             # Resume storage
├── uploads/             # File uploads
└── main.py              # Application entry point
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/      # Reusable components
│   ├── pages/           # Page components
│   ├── services/        # API services
│   ├── stores/          # State management
│   ├── types/           # TypeScript types
│   └── utils/           # Utility functions
├── public/              # Static assets
└── vite.config.ts       # Vite configuration
```

## Adding New Features

### Backend Feature

#### 1. Create Service Interface
```python
# src/core/new_service.py
from abc import ABC, abstractmethod

class NewService(ABC):
    @abstractmethod
    async def operation(self, data: Data) -> Result:
        pass
```

#### 2. Implement Service
```python
# src/services/new_service.py
from ..core.new_service import NewService

class NewServiceImpl(NewService):
    async def operation(self, data: Data) -> Result:
        # Implementation
        pass
```

#### 3. Register Service
```python
# src/services/service_registry.py
# Add service provider and registration
```

#### 4. Create API Endpoint
```python
# src/api/v1/new_feature.py
from fastapi import APIRouter, HTTPException
from src.services.service_registry import service_registry

router = APIRouter()

@router.post("/operation")
async def operation(data: DataRequest):
    service = await service_registry.get_new_service()
    result = await service.operation(data)
    return result
```

#### 5. Add Tests
```python
# tests/unit/test_new_service.py
import pytest
from src.services.new_service import NewServiceImpl

@pytest.mark.asyncio
async def test_operation():
    service = NewServiceImpl()
    result = await service.operation(test_data)
    assert result is not None
```

### Frontend Feature

#### 1. Create Type Definitions
```typescript
// src/types/index.ts
export interface NewFeature {
  id: string;
  name: string;
  // ...
}
```

#### 2. Add API Service
```typescript
// src/services/api.ts
export const newFeatureService = {
  getFeature: async (id: string): Promise<NewFeature> => {
    const response = await apiClient.get(`/api/v1/new-feature/${id}`);
    return handleApiResponse(response);
  },
};
```

#### 3. Create Component
```typescript
// src/components/NewFeature.tsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { newFeatureService } from '../services/api';

export const NewFeature: React.FC = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['newFeature'],
    queryFn: () => newFeatureService.getFeature('id'),
  });

  if (isLoading) return <div>Loading...</div>;
  return <div>{data?.name}</div>;
};
```

#### 4. Add Page (if needed)
```typescript
// src/pages/NewFeaturePage.tsx
import { NewFeature } from '../components/NewFeature';

export const NewFeaturePage: React.FC = () => {
  return (
    <div>
      <h1>New Feature</h1>
      <NewFeature />
    </div>
  );
};
```

#### 5. Add Tests
```typescript
// src/components/__tests__/NewFeature.test.tsx
import { render, screen } from '@testing-library/react';
import { NewFeature } from '../NewFeature';

test('renders new feature', () => {
  render(<NewFeature />);
  expect(screen.getByText('Loading...')).toBeInTheDocument();
});
```

## Debugging

### Backend Debugging

#### Enable Debug Mode
```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG
```

#### View Logs
```bash
# Logs are written to console and file
tail -f logs/app.log
```

#### Debug API Endpoints
```bash
# Use Swagger UI
http://localhost:8000/docs

# Or use curl
curl http://localhost:8000/api/v1/applications
```

### Frontend Debugging

#### React DevTools
- Install React DevTools browser extension
- Inspect component tree and state

#### Network Debugging
- Open browser DevTools → Network tab
- Monitor API requests and responses

#### Console Logging
```typescript
console.log('Debug info', data);
```

## Code Quality

### Pre-commit Hooks
```bash
# Install hooks
make install-hooks

# Run hooks manually
make run-hooks
```

### Quality Checks
```bash
# Run all quality checks
make check-quality

# Auto-fix issues
make fix-quality
```

### Technical Debt Monitoring
```bash
# Check technical debt
make check-debt

# Generate debt report
make debt-report
```

## Performance Optimization

### Backend
- Use async/await for I/O operations
- Implement connection pooling
- Add database indexes
- Use caching for frequently accessed data

### Frontend
- Code splitting with lazy loading
- Memoization with React.memo
- Optimize bundle size
- Use React Query caching

## Common Tasks

### Add New Database Model
1. Create SQLAlchemy model in `src/database/models.py`
2. Create Pydantic model in `src/models/`
3. Create repository in `src/database/repositories/`
4. Create migration: `alembic revision --autogenerate -m "add new model"`
5. Apply migration: `alembic upgrade head`

### Add New API Endpoint
1. Create router in `src/api/v1/`
2. Add endpoint with proper validation
3. Register router in `src/api/app.py`
4. Add tests in `tests/integration/`

### Add New Frontend Page
1. Create page component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation link in `src/components/layout/Sidebar.tsx`
4. Add tests if needed

## Troubleshooting

### Backend Issues

#### Import Errors
```bash
# Ensure you're in the backend directory
cd backend

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Database Connection Errors
```bash
# Check database URL in .env
echo $DATABASE_URL

# Test connection
python -c "from src.database.config import get_database; print('OK')"
```

#### Service Initialization Errors
```bash
# Check service registry logs
tail -f logs/app.log | grep ServiceRegistry
```

### Frontend Issues

#### Build Errors
```bash
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run build
```

#### Type Errors
```bash
# Check TypeScript configuration
cat tsconfig.json

# Run type check
npm run type-check
```

#### API Connection Errors
```bash
# Check API base URL
echo $VITE_API_BASE_URL

# Test API connection
curl http://localhost:8000/health
```

## Best Practices

### Code Organization
- Keep functions small (< 20 lines)
- Keep classes focused (< 200 lines)
- Use meaningful names
- Add docstrings to public APIs

### Testing
- Write tests before implementation (TDD)
- Aim for 95%+ coverage
- Test edge cases
- Mock external dependencies

### Git Workflow
- Create feature branches
- Write descriptive commit messages
- Keep commits atomic
- Review code before merging

### Documentation
- Update README for major changes
- Document API changes
- Add inline comments for complex logic
- Keep architecture docs up to date

---

**Development Status**: Active development, following best practices

