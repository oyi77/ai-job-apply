#!/usr/bin/env python3
"""Production setup script for the AI Job Application Assistant."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.config import database_config, init_database
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def setup_database():
    """Set up the database for production use."""
    try:
        logger.info("Setting up database for production...")
        
        # Initialize database
        await init_database()
        
        logger.info("Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}", exc_info=True)
        return False


def setup_environment():
    """Set up environment variables for production."""
    try:
        logger.info("Checking environment configuration...")
        
        # Check required environment variables
        required_vars = [
            "GEMINI_API_KEY",  # For AI services
        ]
        
        optional_vars = {
            "DATABASE_URL": "Database connection string (defaults to SQLite)",
            "DB_TYPE": "Database type: sqlite, postgresql, mysql (default: sqlite)",
            "MAX_FILE_SIZE_MB": "Maximum file upload size in MB (default: 10)",
            "UPLOAD_DIRECTORY": "Directory for file uploads (default: uploads)",
            "LOG_LEVEL": "Logging level (default: INFO)",
            "DEBUG": "Debug mode (default: False)"
        }
        
        missing_required = []
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)
        
        if missing_required:
            logger.warning(f"Missing required environment variables: {', '.join(missing_required)}")
            logger.info("The application will run with reduced functionality (mock AI responses)")
        
        # Log optional configuration
        logger.info("Optional configuration:")
        for var, description in optional_vars.items():
            value = os.getenv(var, "Not set")
            logger.info(f"  {var}: {value} - {description}")
        
        # Create necessary directories
        upload_dir = Path(os.getenv("UPLOAD_DIRECTORY", "uploads"))
        upload_dir.mkdir(exist_ok=True)
        logger.info(f"Upload directory created: {upload_dir}")
        
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        logger.info(f"Logs directory created: {logs_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"Environment setup failed: {e}", exc_info=True)
        return False


def install_dependencies():
    """Check and install Python dependencies."""
    try:
        import subprocess
        import sys
        
        logger.info("Checking Python dependencies...")
        
        # Check if requirements.txt exists
        requirements_file = Path("requirements.txt")
        if not requirements_file.exists():
            logger.error("requirements.txt not found!")
            return False
        
        # Install dependencies
        logger.info("Installing dependencies from requirements.txt...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Dependencies installed successfully!")
            return True
        else:
            logger.error(f"Failed to install dependencies: {result.stderr}")
            return False
        
    except Exception as e:
        logger.error(f"Dependency installation failed: {e}", exc_info=True)
        return False


def create_env_template():
    """Create a .env template file."""
    try:
        env_template = """# AI Job Application Assistant - Environment Configuration

# AI Service Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
# DATABASE_URL=sqlite:///ai_job_assistant.db
# DB_TYPE=sqlite
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=ai_job_assistant
# DB_USER=postgres
# DB_PASSWORD=your_password

# File Upload Configuration
MAX_FILE_SIZE_MB=10
UPLOAD_DIRECTORY=uploads

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO

# Server Configuration (for production deployment)
HOST=0.0.0.0
PORT=8000
"""
        
        env_file = Path(".env")
        if not env_file.exists():
            with open(env_file, "w") as f:
                f.write(env_template)
            logger.info("Created .env template file")
            logger.info("Please edit .env file with your configuration")
        else:
            logger.info(".env file already exists")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create .env template: {e}", exc_info=True)
        return False


async def main():
    """Main setup function."""
    logger.info("🚀 AI Job Application Assistant - Production Setup")
    logger.info("=" * 50)
    
    success = True
    
    # Step 1: Create environment template
    logger.info("Step 1: Creating environment template...")
    if not create_env_template():
        success = False
    
    # Step 2: Install dependencies
    logger.info("\nStep 2: Installing dependencies...")
    if not install_dependencies():
        success = False
    
    # Step 3: Setup environment
    logger.info("\nStep 3: Setting up environment...")
    if not setup_environment():
        success = False
    
    # Step 4: Setup database
    logger.info("\nStep 4: Setting up database...")
    if not await setup_database():
        success = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    if success:
        logger.info("✅ Production setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Edit .env file with your configuration")
        logger.info("2. Set your GEMINI_API_KEY for AI features")
        logger.info("3. Run: python main.py")
        logger.info("4. Access the application at http://localhost:8000")
    else:
        logger.error("❌ Production setup failed!")
        logger.error("Please check the logs above and fix any issues")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
