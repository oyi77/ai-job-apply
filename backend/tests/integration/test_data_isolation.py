import pytest
import os
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import uuid

# Set env vars BEFORE importing app/config to ensure test DB is used
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test_isolation.db"
os.environ["Rate_Limit_Enabled"] = "False"  # Disable rate limit for tests

from src.api.app import create_app
from src.database.config import database_config
from src.database.models import Base

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
    if os.path.exists("test_isolation.db"):
        os.remove("test_isolation.db")

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

async def register_user(client, email, password, name):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": name
        }
    )
    if response.status_code == 400 and "already registered" in response.text:
        # Login instead
        response = await client.post(
             "/api/v1/auth/login",
             json={"email": email, "password": password}
        )
    assert response.status_code in [201, 200]
    return response.json()

@pytest.mark.asyncio
async def test_user_data_isolation(client):
    try:
        # 1. Register User 1
        user1_email = f"user1_{uuid.uuid4()}@example.com"
        token1_data = await register_user(client, user1_email, "Password123!", "User One")
        if not isinstance(token1_data, dict):
             raise ValueError(f"token1_data is not dict: {type(token1_data)} - {token1_data}")
        
        token1 = token1_data["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # 2. Register User 2
        user2_email = f"user2_{uuid.uuid4()}@example.com"
        token2_data = await register_user(client, user2_email, "Password123!", "User Two")
        if not isinstance(token2_data, dict):
             raise ValueError(f"token2_data is not dict: {type(token2_data)} - {token2_data}")
        token2 = token2_data["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # 3. User 1 creates a Application
        app_data = {
            "job_title": "Backend Dev",
            "company": "Google",
            "status": "submitted",
            "job_id": "job_123"
        }
        resp = await client.post(
            "/api/v1/applications/",
            json=app_data,
            headers=headers1
        )
        
        if resp.status_code not in [200, 201]:
             raise ValueError(f"Create App failed: {resp.status_code} - {resp.text}")
             
        response_json = resp.json()
        
        if not isinstance(response_json, dict):
            raise ValueError(f"Response is not a dict: {response_json}")
        
        # Check if "data" key exists
        if "data" not in response_json:
            # Maybe it returned the application directly?
            if "id" in response_json:
                 # print("WARNING: Response seems to be the application object directly, not wrapped.")
                 app1_id = response_json["id"]
            else:
                 raise ValueError(f"Response missing 'data' and 'id': {response_json}")
        else:
            data_field = response_json["data"]
            
            if not isinstance(data_field, dict):
                 raise TypeError(f"response_json['data'] is type {type(data_field)}, content: {data_field}")
            app1_id = data_field["id"]

        # 4. User 1 should see it
        resp = await client.get("/api/v1/applications", headers=headers1)
        if resp.status_code != 200:
             raise ValueError(f"Get App U1 failed: {resp.status_code} - {resp.text}")
        
        items_resp = resp.json()
        
        if isinstance(items_resp, dict) and "data" in items_resp:
             if isinstance(items_resp["data"], dict) and "data" in items_resp["data"]:
                 items = items_resp["data"]["data"] # Paginated
             elif isinstance(items_resp["data"], list):
                 items = items_resp["data"] # Non-paginated
             else:
                 raise ValueError(f"Unexpected data field format: {items_resp['data']}")
        else:
             raise ValueError(f"Unexpected items response format: {items_resp}")
             
        if not any(item["id"] == app1_id for item in items):
             raise ValueError(f"User 1 cannot see their own app {app1_id}. Items: {items}")

        # 5. User 2 should NOT see it
        resp = await client.get("/api/v1/applications", headers=headers2)
        if resp.status_code != 200:
             raise ValueError(f"Get App U2 failed: {resp.status_code} - {resp.text}")
             
        items_resp = resp.json()
        if isinstance(items_resp, dict) and "data" in items_resp:
             if isinstance(items_resp["data"], dict) and "data" in items_resp["data"]:
                 items = items_resp["data"]["data"] # Paginated
             elif isinstance(items_resp["data"], list):
                 items = items_resp["data"] # Non-paginated
             else:
                 items = [] 
        else:
             items = []
        
        if any(item["id"] == app1_id for item in items):
             raise ValueError(f"User 2 CAN see User 1's app {app1_id}! Violation!")

        # 6. User 2 tries to access User 1's application directly
        resp = await client.get(f"/api/v1/applications/{app1_id}", headers=headers2)
        if resp.status_code not in [404, 403]:
             raise ValueError(f"User 2 could access User 1's app directly! Status: {resp.status_code}")
        
    except Exception as e:
        # Re-raise with context
        raise Exception(f"TEST FAILED: {str(e)}") from e
