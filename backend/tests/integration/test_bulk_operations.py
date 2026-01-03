import pytest
import os
from httpx import AsyncClient, ASGITransport
import uuid

# Set env vars BEFORE importing app/config to ensure test DB is used
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test_bulk_ops.db"
os.environ["Rate_Limit_Enabled"] = "False"

from src.api.app import create_app
from src.database.config import database_config

# Fixture to setup DB
@pytest.fixture(scope="module")
async def setup_db():
    # Initialize DB (will use the env var set above)
    await database_config.initialize()
    # Create tables
    await database_config.create_tables()
    yield
    # Cleanup
    await database_config.drop_tables()
    await database_config.close()
    if os.path.exists("test_bulk_ops.db"):
        os.remove("test_bulk_ops.db")

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

async def register_user(client, email, password, name="Test User"):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": name
        }
    )
    if response.status_code == 400 and "already registered" in response.text:
         response = await client.post(
             "/api/v1/auth/login",
             json={"email": email, "password": password}
         )
    return response.json()


@pytest.mark.asyncio
async def test_bulk_operations(client):
    try:
        # Register User
        user_email = f"user_bulk_{uuid.uuid4()}@example.com"
        token_data = await register_user(client, user_email, "Password123!")
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Bulk Create
        apps_to_create = [
            {"job_title": f"Bulk Job {i}", "company": "Bulk Co", "status": "draft", "job_id": f"job_{i}"}
            for i in range(5)
        ]
        
        resp = await client.post("/api/v1/applications/bulk", json={"applications": apps_to_create}, headers=headers)
        assert resp.status_code == 200
        result = resp.json()["data"]
        assert len(result) == 5
        ids = [app["id"] for app in result]
        
        # 2. Bulk Update
        update_data = {
            "ids": ids,
            "updates": {"status": "submitted", "notes": "Bulk updated"}
        }
        resp = await client.put("/api/v1/applications/bulk", json=update_data, headers=headers)
        assert resp.status_code == 200
        
        # Verify update
        resp = await client.get("/api/v1/applications", headers=headers)
        data = resp.json()
        items = data["data"]["data"] if "data" in data["data"] else data["data"]
        
        updated_items = [item for item in items if item["id"] in ids]
        assert len(updated_items) == 5
        for item in updated_items:
            assert item["status"] == "submitted"
            assert item["notes"] == "Bulk updated"
            
        # 3. Bulk Delete
        # Delete first 3
        ids_to_delete = ids[:3]
        delete_req = {"ids": ids_to_delete}
        
        resp = await client.request("DELETE", "/api/v1/applications/bulk", json=delete_req, headers=headers)
        assert resp.status_code == 200
        
        # Verify deletion
        resp = await client.get("/api/v1/applications", headers=headers)
        data = resp.json()
        items = data["data"]["data"] if "data" in data["data"] else data["data"]
        
        remaining_ids = [item["id"] for item in items]
        
        for deleted_id in ids_to_delete:
            assert deleted_id not in remaining_ids
            
        for remaining_id in ids[3:]:
            assert remaining_id in remaining_ids
            
        print("Bulk operations test passed!")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise

