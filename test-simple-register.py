#!/usr/bin/env python3
"""
Simplified registration test without name requirement
"""

import requests

BACKEND_URL = "http://localhost:8000"


def main():
    """Test registration without name field."""
    print("=" * 60)
    print("SIMPLIFIED REGISTRATION TEST")
    print("=" * 60)

    # Test 1: Registration WITHOUT name
    print("\nTest 1: Registration WITHOUT name field")
    registration_data = {"email": "simpletest@example.com", "password": "Test123!@#"}

    print(f"Sending: {registration_data}")

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/register", json=registration_data, timeout=10
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            print(f"✅ SUCCESS!")
            print(f"Access Token: {data.get('access_token', 'N/A')}")
            print(f"Refresh Token: {data.get('refresh_token', 'N/A')}")
        else:
            print(f"❌ FAILED!")

    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()

    # Test 2: Check backend health
    print("\nTest 2: Check backend health")
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"Health Status: {health.status_code}")
        print(f"Health Response: {health.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")


if __name__ == "__main__":
    main()
