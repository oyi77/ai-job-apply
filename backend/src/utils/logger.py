"""Centralized logging configuration for the AI Job Application Assistant."""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


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
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_root_logging(
    level: int = logging.INFO,
    log_dir: str = "logs",
    log_filename: Optional[str] = None
) -> None:
    """
    Setup root logging configuration.
    
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
    
    # Log startup message
    root_logger.info("Logging system initialized")
    root_logger.info(f"Log file: {log_path}")
    root_logger.info(f"Log level: {logging.getLevelName(level)}")


# Default logger instance
default_logger = get_logger("ai_job_apply")
