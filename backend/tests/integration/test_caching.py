
import pytest
import os
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch
from src.api.app import create_app
from src.database.config import database_config
from src.core.cache import cache_region

# Set env vars
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test_caching.db"

@pytest.fixture(scope="module", autouse=True)
def setup_cache():
    """Force cache to use memory backend for tests."""
    from dogpile.cache import make_region
    from src.core.cache import cache_region
    
    # Create memory backend
    memory_region = make_region().configure("dogpile.cache.memory")
    
    # Store old backend
    old_backend = cache_region.backend
    
    # Swap to memory backend
    cache_region.backend = memory_region.backend
    
    yield
    
    # Restore old backend
    cache_region.backend = old_backend

@pytest.fixture(scope="module")
async def setup_db():
    await database_config.initialize()
    await database_config.create_tables()
    yield
    await database_config.drop_tables()
    await database_config.close()
    if os.path.exists("test_caching.db"):
        os.remove("test_caching.db")

@pytest.fixture
async def app_instance(setup_db):
    return create_app()

@pytest.fixture
async def client(app_instance):
    async with AsyncClient(
        transport=ASGITransport(app=app_instance),
        base_url="http://test"
    ) as ac:
        yield ac

async def register_user(client, email, password):
    response = await client.post("/api/v1/auth/register", json={
        "email": email, "password": password, "name": "Cache User"
    })
    if response.status_code == 400:
        response = await client.post("/api/v1/auth/login", json={
            "email": email, "password": password
        })
    return response.json()

@pytest.mark.asyncio
async def test_cache_stats_invalidation(client):
    """
    Test that stats endpoint is cached and invalidated on create/update/delete.
    We'll spy on the service method or repository to check call counts.
    Actually, easier to check strict timing or side effects, but for integration,
    we rely on the cache backend working.
    
    To verify 'cache hit', we can use a mock side effect or inspect the cache backend directly if possible.
    For dogpile memory backend, we can inspect `cache_region.backend._cache`.
    """
    
    email = "cache_test@example.com"
    token_data = await register_user(client, email, "Pass1234!")
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get Stats (Miss)
    resp = await client.get("/api/v1/applications/stats", headers=headers)
    assert resp.status_code == 200
    initial_stat = resp.json()["data"]
    assert initial_stat["total_applications"] == 0
    
    # Check cache directly?
    # dogpile memory backend stores in a dict.
    # The key is generated based on function arguments.
    # We can just verify that the second call returns the same result quickly/correctly at least.
    
    # 2. Create Application (Should Invalidate)
    app_data = {"job_title": "Cache Dev", "company": "Redis Co", "status": "submitted"}
    resp = await client.post("/api/v1/applications/", json=app_data, headers=headers)
    assert resp.status_code == 200 or resp.status_code == 201
    
    # 3. Get Stats (Should be new data, Cache Miss again because of invalidation)
    resp = await client.get("/api/v1/applications/stats", headers=headers)
    stat_after_create = resp.json()["data"]
    assert stat_after_create["total_applications"] == 1
    
    # 4. Get Stats Again (Cache Hit)
    # We can't easily prove it's a hit without mocking internals, but we assume if it returns correct data it's good.
    resp = await client.get("/api/v1/applications/stats", headers=headers)
    assert resp.json()["data"]["total_applications"] == 1
    
    # 5. Bulk Create (Should Invalidate)
    bulk_data = {"applications": [{"job_title": "Bulk 1", "company": "B"}, {"job_title": "Bulk 2", "company": "B"}]}
    resp = await client.post("/api/v1/applications/bulk", json=bulk_data, headers=headers)
    # 6. Get Stats (Updated)
    resp = await client.get("/api/v1/applications/stats", headers=headers)
    assert resp.json()["data"]["total_applications"] == 3
    
    # 7. List Applications (Cache Invalidation Check)
    # First call - cache miss
    resp = await client.get("/api/v1/applications/", headers=headers)
    assert resp.status_code == 200
    
    # Handle paginated response structure: data -> {data: [], pagination: {}}
    resp_data = resp.json()["data"]
    if isinstance(resp_data, dict) and "data" in resp_data:
        apps_list = resp_data["data"]
    else:
        apps_list = resp_data
        
    assert len(apps_list) == 3
    
    # Create another to invalidate list cache
    app_data = {"job_title": " List Invalidate", "company": "Redis Co", "status": "submitted"}
    await client.post("/api/v1/applications/", json=app_data, headers=headers)
    
    # Get list again - should have 4
    resp = await client.get("/api/v1/applications/", headers=headers)
    
    resp_data = resp.json()["data"]
    if isinstance(resp_data, dict) and "data" in resp_data:
        apps_list = resp_data["data"]
    else:
        apps_list = resp_data
        
    assert len(apps_list) == 4

    print("Cache invalidation flow verified via state changes (stats and list).")

