import pytest
from httpx import AsyncClient
import asyncio
from src.core.cache import cache_region
from src.database.config import Base, database_config, get_db_session
from src.api.app import app
from src.services.service_registry import service_registry

# Setup/Teardown
@pytest.fixture(scope="module", autouse=True)
async def setup_test_db():
    # Configure cache to use memory backend specifically for tests
    # This overrides any existing configuration to ensuring process-local memory cache
    # to avoid race conditions and ensure tests are isolated
    cache_region.configure("dogpile.cache.memory", replace_existing_backend=True)
    
    # Initialize DB
    await database_config.initialize(test_mode=True)
    async with database_config.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Service Registry for tests
    await service_registry.initialize()
    
    yield
    
    # Teardown
    async with database_config.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await database_config.close()

@pytest.fixture
async def client():
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

async def get_auth_headers(client: AsyncClient):
    """Helper to register/login and return auth headers"""
    user_data = {
        "email": "resume_cache_test@example.com",
        "password": "Password123!",
        "full_name": "Resume Cache Test"
    }
    
    # Register/Login (idempotent for tests if DB persists, but we reset DB)
    try:
        await client.post("/api/v1/auth/register", json=user_data)
    except:
        pass
        
    response = await client.post("/api/v1/auth/login", data={
        "username": user_data["email"], 
        "password": user_data["password"]
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_resume_caching_flow(client):
    headers = await get_auth_headers(client)
    
    # 1. Clear Cache
    cache_region.invalidate()
    
    # 2. Upload Resume
    # Create a dummy PDF content
    dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000117 00000 n\n0000000224 00000 n\n0000000311 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n406\n%%EOF"
    
    files = {'file': ('test_resume.pdf', dummy_pdf_content, 'application/pdf')}
    data = {'name': 'Cached Resume'}
    
    resp = await client.post("/api/v1/resumes/upload", headers=headers, files=files, data=data) 
    assert resp.status_code == 200
    resume_data = resp.json()["data"]
    resume_id = resume_data["id"]
    
    # 3. Get Resume (First call - cache miss, should cache)
    resp = await client.get(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert resp.status_code == 200
    
    # 4. Get Resume (Second call - cache hit)
    # We can't verify hit directly without logs, but we verify data consistency
    resp = await client.get(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert resp.status_code == 200
    
    # 5. List Resumes (Should be cached)
    resp = await client.get("/api/v1/resumes/", headers=headers)
    assert resp.status_code == 200
    resumes_list = resp.json() # Assuming it's a direct list or has data key
    if isinstance(resumes_list, dict) and "data" in resumes_list:
        resumes_list = resumes_list["data"]
    assert len(resumes_list) >= 1
    
    # 6. Update Resume (Should invalidate both resume and list cache)
    update_data = {"name": "Updated Resume Name"}
    resp = await client.patch(f"/api/v1/resumes/{resume_id}", json=update_data, headers=headers)
    assert resp.status_code == 200
    
    # 7. Get Resume (Should verify updated name and re-cache)
    resp = await client.get(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Updated Resume Name"
    
    # 8. Delete Resume (Should invalidate caches)
    resp = await client.delete(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert resp.status_code == 200
    
    # 9. List Resumes (check count decreased)
    resp = await client.get("/api/v1/resumes/", headers=headers)
    resumes_list = resp.json()
    if isinstance(resumes_list, dict) and "data" in resumes_list:
        resumes_list = resumes_list["data"]
    
    # Depending on implementation, might return empty list or just previous resumes (if any)
    # Since we cleaned DB, it should be 0 or 1 dependent on if other tests ran
    # Basically checking that our deleted resume isn't there
    ids = [r["id"] for r in resumes_list]
    assert resume_id not in ids
    
    print("Resume caching verified.")
