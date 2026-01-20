# Troubleshooting Guide: Common Issues and Solutions

> **Quick solutions to common problems**

## Table of Contents
- [Database Issues](#database-issues)
- [AI Service Issues](#ai-service-issues)
- [File Upload Issues](#file-upload-issues)
- [CORS Errors](#cors-errors)
- [Build and Deployment Issues](#build-and-deployment-issues)
- [Test Failures](#test-failures)
- [Performance Issues](#performance-issues)
- [Authentication Issues](#authentication-issues)

---

## Database Issues

### Issue: Database Connection Failed

**Symptoms**:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

**Root Cause**: Database file doesn't exist or incorrect path

**Solution**:
```bash
cd backend

# Initialize database
python setup-database.py

# Or run migrations
alembic upgrade head
```

**Prevention**: Always run `setup-database.py` after cloning the repository.

---

### Issue: Migration Conflicts

**Symptoms**:
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Root Cause**: Local migrations out of sync with database

**Solution**:
```bash
cd backend

# Check current version
alembic current

# Check migration history
alembic history

# Downgrade to base
alembic downgrade base

# Upgrade to head
alembic upgrade head
```

**Prevention**: Always pull latest migrations before creating new ones.

---

### Issue: Duplicate Key Error

**Symptoms**:
```
sqlalchemy.exc.IntegrityError: UNIQUE constraint failed: users.email
```

**Root Cause**: Trying to insert duplicate unique values

**Solution**:
```python
# Check if exists before creating
existing = await repository.get_by_email(email)
if existing:
    raise HTTPException(status_code=400, detail="Email already exists")
```

**Prevention**: Always check for existing records before creating.

---

## AI Service Issues

### Issue: Gemini API Key Not Found

**Symptoms**:
```
google.api_core.exceptions.Unauthenticated: Request had invalid authentication credentials
```

**Root Cause**: Missing or invalid `GEMINI_API_KEY` in `.env`

**Solution**:
```bash
# 1. Get API key from https://makersuite.google.com/app/apikey

# 2. Add to .env file
echo "GEMINI_API_KEY=your_actual_key_here" >> backend/.env

# 3. Restart backend
cd backend
python main.py
```

**Prevention**: Always check `.env.example` for required variables.

---

### Issue: AI Service Timeout

**Symptoms**:
```
TimeoutError: Request timed out after 30 seconds
```

**Root Cause**: Large input or slow API response

**Solution**:
```python
# Increase timeout in service
async def optimize_resume(self, resume_text: str, timeout: int = 60):
    try:
        response = await asyncio.wait_for(
            self.model.generate_content_async(prompt),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error("AI request timed out")
        # Return fallback response
```

**Prevention**: Implement fallback responses for AI failures.

---

### Issue: AI Response Parsing Error

**Symptoms**:
```
json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Root Cause**: AI returned non-JSON response

**Solution**:
```python
try:
    result = json.loads(response.text)
except json.JSONDecodeError:
    # Extract text manually
    result = {
        "success": True,
        "content": response.text,
        "parsed": False
    }
```

**Prevention**: Always validate AI responses before parsing.

---

## File Upload Issues

### Issue: File Too Large

**Symptoms**:
```
413 Request Entity Too Large
```

**Root Cause**: File exceeds maximum size limit

**Solution**:
```python
# In backend/src/config.py
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# In endpoint
if file.size > MAX_FILE_SIZE:
    raise HTTPException(
        status_code=413,
        detail=f"File too large. Maximum size: {MAX_FILE_SIZE} bytes"
    )
```

**Prevention**: Validate file size on frontend before upload.

---

### Issue: Invalid File Type

**Symptoms**:
```
400 Bad Request: Invalid file type
```

**Root Cause**: Unsupported file format

**Solution**:
```python
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

file_ext = os.path.splitext(file.filename)[1].lower()
if file_ext not in ALLOWED_EXTENSIONS:
    raise HTTPException(
        status_code=400,
        detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}"
    )
```

**Prevention**: Validate file type on frontend with accept attribute.

---

### Issue: File Not Found After Upload

**Symptoms**:
```
404 Not Found: File not found
```

**Root Cause**: File path incorrect or file not saved

**Solution**:
```python
# Ensure upload directory exists
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)

# Save with full path
file_path = upload_dir / filename
with open(file_path, "wb") as f:
    f.write(await file.read())

# Verify file exists
if not file_path.exists():
    raise HTTPException(status_code=500, detail="File save failed")
```

**Prevention**: Always verify file save operations.

---

## CORS Errors

### Issue: CORS Policy Blocked Request

**Symptoms**:
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Root Cause**: Frontend origin not in allowed CORS origins

**Solution**:
```python
# In backend/src/api/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "https://yourdomain.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Prevention**: Configure CORS before deploying to production.

---

### Issue: Preflight Request Failed

**Symptoms**:
```
OPTIONS request failed with status 403
```

**Root Cause**: Server not handling OPTIONS requests

**Solution**:
```python
# Ensure allow_methods includes OPTIONS
allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
```

**Prevention**: Always allow OPTIONS method for CORS.

---

## Build and Deployment Issues

### Issue: Frontend Build Fails

**Symptoms**:
```
Error: Cannot find module '@/components/Button'
```

**Root Cause**: Missing TypeScript path alias configuration

**Solution**:
```typescript
// In vite.config.ts
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});

// In tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Prevention**: Configure path aliases in both Vite and TypeScript.

---

### Issue: Backend Import Error

**Symptoms**:
```
ModuleNotFoundError: No module named 'src'
```

**Root Cause**: Incorrect Python path or relative imports

**Solution**:
```python
# Use absolute imports (REQUIRED)
from src.core.ai_service import IAIService  # ✅ Correct
from ..core.ai_service import IAIService    # ❌ Wrong

# If running from wrong directory
cd backend
python main.py  # Run from backend directory
```

**Prevention**: Always use absolute imports starting with `src.`

---

### Issue: Docker Container Won't Start

**Symptoms**:
```
Error: Container exited with code 1
```

**Root Cause**: Missing environment variables or build errors

**Solution**:
```bash
# Check logs
docker-compose logs backend

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check environment variables
docker-compose exec backend env | grep GEMINI_API_KEY
```

**Prevention**: Always set required environment variables before starting.

---

## Test Failures

### Issue: Async Test Fails

**Symptoms**:
```
RuntimeError: Event loop is closed
```

**Root Cause**: Missing pytest-asyncio marker

**Solution**:
```python
import pytest

@pytest.mark.asyncio  # Add this decorator
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

**Prevention**: Always mark async tests with `@pytest.mark.asyncio`.

---

### Issue: Database Test Conflicts

**Symptoms**:
```
IntegrityError: UNIQUE constraint failed
```

**Root Cause**: Tests not isolated, sharing database state

**Solution**:
```python
# In conftest.py
@pytest.fixture
async def db_session():
    """Create isolated database session for each test"""
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()  # Rollback after test
```

**Prevention**: Use fixtures with rollback for database tests.

---

### Issue: Mock Not Working

**Symptoms**:
```
AssertionError: Expected mock to be called once, called 0 times
```

**Root Cause**: Mock not properly patched

**Solution**:
```python
from unittest.mock import patch, AsyncMock

@patch('src.services.ai_service.GeminiAIService.optimize_resume')
async def test_with_mock(mock_optimize):
    mock_optimize.return_value = AsyncMock(return_value={"result": "test"})
    
    # Test code
    result = await service.optimize_resume("test")
    
    mock_optimize.assert_called_once()
```

**Prevention**: Patch at the correct import path.

---

## Performance Issues

### Issue: Slow API Response

**Symptoms**: API responses take > 2 seconds

**Root Cause**: N+1 query problem or missing indexes

**Solution**:
```python
# Use eager loading
from sqlalchemy.orm import selectinload

result = await session.execute(
    select(Application)
    .options(selectinload(Application.resume))  # Eager load
    .where(Application.user_id == user_id)
)

# Add database indexes
class Application(Base):
    __table_args__ = (
        Index('idx_application_user_id', 'user_id'),
        Index('idx_application_status', 'status'),
    )
```

**Prevention**: Always use eager loading for relationships.

---

### Issue: High Memory Usage

**Symptoms**: Application using > 1GB RAM

**Root Cause**: Large file processing or memory leaks

**Solution**:
```python
# Stream large files
async def process_large_file(file_path: Path):
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):  # Read in chunks
            await process_chunk(chunk)

# Clear caches periodically
import gc
gc.collect()
```

**Prevention**: Always process large files in chunks.

---

### Issue: Slow Frontend Load

**Symptoms**: Frontend takes > 5 seconds to load

**Root Cause**: Large bundle size or no code splitting

**Solution**:
```typescript
// Use lazy loading
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Applications = lazy(() => import('./pages/Applications'));

// In routes
<Suspense fallback={<Loading />}>
  <Dashboard />
</Suspense>
```

**Prevention**: Always use code splitting for routes.

---

## Authentication Issues

### Issue: Token Expired

**Symptoms**:
```
401 Unauthorized: Token has expired
```

**Root Cause**: JWT token expired

**Solution**:
```typescript
// Implement token refresh
const refreshToken = async () => {
  try {
    const response = await api.post('/auth/refresh');
    localStorage.setItem('token', response.data.access_token);
    return response.data.access_token;
  } catch (error) {
    // Redirect to login
    window.location.href = '/login';
  }
};

// Add interceptor
apiClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const newToken = await refreshToken();
      error.config.headers.Authorization = `Bearer ${newToken}`;
      return apiClient.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

**Prevention**: Implement automatic token refresh.

---

### Issue: Password Reset Not Working

**Symptoms**: Password reset email not received

**Root Cause**: Email service not configured

**Solution**:
```python
# Configure email service in .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Test email service
from src.services.email_service import EmailService

email_service = EmailService()
await email_service.send_password_reset("test@example.com", "reset_token")
```

**Prevention**: Test email service in development.

---

### Issue: Session Not Persisting

**Symptoms**: User logged out after page refresh

**Root Cause**: Token not stored properly

**Solution**:
```typescript
// Store token in localStorage
const login = async (email: string, password: string) => {
  const response = await api.post('/auth/login', { email, password });
  localStorage.setItem('token', response.data.access_token);
  localStorage.setItem('refresh_token', response.data.refresh_token);
};

// Restore session on app load
useEffect(() => {
  const token = localStorage.getItem('token');
  if (token) {
    // Verify token and restore session
    verifyToken(token);
  }
}, []);
```

**Prevention**: Always persist tokens to localStorage.

---

## Quick Diagnostic Commands

### Backend Health Check
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check database connection
cd backend
python -c "from src.database.config import engine; print('DB OK')"

# Check AI service
curl http://localhost:8000/api/v1/ai/health
```

### Frontend Health Check
```bash
# Check if frontend is running
curl http://localhost:5173

# Check build
cd frontend
npm run build

# Check TypeScript
npm run type-check
```

### Database Health Check
```bash
# SQLite
sqlite3 backend/app.db "SELECT COUNT(*) FROM users;"

# PostgreSQL
psql -U postgres -d ai_job_assistant -c "SELECT COUNT(*) FROM users;"
```

### Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

**Last Updated**: 2026-01-20  
**Purpose**: Quick troubleshooting reference for common issues  
**Coverage**: All major issue categories with solutions
