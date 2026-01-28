#!/usr/bin/env python
"""Debug script to test imports."""

import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

try:
    from src.api.v1.auth import router

    print("✓ Successfully imported src.api.v1.auth")
    print(f"  Router: {router}")
except Exception as e:
    print(f"✗ Failed to import src.api.v1.auth")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
