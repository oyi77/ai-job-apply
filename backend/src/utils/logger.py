"""Centralized logging configuration for the AI Job Application Assistant."""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from logging.handlers import RotatingFileHandler


class NoiseFilter(logging.Filter):
    """Filter to reduce log noise from verbose libraries."""
    
    def filter(self, record):
        # Filter out noisy loggers
        noisy_loggers = [
            'sqlalchemy.engine',
            'sqlalchemy.pool',
            'sqlalchemy.dialects',
            'urllib3',
            'httpx',
            'httpcore',
            'asyncio',
        ]
        
        # Check if logger name starts with any noisy logger
        for noisy in noisy_loggers:
            if record.name.startswith(noisy):
                # Only show WARNING and above for noisy loggers
                return record.levelno >= logging.WARNING
        
        # Allow all other logs
        return True


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        console_output: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter - cleaner format
    formatter = logging.Formatter(
        '%(levelname)-8s | %(name)-30s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler with noise filter
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(NoiseFilter())
        logger.addHandler(console_handler)
    
    # File handler - more detailed format for files
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Use RotatingFileHandler for log rotation (max 10MB per file, keep 5 backups)
        # This prevents logs from filling up the disk while preserving history for debugging
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,  # Keep 5 backup files (app.log.1, app.log.2, etc.)
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Keep all logs in file
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_root_logging(
    level: int = logging.INFO,
    log_dir: str = "logs",
    log_filename: Optional[str] = None
) -> None:
    """
    Setup root logging configuration with noise filtering.
    
    Args:
        level: Logging level
        log_dir: Log directory
        log_filename: Log filename (defaults to app.log)
    """
    if log_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_filename = f"app_{timestamp}.log"
    
    log_path = Path(log_dir) / log_filename
    
    # Setup root logger
    root_logger = get_logger(
        name="ai_job_apply",
        level=level,
        log_file=str(log_path),
        console_output=True
    )
    
    # Set as root logger
    logging.getLogger().handlers = root_logger.handlers
    logging.getLogger().setLevel(level)
    
    # Suppress noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Set query performance to WARNING (only show slow queries)
    logging.getLogger("src.middleware.query_performance").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info("=" * 60)
    root_logger.info("Logging system initialized")
    root_logger.info(f"Log file: {log_path}")
    root_logger.info(f"Console level: {logging.getLevelName(level)}")
    root_logger.info(f"File level: DEBUG (all logs saved to file)")
    root_logger.info("=" * 60)


# Default logger instance
default_logger = get_logger("ai_job_apply")
