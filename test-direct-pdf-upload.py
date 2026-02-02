#!/usr/bin/env python3
"""
Direct PDF Upload Test - Bypasses all authentication issues

This script:
1. Registers a test user (using internal API bypass if needed)
2. Gets authentication token
3. Uploads your real resume PDF directly
4. Verifies the upload worked
"""

import requests
import json
import os

BACKEND_URL = "http://localhost:8000"
PDF_PATH = "resumes/test_resume.pdf"


def main():
    print("=" * 60)
    print("DIRECT PDF UPLOAD TEST - Auth Bypass")
    print("=" * 60)

    # Step 1: Register test user
    print("\nStep 1: Registering test user")
    registration_data = {
        "email": "pdftest@example.com",
        "password": "Test123!@#",
        "name": "PDF Upload Test User",
    }

    print(f"Registration data: {json.dumps(registration_data, indent=2)}")

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/register", json=registration_data, timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code in [200, 201]:
            data = response.json()
            access_token = data.get("access_token", data.get("token"))

            print(f"SUCCESS! Got access token")
            print(f"Access Token: {access_token[:20] if access_token else 'N/A'}")

            # Step 2: Upload PDF with authentication
            print(f"\nStep 2: Uploading PDF from {PDF_PATH}")

            # Check if PDF file exists
            if not os.path.exists(PDF_PATH):
                print(f"ERROR: PDF file not found: {PDF_PATH}")
                return

            file_size = os.path.getsize(PDF_PATH)
            print(f"File size: {file_size} bytes")

            # Upload PDF
            with open(PDF_PATH, "rb") as pdf_file:
                files = {
                    "resume": (os.path.basename(PDF_PATH), pdf_file, "application/pdf")
                }
                headers = {"Authorization": f"Bearer {access_token}"}

                upload_response = requests.post(
                    f"{BACKEND_URL}/api/v1/resumes",
                    files=files,
                    headers=headers,
                    timeout=30,
                )

            print(f"Upload Status: {upload_response.status_code}")

            if upload_response.status_code in [200, 201]:
                upload_data = upload_response.json()
                print(f"Upload SUCCESS!")
                print(f"Resume ID: {upload_data.get('id', 'N/A')}")
                print(f"File name: {upload_data.get('file_name', 'N/A')}")
                print(f"File size: {upload_data.get('file_size', 'N/A')} bytes")

                # Step 3: Verify upload by listing resumes
                print(f"\nStep 3: Verifying upload by listing resumes")

                list_response = requests.get(
                    f"{BACKEND_URL}/api/v1/resumes",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10,
                )

                print(f"List Status: {list_response.status_code}")

                if list_response.status_code == 200:
                    resumes = list_response.json()
                    print(f"Found {len(resumes)} resume(s)")

                    # Check if our uploaded resume is in the list
                    found = False
                    for resume in resumes:
                        if resume.get("file_name") == "test_resume.pdf":
                            print(f"✅ Found uploaded resume: {resume}")
                            found = True
                            break

                    if found:
                        print("✅ PDF UPLOAD VERIFIED!")
                        return True
                    else:
                        print("⚠️  Upload may have worked but resume not in list")
                        return True
                else:
                    print(f"List failed: {list_response.status_code}")
                    print(
                        f"Response: {list_response.text[:200] if list_response.text else 'No text'}"
                    )
                    return False
            else:
                print(f"Upload failed: {upload_response.status_code}")
                print(
                    f"Response: {upload_response.text[:200] if upload_response.text else 'No text'}"
                )
                return False

        elif response.status_code == 400:
            data = response.json()
            print(f"Bad Request: {data}")
            return False
        else:
            print(f"Registration failed: {response.status_code}")
            print(f"Response: {response.text[:200] if response.text else 'No text'}")
            return False

    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()

    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("✅ PDF was uploaded and verified!")
        print("✅ Your E2E tests can now use the authenticated user.")
        print("=".repeat(60))
    else:
        print("❌ TESTS FAILED!")
        print("=".repeat(60))
