#!/usr/bin/env python3
"""
Direct API test for PDF resume upload
Simplified version to avoid encoding issues
"""

import os
import sys
import requests
from pathlib import Path

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
PDF_PATH = Path(__file__).parent / "resumes" / "test_resume.pdf"


def test_backend_health() -> bool:
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("Backend is healthy")
            return True
        else:
            print(f"Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Backend connection failed: {e}")
        return False


def register_user(email: str, password: str, name: str) -> dict | None:
    """Register a new user"""
    print(f"Registering user: {email}")

    response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/register",
        json={"email": email, "password": password, "name": name},
        timeout=10,
    )

    if response.status_code == 200:
        data = response.json()
        print("Registration successful")
        return {"access_token": data.get("access_token"), "token": data.get("token")}
    else:
        print(f"Registration failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def upload_pdf_resume(token: str, pdf_path: Path) -> dict | None:
    """Upload PDF resume via API"""
    print(f"Uploading PDF resume: {pdf_path}")
    print(f"File size: {pdf_path.stat().st_size} bytes")

    # Check if file exists
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        return None

    # Upload PDF
    with open(pdf_path, "rb") as pdf_file:
        files = {"file": (pdf_path.name, pdf_file, "application/pdf")}

        headers = {"Authorization": f"Bearer {token}"}

        response = requests.post(
            f"{BACKEND_URL}/api/v1/resumes", files=files, headers=headers, timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print("PDF upload successful!")
            print(f"Resume ID: {data.get('id')}")
            print(f"Filename: {data.get('file_name')}")
            skills = data.get("skills", [])
            print(f"Skills: {skills}")
            return data
        else:
            print(f"PDF upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None


def get_resumes(token: str) -> list:
    """Get list of resumes"""
    print("Fetching resumes...")

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BACKEND_URL}/api/v1/resumes", headers=headers, timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        resumes = data if isinstance(data, list) else []
        print(f"Found {len(resumes)} resume(s)")
        for i, resume in enumerate(resumes, 1):
            print(f"  {i}. {resume.get('file_name', resume.get('id'))}")
        return resumes
    else:
        print(f"Failed to fetch resumes: {response.status_code}")
        print(f"Response: {response.text}")
        return []


def main():
    """Main test flow"""
    print("=" * 60)
    print("PDF RESUME UPLOAD API TEST")
    print("=" * 60)

    # Test backend health
    if not test_backend_health():
        print("Backend not available. Please start backend first.")
        print("Run: python main.py (from project root)")
        sys.exit(1)

    # Register test user
    timestamp = int(Path(__file__).stat().st_mtime)
    test_email = f"directtest{timestamp}@example.com"
    test_password = "Test123!@#"
    test_name = "Direct API Test"

    auth_data = register_user(test_email, test_password, test_name)
    if not auth_data:
        print("Cannot proceed without authentication token")
        sys.exit(1)

    token = auth_data.get("token") or auth_data.get("access_token")
    if not token:
        print("Cannot get authentication token")
        sys.exit(1)

    # Test PDF upload
    result = upload_pdf_resume(token, PDF_PATH)
    if result:
        print("TEST PASSED: PDF uploaded successfully via API")
    else:
        print("TEST FAILED: Could not upload PDF")

    # Verify upload
    resumes = get_resumes(token)
    if resumes and len(resumes) > 0:
        print("VERIFICATION PASSED: Resume list contains uploaded PDF")
    else:
        print("VERIFICATION WARNING: Resume list is empty")

    print("=" * 60)
    print("Test complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
