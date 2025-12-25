"""Validation utilities for the AI Job Application Assistant."""

import re
from typing import List, Optional, Any
from urllib.parse import urlparse
from pathlib import Path


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_file_type(file_path: str, allowed_types: List[str]) -> bool:
    """
    Validate file type based on extension.
    
    Args:
        file_path: Path to the file
        allowed_types: List of allowed file extensions (with or without dot)
        
    Returns:
        True if file type is allowed, False otherwise
    """
    if not file_path or not allowed_types:
        return False
    
    file_ext = Path(file_path).suffix.lower()
    
    # Normalize allowed types (ensure they start with dot)
    normalized_types = [
        f".{ext.lower()}" if not ext.startswith('.') else ext.lower()
        for ext in allowed_types
    ]
    
    return file_ext in normalized_types


def validate_file_size(file_path_or_size: Any, max_size_mb: float) -> bool:
    """
    Validate file size.
    
    Args:
        file_path_or_size: Path to the file OR size in bytes
        max_size_mb: Maximum file size in MB
        
    Returns:
        True if file size is within limit, False otherwise
    """
    try:
        if isinstance(file_path_or_size, (int, float)):
            file_size = file_path_or_size
        else:
            file_size = Path(str(file_path_or_size)).stat().st_size
            
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    except (OSError, ValueError):
        return False


def validate_job_keywords(keywords: List[str]) -> bool:
    """
    Validate job search keywords.
    
    Args:
        keywords: List of keywords to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not keywords or not isinstance(keywords, list):
        return False
    
    if len(keywords) == 0:
        return False
    
    # Check each keyword
    for keyword in keywords:
        if not keyword or not isinstance(keyword, str):
            return False
        
        if len(keyword.strip()) == 0:
            return False
        
        if len(keyword) > 100:  # Reasonable limit
            return False
    
    return True


def validate_location(location: str) -> bool:
    """
    Validate job location.
    
    Args:
        location: Location string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not location or not isinstance(location, str):
        return False
    
    if len(location.strip()) == 0:
        return False
    
    if len(location) > 200:  # Reasonable limit
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove or replace unsafe characters
    unsafe_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(unsafe_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed"
    
    return sanitized
