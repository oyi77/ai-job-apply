#!/usr/bin/env python3
"""
AI Job Application Assistant
Main entry point for the application
"""

import uvicorn
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.api import app
from src.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def validate_environment():
    """Validate environment setup"""
    project_root = Path(__file__).parent
    
    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("❌ Error: .env file not found!")
        print("Please create a .env file with your Gemini API key.")
        print("You can copy config.env.example to .env and edit it.")
        print("Or run: ./start.sh to set up automatically.")
        sys.exit(1)
    
    # Check if GEMINI_API_KEY is set
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY not found in .env file!")
        print("Please add your Gemini API key to the .env file.")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)

def main():
    """Main function to run the AI Job Application Assistant"""
    try:
        # Validate environment first
        validate_environment()
        
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
        
        # Create necessary directories
        Path("logs").mkdir(exist_ok=True)
        Path("output").mkdir(exist_ok=True)
        Path("resumes").mkdir(exist_ok=True)
        Path("templates").mkdir(exist_ok=True)
        
        logger.info("Starting AI Job Application Assistant...")
        logger.info("Web interface will be available at: http://localhost:8000")
        logger.info("API documentation will be available at: http://localhost:8000/docs")
        
        print("🚀 Starting AI Job Application Assistant...")
        print("📝 Make sure you have Chrome browser installed for web scraping")
        print("🌐 Web interface will be available at: http://localhost:8000")
        print("📚 API docs will be available at: http://localhost:8000/docs")
        print()
        
        # Run the FastAPI application
        uvicorn.run(
            "src.api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 