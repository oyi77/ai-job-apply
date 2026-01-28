"""Seed script to create a mock resume in the database for testing."""

import asyncio
import os
from pathlib import Path
from datetime import datetime, timezone

from src.database.config import database_config, Base
from src.database.models import DBUser, DBResume


async def seed_mock_resume():
    """Create a mock resume in the database for test@example.com."""

    # Initialize database
    await database_config.initialize()

    # Create resumes directory if it doesn't exist
    resumes_dir = Path("resumes")
    resumes_dir.mkdir(parents=True, exist_ok=True)

    # Create a dummy PDF file
    dummy_pdf_path = resumes_dir / "test_resume.pdf"
    with open(dummy_pdf_path, "w") as f:
        f.write("Mock PDF Resume Content\n")
        f.write("This is a dummy resume file for testing.\n")

    print(f"Created dummy resume file: {dummy_pdf_path.resolve()}")

    # Get database session
    async with database_config.get_session() as session:
        async with session.begin():
            # Check if user exists
            from sqlalchemy import select

            user_result = await session.execute(
                select(DBUser).where(DBUser.email == "test@example.com")
            )
            user = user_result.scalar_one_or_none()

            if not user:
                # Create user if doesn't exist
                user = DBUser(
                    email="test@example.com",
                    password_hash="hashed_password_placeholder",
                    name="Test User",
                    is_active=True,
                )
                session.add(user)
                await session.flush()
                print(f"Created user: {user.email}")
            else:
                print(f"User already exists: {user.email}")

            # Create resume record
            resume = DBResume(
                name="Test Resume",
                file_path=str(dummy_pdf_path),
                file_type="pdf",
                content="Mock resume content for testing",
                skills='["Python", "FastAPI", "React", "TypeScript"]',
                experience_years=5,
                education='[{"degree": "Bachelor", "field": "Computer Science"}]',
                certifications='["AWS Certified"]',
                is_default=True,
                user_id=user.id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(resume)
            await session.flush()
            print(f"Created resume: {resume.name} (ID: {resume.id})")

    await database_config.close()
    print("Mock resume seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_mock_resume())
