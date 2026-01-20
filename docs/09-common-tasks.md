# Common Tasks Guide: Step-by-Step Instructions

> **Practical guides for common development tasks**

## Table of Contents
- [Adding a New API Endpoint](#adding-a-new-api-endpoint)
- [Creating a New Database Model](#creating-a-new-database-model)
- [Adding a New Service](#adding-a-new-service)
- [Creating a New React Component](#creating-a-new-react-component)
- [Implementing a New AI Feature](#implementing-a-new-ai-feature)
- [Adding Database Migrations](#adding-database-migrations)
- [Writing Tests](#writing-tests)

---

## Adding a New API Endpoint

### Step 1: Define Pydantic Schemas

**File**: `backend/src/models/your_feature.py`

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class YourFeatureBase(BaseModel):
    """Base schema for your feature"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class YourFeatureCreate(YourFeatureBase):
    """Schema for creating a new feature"""
    pass

class YourFeatureUpdate(BaseModel):
    """Schema for updating a feature"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

class YourFeatureResponse(YourFeatureBase):
    """Schema for feature response"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### Step 2: Create API Endpoint

**File**: `backend/src/api/v1/your_feature.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.models.your_feature import (
    YourFeatureCreate,
    YourFeatureUpdate,
    YourFeatureResponse
)
from src.services.your_feature_service import YourFeatureService
from src.services.service_registry import get_service_registry

router = APIRouter(prefix="/your-feature", tags=["your-feature"])

def get_service() -> YourFeatureService:
    """Dependency to get service instance"""
    registry = get_service_registry()
    return registry.get_service("your_feature")

@router.get("/", response_model=List[YourFeatureResponse])
async def list_features(
    skip: int = 0,
    limit: int = 100,
    service: YourFeatureService = Depends(get_service)
):
    """List all features"""
    return await service.list_features(skip=skip, limit=limit)

@router.get("/{feature_id}", response_model=YourFeatureResponse)
async def get_feature(
    feature_id: str,
    service: YourFeatureService = Depends(get_service)
):
    """Get feature by ID"""
    feature = await service.get_feature(feature_id)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    return feature

@router.post("/", response_model=YourFeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_feature(
    data: YourFeatureCreate,
    service: YourFeatureService = Depends(get_service)
):
    """Create a new feature"""
    return await service.create_feature(data)

@router.put("/{feature_id}", response_model=YourFeatureResponse)
async def update_feature(
    feature_id: str,
    data: YourFeatureUpdate,
    service: YourFeatureService = Depends(get_service)
):
    """Update a feature"""
    feature = await service.update_feature(feature_id, data)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
    return feature

@router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(
    feature_id: str,
    service: YourFeatureService = Depends(get_service)
):
    """Delete a feature"""
    success = await service.delete_feature(feature_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature not found"
        )
```

### Step 3: Register Router

**File**: `backend/src/api/v1/__init__.py`

```python
from fastapi import APIRouter
from .your_feature import router as your_feature_router

api_router = APIRouter()

# ... existing routers ...
api_router.include_router(your_feature_router)
```

### Step 4: Add Frontend API Client

**File**: `frontend/src/services/api.ts`

```typescript
// Add to api.ts
export const yourFeatureApi = {
  list: async (params?: { skip?: number; limit?: number }) => {
    const response = await apiClient.get<YourFeature[]>('/your-feature', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await apiClient.get<YourFeature>(`/your-feature/${id}`);
    return response.data;
  },

  create: async (data: YourFeatureCreate) => {
    const response = await apiClient.post<YourFeature>('/your-feature', data);
    return response.data;
  },

  update: async (id: string, data: YourFeatureUpdate) => {
    const response = await apiClient.put<YourFeature>(`/your-feature/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await apiClient.delete(`/your-feature/${id}`);
  },
};
```

### Step 5: Add TypeScript Types

**File**: `frontend/src/types/index.ts`

```typescript
export interface YourFeature {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface YourFeatureCreate {
  name: string;
  description?: string;
}

export interface YourFeatureUpdate {
  name?: string;
  description?: string;
}
```

### Step 6: Test the Endpoint

```bash
# Start backend
cd backend
python main.py

# Test with curl
curl -X POST http://localhost:8000/api/v1/your-feature \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Feature", "description": "Test"}'

# Or visit http://localhost:8000/docs for Swagger UI
```

---

## Creating a New Database Model

### Step 1: Define SQLAlchemy Model

**File**: `backend/src/database/models.py`

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class YourModel(Base):
    """Your model description"""
    __tablename__ = "your_models"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Fields
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="your_models")
    
    # Indexes
    __table_args__ = (
        Index('idx_your_model_user_id', 'user_id'),
        Index('idx_your_model_created_at', 'created_at'),
    )
```

### Step 2: Update User Model (if needed)

**File**: `backend/src/database/models.py`

```python
class User(Base):
    # ... existing fields ...
    
    # Add relationship
    your_models = relationship("YourModel", back_populates="user", cascade="all, delete-orphan")
```

### Step 3: Create Repository Interface

**File**: `backend/src/core/your_model_repository.py`

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.your_feature import YourFeatureCreate, YourFeatureUpdate
from src.database.models import YourModel

class IYourModelRepository(ABC):
    """Repository interface for YourModel"""
    
    @abstractmethod
    async def create(self, data: YourFeatureCreate, user_id: str) -> YourModel:
        """Create a new model"""
        pass
    
    @abstractmethod
    async def get_by_id(self, model_id: str) -> Optional[YourModel]:
        """Get model by ID"""
        pass
    
    @abstractmethod
    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[YourModel]:
        """List models by user"""
        pass
    
    @abstractmethod
    async def update(self, model_id: str, data: YourFeatureUpdate) -> Optional[YourModel]:
        """Update a model"""
        pass
    
    @abstractmethod
    async def delete(self, model_id: str) -> bool:
        """Delete a model"""
        pass
```

### Step 4: Implement Repository

**File**: `backend/src/database/repositories/your_model_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from src.core.your_model_repository import IYourModelRepository
from src.database.models import YourModel
from src.models.your_feature import YourFeatureCreate, YourFeatureUpdate

class YourModelRepository(IYourModelRepository):
    """Repository implementation for YourModel"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: YourFeatureCreate, user_id: str) -> YourModel:
        """Create a new model"""
        model = YourModel(
            **data.model_dump(),
            user_id=user_id
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model
    
    async def get_by_id(self, model_id: str) -> Optional[YourModel]:
        """Get model by ID"""
        result = await self.session.execute(
            select(YourModel).where(YourModel.id == model_id)
        )
        return result.scalar_one_or_none()
    
    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[YourModel]:
        """List models by user"""
        result = await self.session.execute(
            select(YourModel)
            .where(YourModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(YourModel.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update(self, model_id: str, data: YourFeatureUpdate) -> Optional[YourModel]:
        """Update a model"""
        model = await self.get_by_id(model_id)
        if not model:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(model, key, value)
        
        await self.session.commit()
        await self.session.refresh(model)
        return model
    
    async def delete(self, model_id: str) -> bool:
        """Delete a model"""
        model = await self.get_by_id(model_id)
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
```

### Step 5: Create Migration

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add your_models table"

# Review the generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

### Step 6: Verify Database

```bash
# Connect to database
sqlite3 backend/app.db  # or psql for PostgreSQL

# Check table
.schema your_models

# Exit
.quit
```

---

## Adding a New Service

### Step 1: Define Service Interface

**File**: `backend/src/core/your_feature_service.py`

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.your_feature import (
    YourFeatureCreate,
    YourFeatureUpdate,
    YourFeatureResponse
)

class IYourFeatureService(ABC):
    """Service interface for your feature"""
    
    @abstractmethod
    async def create_feature(self, data: YourFeatureCreate) -> YourFeatureResponse:
        """Create a new feature"""
        pass
    
    @abstractmethod
    async def get_feature(self, feature_id: str) -> Optional[YourFeatureResponse]:
        """Get feature by ID"""
        pass
    
    @abstractmethod
    async def list_features(self, skip: int = 0, limit: int = 100) -> List[YourFeatureResponse]:
        """List all features"""
        pass
    
    @abstractmethod
    async def update_feature(
        self, 
        feature_id: str, 
        data: YourFeatureUpdate
    ) -> Optional[YourFeatureResponse]:
        """Update a feature"""
        pass
    
    @abstractmethod
    async def delete_feature(self, feature_id: str) -> bool:
        """Delete a feature"""
        pass
```

### Step 2: Implement Service

**File**: `backend/src/services/your_feature_service.py`

```python
from typing import List, Optional
from src.core.your_feature_service import IYourFeatureService
from src.core.your_model_repository import IYourModelRepository
from src.models.your_feature import (
    YourFeatureCreate,
    YourFeatureUpdate,
    YourFeatureResponse
)
from src.utils.logger import logger

class YourFeatureService(IYourFeatureService):
    """Service implementation for your feature"""
    
    def __init__(self, repository: IYourModelRepository):
        self.repository = repository
        logger.info("YourFeatureService initialized")
    
    async def create_feature(self, data: YourFeatureCreate) -> YourFeatureResponse:
        """Create a new feature"""
        logger.info(f"Creating feature: {data.name}")
        
        # Business logic here
        model = await self.repository.create(data, user_id="system")  # Get from auth
        
        return YourFeatureResponse.model_validate(model)
    
    async def get_feature(self, feature_id: str) -> Optional[YourFeatureResponse]:
        """Get feature by ID"""
        logger.info(f"Getting feature: {feature_id}")
        
        model = await self.repository.get_by_id(feature_id)
        if not model:
            return None
        
        return YourFeatureResponse.model_validate(model)
    
    async def list_features(self, skip: int = 0, limit: int = 100) -> List[YourFeatureResponse]:
        """List all features"""
        logger.info(f"Listing features (skip={skip}, limit={limit})")
        
        models = await self.repository.list_by_user("system", skip=skip, limit=limit)
        
        return [YourFeatureResponse.model_validate(m) for m in models]
    
    async def update_feature(
        self, 
        feature_id: str, 
        data: YourFeatureUpdate
    ) -> Optional[YourFeatureResponse]:
        """Update a feature"""
        logger.info(f"Updating feature: {feature_id}")
        
        model = await self.repository.update(feature_id, data)
        if not model:
            return None
        
        return YourFeatureResponse.model_validate(model)
    
    async def delete_feature(self, feature_id: str) -> bool:
        """Delete a feature"""
        logger.info(f"Deleting feature: {feature_id}")
        
        return await self.repository.delete(feature_id)
```

### Step 3: Register Service

**File**: `backend/src/services/service_registry.py`

```python
# In ServiceRegistry class

async def _initialize_services(self):
    """Initialize all services"""
    # ... existing services ...
    
    # Add your service
    from src.services.your_feature_service import YourFeatureService
    from src.database.repositories.your_model_repository import YourModelRepository
    
    your_model_repo = YourModelRepository(self.db_session)
    self._services["your_feature"] = YourFeatureService(your_model_repo)
```

---

## Creating a New React Component

### Step 1: Create Component File

**File**: `frontend/src/components/YourComponent.tsx`

```typescript
import React, { useState, useEffect } from 'react';

interface YourComponentProps {
  title: string;
  onAction?: () => void;
  className?: string;
}

export const YourComponent: React.FC<YourComponentProps> = ({
  title,
  onAction,
  className = ''
}) => {
  const [state, setState] = useState<string>('');
  
  useEffect(() => {
    // Component mount logic
    return () => {
      // Cleanup logic
    };
  }, []);
  
  const handleClick = () => {
    // Handle click
    onAction?.();
  };
  
  return (
    <div className={`your-component ${className}`}>
      <h2 className="text-xl font-bold">{title}</h2>
      <button
        onClick={handleClick}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Click Me
      </button>
    </div>
  );
};
```

### Step 2: Add Component Tests

**File**: `frontend/src/components/__tests__/YourComponent.test.tsx`

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { YourComponent } from '../YourComponent';

describe('YourComponent', () => {
  it('renders with title', () => {
    render(<YourComponent title="Test Title" />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });
  
  it('calls onAction when button clicked', () => {
    const onAction = vi.fn();
    render(<YourComponent title="Test" onAction={onAction} />);
    
    fireEvent.click(screen.getByText('Click Me'));
    expect(onAction).toHaveBeenCalledTimes(1);
  });
  
  it('applies custom className', () => {
    const { container } = render(
      <YourComponent title="Test" className="custom-class" />
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
```

### Step 3: Export Component

**File**: `frontend/src/components/index.ts`

```typescript
export { YourComponent } from './YourComponent';
```

### Step 4: Use Component

**File**: `frontend/src/pages/SomePage.tsx`

```typescript
import { YourComponent } from '@/components';

export const SomePage = () => {
  const handleAction = () => {
    console.log('Action triggered!');
  };
  
  return (
    <div>
      <YourComponent 
        title="My Component" 
        onAction={handleAction}
        className="mb-4"
      />
    </div>
  );
};
```

---

## Implementing a New AI Feature

### Step 1: Add Method to AI Service Interface

**File**: `backend/src/core/ai_service.py`

```python
@abstractmethod
async def your_ai_feature(self, input_data: str) -> Dict[str, Any]:
    """Your AI feature description"""
    pass
```

### Step 2: Implement in Gemini Service

**File**: `backend/src/services/gemini_ai_service.py`

```python
async def your_ai_feature(self, input_data: str) -> Dict[str, Any]:
    """Your AI feature implementation"""
    try:
        prompt = f"""
        Analyze the following data and provide insights:
        
        Data: {input_data}
        
        Provide:
        1. Summary
        2. Key points
        3. Recommendations
        """
        
        response = await self.model.generate_content_async(prompt)
        
        return {
            "success": True,
            "result": response.text,
            "metadata": {
                "model": self.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"AI feature error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
```

### Step 3: Add API Endpoint

**File**: `backend/src/api/v1/ai.py`

```python
@router.post("/your-feature")
async def your_ai_feature(
    data: YourFeatureRequest,
    service: IAIService = Depends(get_ai_service)
):
    """Your AI feature endpoint"""
    result = await service.your_ai_feature(data.input_data)
    return result
```

### Step 4: Add Frontend Integration

**File**: `frontend/src/services/api.ts`

```typescript
export const aiApi = {
  // ... existing methods ...
  
  yourFeature: async (inputData: string) => {
    const response = await apiClient.post('/ai/your-feature', {
      input_data: inputData
    });
    return response.data;
  },
};
```

---

## Adding Database Migrations

### Step 1: Make Model Changes

Edit `backend/src/database/models.py` with your changes.

### Step 2: Generate Migration

```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "Descriptive message"

# Example: alembic revision --autogenerate -m "Add email field to users"
```

### Step 3: Review Migration

**File**: `backend/alembic/versions/xxxx_descriptive_message.py`

```python
# Review the generated migration
# Make manual adjustments if needed

def upgrade():
    # Check the upgrade operations
    pass

def downgrade():
    # Check the downgrade operations
    pass
```

### Step 4: Apply Migration

```bash
# Apply migration
alembic upgrade head

# Or apply specific version
alembic upgrade +1  # Apply one migration
```

### Step 5: Rollback (if needed)

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

---

## Writing Tests

### Backend Unit Test

**File**: `backend/tests/unit/test_your_service.py`

```python
import pytest
from unittest.mock import Mock, AsyncMock
from src.services.your_feature_service import YourFeatureService
from src.models.your_feature import YourFeatureCreate

@pytest.mark.asyncio
async def test_create_feature():
    """Test feature creation"""
    # Arrange
    mock_repo = Mock()
    mock_repo.create = AsyncMock(return_value=Mock(
        id="123",
        name="Test",
        created_at="2024-01-01"
    ))
    service = YourFeatureService(mock_repo)
    data = YourFeatureCreate(name="Test")
    
    # Act
    result = await service.create_feature(data)
    
    # Assert
    assert result.name == "Test"
    mock_repo.create.assert_called_once()
```

### Backend Integration Test

**File**: `backend/tests/integration/test_your_api.py`

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_feature_endpoint(client: AsyncClient):
    """Test feature creation endpoint"""
    # Arrange
    data = {"name": "Test Feature", "description": "Test"}
    
    # Act
    response = await client.post("/api/v1/your-feature", json=data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["name"] == "Test Feature"
```

### Frontend Component Test

**File**: `frontend/src/components/__tests__/YourComponent.test.tsx`

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { YourComponent } from '../YourComponent';

describe('YourComponent', () => {
  it('renders correctly', () => {
    render(<YourComponent title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

### Run Tests

```bash
# Backend
cd backend
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/integration/ -v

# Frontend
cd frontend
npm test
npm run test:run
```

---

**Last Updated**: 2026-01-20  
**Purpose**: Step-by-step guides for common development tasks  
**Coverage**: All major development workflows
