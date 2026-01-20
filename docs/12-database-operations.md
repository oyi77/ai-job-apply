# Database Operations: Query Patterns and Best Practices

> **Common database patterns, queries, and operations**

## Repository Pattern Overview

All database operations use the repository pattern for clean separation of concerns.

**Pattern Structure**:
```
Interface (core/) → Implementation (database/repositories/) → Usage (services/)
```

## Common Query Patterns

### Basic CRUD Operations

#### Create
```python
from src.database.models import Application
from src.models.application import ApplicationCreate

async def create_application(data: ApplicationCreate, user_id: str) -> Application:
    """Create a new application"""
    application = Application(
        **data.model_dump(),
        user_id=user_id
    )
    session.add(application)
    await session.commit()
    await session.refresh(application)
    return application
```

#### Read (Single)
```python
from sqlalchemy import select

async def get_by_id(application_id: str) -> Optional[Application]:
    """Get application by ID"""
    result = await session.execute(
        select(Application).where(Application.id == application_id)
    )
    return result.scalar_one_or_none()
```

#### Read (List with Pagination)
```python
async def list_applications(
    user_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[Application]:
    """List applications with pagination"""
    result = await session.execute(
        select(Application)
        .where(Application.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(Application.created_at.desc())
    )
    return list(result.scalars().all())
```

#### Update
```python
async def update_application(
    application_id: str,
    data: ApplicationUpdate
) -> Optional[Application]:
    """Update application"""
    application = await get_by_id(application_id)
    if not application:
        return None
    
    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(application, key, value)
    
    await session.commit()
    await session.refresh(application)
    return application
```

#### Delete
```python
async def delete_application(application_id: str) -> bool:
    """Delete application"""
    application = await get_by_id(application_id)
    if not application:
        return False
    
    await session.delete(application)
    await session.commit()
    return True
```

---

### Filtering and Search

#### Simple Filter
```python
async def get_by_status(user_id: str, status: str) -> List[Application]:
    """Get applications by status"""
    result = await session.execute(
        select(Application)
        .where(
            Application.user_id == user_id,
            Application.status == status
        )
    )
    return list(result.scalars().all())
```

#### Multiple Filters
```python
async def search_applications(
    user_id: str,
    status: Optional[str] = None,
    company: Optional[str] = None,
    from_date: Optional[date] = None
) -> List[Application]:
    """Search with multiple filters"""
    query = select(Application).where(Application.user_id == user_id)
    
    if status:
        query = query.where(Application.status == status)
    
    if company:
        query = query.where(Application.company_name.ilike(f"%{company}%"))
    
    if from_date:
        query = query.where(Application.applied_date >= from_date)
    
    result = await session.execute(query)
    return list(result.scalars().all())
```

#### Text Search
```python
async def full_text_search(user_id: str, search_term: str) -> List[Application]:
    """Search across multiple text fields"""
    result = await session.execute(
        select(Application)
        .where(
            Application.user_id == user_id,
            or_(
                Application.company_name.ilike(f"%{search_term}%"),
                Application.position_title.ilike(f"%{search_term}%"),
                Application.notes.ilike(f"%{search_term}%")
            )
        )
    )
    return list(result.scalars().all())
```

---

### Relationships and Joins

#### Eager Loading (Prevent N+1)
```python
from sqlalchemy.orm import selectinload

async def get_with_resume(application_id: str) -> Optional[Application]:
    """Get application with resume (eager loading)"""
    result = await session.execute(
        select(Application)
        .options(selectinload(Application.resume))
        .where(Application.id == application_id)
    )
    return result.scalar_one_or_none()
```

#### Multiple Relationships
```python
async def get_with_all_relations(application_id: str) -> Optional[Application]:
    """Get application with all related data"""
    result = await session.execute(
        select(Application)
        .options(
            selectinload(Application.resume),
            selectinload(Application.cover_letter),
            selectinload(Application.user)
        )
        .where(Application.id == application_id)
    )
    return result.scalar_one_or_none()
```

#### Join Query
```python
async def get_applications_with_resume_title(user_id: str) -> List[tuple]:
    """Get applications with resume titles"""
    result = await session.execute(
        select(Application, Resume.title)
        .join(Resume, Application.resume_id == Resume.id)
        .where(Application.user_id == user_id)
    )
    return list(result.all())
```

---

### Aggregations and Statistics

#### Count
```python
from sqlalchemy import func

async def count_by_status(user_id: str) -> Dict[str, int]:
    """Count applications by status"""
    result = await session.execute(
        select(
            Application.status,
            func.count(Application.id).label('count')
        )
        .where(Application.user_id == user_id)
        .group_by(Application.status)
    )
    return {row.status: row.count for row in result.all()}
```

#### Average and Sum
```python
async def get_statistics(user_id: str) -> Dict[str, Any]:
    """Get application statistics"""
    result = await session.execute(
        select(
            func.count(Application.id).label('total'),
            func.avg(
                func.julianday(Application.updated_at) - 
                func.julianday(Application.created_at)
            ).label('avg_days')
        )
        .where(Application.user_id == user_id)
    )
    row = result.one()
    return {
        'total_applications': row.total,
        'average_days_active': round(row.avg_days, 2) if row.avg_days else 0
    }
```

---

### Transaction Management

#### Simple Transaction
```python
async def create_application_with_resume(
    app_data: ApplicationCreate,
    resume_data: ResumeCreate,
    user_id: str
) -> Application:
    """Create application and resume in single transaction"""
    async with session.begin():
        # Create resume
        resume = Resume(**resume_data.model_dump(), user_id=user_id)
        session.add(resume)
        await session.flush()  # Get resume.id
        
        # Create application
        application = Application(
            **app_data.model_dump(),
            user_id=user_id,
            resume_id=resume.id
        )
        session.add(application)
        
        await session.commit()
        await session.refresh(application)
        return application
```

#### Rollback on Error
```python
async def update_with_validation(
    application_id: str,
    data: ApplicationUpdate
) -> Application:
    """Update with automatic rollback on error"""
    try:
        async with session.begin():
            application = await get_by_id(application_id)
            if not application:
                raise ValueError("Application not found")
            
            # Validate business rules
            if data.status == "submitted" and not application.resume_id:
                raise ValueError("Cannot submit without resume")
            
            # Update
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(application, key, value)
            
            await session.commit()
            return application
    except Exception as e:
        await session.rollback()
        raise
```

---

### Bulk Operations

#### Bulk Insert
```python
async def bulk_create_applications(
    applications_data: List[ApplicationCreate],
    user_id: str
) -> List[Application]:
    """Create multiple applications efficiently"""
    applications = [
        Application(**data.model_dump(), user_id=user_id)
        for data in applications_data
    ]
    session.add_all(applications)
    await session.commit()
    
    # Refresh all
    for app in applications:
        await session.refresh(app)
    
    return applications
```

#### Bulk Update
```python
from sqlalchemy import update

async def bulk_update_status(
    application_ids: List[str],
    new_status: str
) -> int:
    """Update status for multiple applications"""
    result = await session.execute(
        update(Application)
        .where(Application.id.in_(application_ids))
        .values(status=new_status, updated_at=datetime.utcnow())
    )
    await session.commit()
    return result.rowcount
```

---

## Migration Workflow

### Creating Migrations

```bash
# 1. Modify models in src/database/models.py

# 2. Generate migration
cd backend
alembic revision --autogenerate -m "Add new field to applications"

# 3. Review generated migration
# Edit alembic/versions/xxxx_add_new_field.py if needed

# 4. Apply migration
alembic upgrade head
```

### Migration Best Practices

```python
# Good: Add column with default
def upgrade():
    op.add_column('applications',
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium')
    )

# Good: Make nullable first, then add constraint
def upgrade():
    # Step 1: Add as nullable
    op.add_column('applications',
        sa.Column('email', sa.String(255), nullable=True)
    )
    # Step 2: Populate data
    op.execute("UPDATE applications SET email = 'default@example.com' WHERE email IS NULL")
    # Step 3: Make not nullable
    op.alter_column('applications', 'email', nullable=False)
```

---

## Indexing Strategy

### Index Definition
```python
from sqlalchemy import Index

class Application(Base):
    __tablename__ = "applications"
    
    # ... columns ...
    
    __table_args__ = (
        # Single column indexes
        Index('idx_application_user_id', 'user_id'),
        Index('idx_application_status', 'status'),
        Index('idx_application_created_at', 'created_at'),
        
        # Composite indexes
        Index('idx_application_user_status', 'user_id', 'status'),
        Index('idx_application_user_date', 'user_id', 'created_at'),
    )
```

### When to Add Indexes
- ✅ Foreign keys (user_id, resume_id)
- ✅ Frequently filtered columns (status, created_at)
- ✅ Columns used in ORDER BY
- ✅ Columns used in JOIN conditions
- ❌ Small tables (< 1000 rows)
- ❌ Columns with low cardinality (true/false)
- ❌ Frequently updated columns

---

## Performance Optimization

### Use select() Instead of Query
```python
# ✅ Good: Modern async approach
result = await session.execute(
    select(Application).where(Application.user_id == user_id)
)

# ❌ Avoid: Legacy sync approach
applications = session.query(Application).filter_by(user_id=user_id).all()
```

### Limit Result Sets
```python
# ✅ Good: Always use pagination
result = await session.execute(
    select(Application)
    .limit(100)
    .offset(skip)
)

# ❌ Avoid: Loading all records
result = await session.execute(select(Application))  # Could be thousands!
```

### Use Eager Loading
```python
# ✅ Good: One query with join
result = await session.execute(
    select(Application)
    .options(selectinload(Application.resume))
)

# ❌ Avoid: N+1 queries
applications = await session.execute(select(Application))
for app in applications.scalars():
    resume = await session.execute(
        select(Resume).where(Resume.id == app.resume_id)
    )  # Separate query for each!
```

---

## Testing Database Operations

### Test with Fixtures
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def db_session():
    """Provide isolated database session for tests"""
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()

@pytest.mark.asyncio
async def test_create_application(db_session: AsyncSession):
    """Test application creation"""
    repo = ApplicationRepository(db_session)
    data = ApplicationCreate(company_name="Test", position_title="Dev")
    
    result = await repo.create(data, user_id="test_user")
    
    assert result.id is not None
    assert result.company_name == "Test"
```

---

**Last Updated**: 2026-01-20  
**Database**: PostgreSQL (production), SQLite (development)  
**ORM**: SQLAlchemy 2.0 async
