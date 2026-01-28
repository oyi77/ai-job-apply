"""Seed default AI provider configurations into the database."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.config import database_config
from src.services.config_service import ConfigService


# Default AI provider configurations
DEFAULT_CONFIGS = [
    # OpenAI
    {
        "name": "OpenAI API Key",
        "key": "openai_api_key",
        "value": "",
        "description": "OpenAI API key for GPT models. Get one at https://platform.openai.com/api-keys",
    },
    {
        "name": "OpenAI Model",
        "key": "openai_model",
        "value": "gpt-4",
        "description": "OpenAI model to use (e.g., gpt-4, gpt-3.5-turbo)",
    },
    {
        "name": "OpenAI Base URL",
        "key": "openai_base_url",
        "value": "",
        "description": "Custom OpenAI API base URL (optional, leave empty for default)",
    },
    # OpenRouter
    {
        "name": "OpenRouter API Key",
        "key": "openrouter_api_key",
        "value": "",
        "description": "OpenRouter API key for accessing multiple AI models. Get one at https://openrouter.ai/keys",
    },
    {
        "name": "OpenRouter Model",
        "key": "openrouter_model",
        "value": "meta-llama/llama-3-8b-instruct",
        "description": "OpenRouter model to use (e.g., meta-llama/llama-3-8b-instruct)",
    },
    {
        "name": "OpenRouter Base URL",
        "key": "openrouter_base_url",
        "value": "https://openrouter.ai/api/v1",
        "description": "OpenRouter API base URL",
    },
    # Cursor
    {
        "name": "Cursor API Key",
        "key": "cursor_api_key",
        "value": "",
        "description": "Cursor AI API key. Get one from your Cursor account settings",
    },
    {
        "name": "Cursor Model",
        "key": "cursor_model",
        "value": "gpt-4o",
        "description": "Cursor AI model to use",
    },
    {
        "name": "Cursor Base URL",
        "key": "cursor_base_url",
        "value": "https://api.cursor.sh/openai/v1",
        "description": "Cursor AI API base URL",
    },
    # Gemini
    {
        "name": "Gemini API Key",
        "key": "gemini_api_key",
        "value": "",
        "description": "Google Gemini API key. Get one at https://makersuite.google.com/app/apikey",
    },
    {
        "name": "Gemini Model",
        "key": "gemini_model",
        "value": "gemini-1.5-flash",
        "description": "Gemini model to use (e.g., gemini-1.5-flash, gemini-pro)",
    },
    # Local AI
    {
        "name": "Local AI Base URL",
        "key": "local_ai_base_url",
        "value": "",
        "description": "Base URL for local AI server (e.g., http://localhost:11434/v1)",
    },
    {
        "name": "Local AI Model",
        "key": "local_ai_model",
        "value": "llama2",
        "description": "Local AI model name",
    },
]


async def seed_configs():
    """Seed default configurations into the database."""
    try:
        print("[*] Seeding default configurations...")

        # Initialize database
        await database_config.initialize()
        await database_config.create_tables()

        # Initialize config service
        config_service = ConfigService()

        # Seed each configuration
        seeded = 0
        skipped = 0

        for config_data in DEFAULT_CONFIGS:
            try:
                # Check if config already exists
                existing = await config_service.get(config_data["key"])
                if existing is None:
                    # Create new config
                    await config_service.set(
                        name=config_data["name"],
                        key=config_data["key"],
                        value=config_data["value"],
                        description=config_data["description"],
                    )
                    seeded += 1
                    print(
                        f"  [OK] Created: {config_data['name']} ({config_data['key']})"
                    )
                else:
                    skipped += 1
                    print(f"  [SKIP] Skipped: {config_data['name']} (already exists)")
            except Exception as e:
                print(f"  [ERROR] Error creating {config_data['key']}: {e}")

        print(f"\n[OK] Seeding complete! Created: {seeded}, Skipped: {skipped}")
        print("\n[INFO] Tip: Update API keys via the API or frontend:")
        print("   PUT /api/v1/config/{key} with {value: 'your-api-key'}")

    except Exception as e:
        print(f"[ERROR] Error seeding configurations: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await database_config.close()


if __name__ == "__main__":
    asyncio.run(seed_configs())
