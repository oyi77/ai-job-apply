#!/usr/bin/env python3
"""Database backup script for AI Job Application Assistant."""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.config import database_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def backup_database(
    backup_dir: Optional[str] = None,
    filename: Optional[str] = None
) -> str:
    """
    Create a database backup.
    
    Args:
        backup_dir: Directory to save backup (default: ./backups)
        filename: Backup filename (default: auto-generated with timestamp)
        
    Returns:
        Path to backup file
    """
    if backup_dir is None:
        backup_dir = os.path.join(os.path.dirname(__file__), "..", "backups")
    
    os.makedirs(backup_dir, exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.db"
    
    backup_path = os.path.join(backup_dir, filename)
    
    try:
        database_url = database_config.database_url
        
        if "sqlite" in database_url.lower():
            # SQLite backup
            import shutil
            db_path = database_url.replace("sqlite+aiosqlite:///", "")
            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_path)
                logger.info(f"SQLite backup created: {backup_path}")
            else:
                raise FileNotFoundError(f"Database file not found: {db_path}")
        else:
            # PostgreSQL backup using pg_dump
            import subprocess
            from urllib.parse import urlparse
            
            parsed = urlparse(database_url.replace("postgresql+asyncpg://", "postgresql://"))
            
            env = os.environ.copy()
            env["PGPASSWORD"] = parsed.password or ""
            
            cmd = [
                "pg_dump",
                "-h", parsed.hostname or "localhost",
                "-p", str(parsed.port or 5432),
                "-U", parsed.username or "postgres",
                "-d", parsed.path.lstrip("/"),
                "-F", "c",  # Custom format
                "-f", backup_path
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"pg_dump failed: {result.stderr}")
            
            logger.info(f"PostgreSQL backup created: {backup_path}")
        
        # Verify backup file exists and has content
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file was not created: {backup_path}")
        
        file_size = os.path.getsize(backup_path)
        if file_size == 0:
            raise ValueError(f"Backup file is empty: {backup_path}")
        
        logger.info(f"Backup verified: {backup_path} ({file_size} bytes)")
        return backup_path
        
    except Exception as e:
        logger.error(f"Backup failed: {e}", exc_info=True)
        if os.path.exists(backup_path):
            os.remove(backup_path)
        raise


async def cleanup_old_backups(backup_dir: str, keep_days: int = 30) -> int:
    """
    Remove backup files older than specified days.
    
    Args:
        backup_dir: Directory containing backups
        keep_days: Number of days to keep backups
        
    Returns:
        Number of backups removed
    """
    if not os.path.exists(backup_dir):
        return 0
    
    cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
    removed = 0
    
    for filename in os.listdir(backup_dir):
        if filename.startswith("backup_") and filename.endswith(".db"):
            filepath = os.path.join(backup_dir, filename)
            if os.path.getmtime(filepath) < cutoff_time:
                os.remove(filepath)
                removed += 1
                logger.info(f"Removed old backup: {filename}")
    
    return removed


async def main():
    """Main backup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup database")
    parser.add_argument("--dir", help="Backup directory", default=None)
    parser.add_argument("--filename", help="Backup filename", default=None)
    parser.add_argument("--cleanup", action="store_true", help="Clean up old backups")
    parser.add_argument("--keep-days", type=int, default=30, help="Days to keep backups")
    
    args = parser.parse_args()
    
    try:
        backup_path = await backup_database(args.dir, args.filename)
        print(f"✅ Backup created: {backup_path}")
        
        if args.cleanup:
            removed = await cleanup_old_backups(
                args.dir or os.path.join(os.path.dirname(__file__), "..", "backups"),
                args.keep_days
            )
            print(f"✅ Cleaned up {removed} old backup(s)")
        
    except Exception as e:
        print(f"❌ Backup failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

