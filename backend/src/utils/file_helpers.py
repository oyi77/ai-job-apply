"""File handling utilities for the AI Job Application Assistant."""

import os
import mimetypes
from pathlib import Path
from typing import List, Optional, Tuple
import hashlib


def get_file_extension(file_path: str) -> str:
    """
    Get file extension from file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (with dot)
    """
    if not file_path:
        return ""
    
    return Path(file_path).suffix.lower()


def get_file_size(file_path: str) -> Optional[int]:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes, or None if error
    """
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return None
    except (OSError, ValueError):
        return None


def is_valid_file(file_path: str) -> bool:
    """
    Check if file exists and is valid.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is valid, False otherwise
    """
    try:
        return os.path.isfile(file_path) and os.path.exists(file_path)
    except (OSError, ValueError):
        return False


def get_file_mime_type(file_path: str) -> str:
    """
    Get MIME type of file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string
    """
    if not file_path:
        return "application/octet-stream"
    
    # Try to guess MIME type from extension
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if mime_type:
        return mime_type
    
    # Fallback based on file extension
    extension = get_file_extension(file_path)
    mime_map = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".txt": "text/plain",
        ".rtf": "application/rtf",
        ".html": "text/html",
        ".htm": "text/html"
    }
    
    return mime_map.get(extension, "application/octet-stream")


def calculate_file_hash(file_path: str, algorithm: str = "md5") -> Optional[str]:
    """
    Calculate file hash for integrity checking.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (md5, sha1, sha256)
        
    Returns:
        File hash string, or None if error
    """
    try:
        if not is_valid_file(file_path):
            return None
        
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except Exception:
        return None


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def list_files_in_directory(
    directory_path: str,
    pattern: Optional[str] = None,
    recursive: bool = False
) -> List[str]:
    """
    List files in directory with optional filtering.
    
    Args:
        directory_path: Path to the directory
        pattern: Optional glob pattern to filter files
        recursive: Whether to search recursively
        
    Returns:
        List of file paths
    """
    try:
        if not os.path.exists(directory_path):
            return []
        
        if pattern:
            if recursive:
                files = list(Path(directory_path).rglob(pattern))
            else:
                files = list(Path(directory_path).glob(pattern))
        else:
            if recursive:
                files = list(Path(directory_path).rglob("*"))
            else:
                files = list(Path(directory_path).glob("*"))
        
        # Filter to only files (not directories)
        file_paths = [str(f) for f in files if f.is_file()]
        
        return sorted(file_paths)
        
    except Exception:
        return []


def get_file_info(file_path: str) -> dict:
    """
    Get comprehensive file information.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    try:
        if not is_valid_file(file_path):
            return {}
        
        stat = os.stat(file_path)
        path_obj = Path(file_path)
        
        info = {
            "name": path_obj.name,
            "stem": path_obj.stem,
            "suffix": path_obj.suffix,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "mime_type": get_file_mime_type(file_path),
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "accessed": stat.st_atime,
            "hash_md5": calculate_file_hash(file_path, "md5"),
            "hash_sha256": calculate_file_hash(file_path, "sha256")
        }
        
        return info
        
    except Exception:
        return {}


def is_safe_filename(filename: str) -> bool:
    """
    Check if filename is safe for file operations.
    
    Args:
        filename: Filename to check
        
    Returns:
        True if filename is safe, False otherwise
    """
    if not filename:
        return False
    
    # Check for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    
    for char in dangerous_chars:
        if char in filename:
            return False
    
    # Check for reserved names (Windows)
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    if filename.upper() in reserved_names:
        return False
    
    # Check length
    if len(filename) > 255:
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
    
    # Remove or replace dangerous characters
    dangerous_chars = {
        '<': '_', '>': '_', ':': '_', '"': '_', '|': '_', 
        '?': '_', '*': '_', '\\': '_', '/': '_'
    }
    
    sanitized = filename
    for char, replacement in dangerous_chars.items():
        sanitized = sanitized.replace(char, replacement)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed"
    
    return sanitized


def get_unique_filename(directory: str, filename: str) -> str:
    """
    Get unique filename in directory (adds number if duplicate exists).
    
    Args:
        directory: Directory path
        filename: Desired filename
        
    Returns:
        Unique filename
    """
    if not filename:
        filename = "unnamed"
    
    # Ensure directory exists
    ensure_directory_exists(directory)
    
    # Get base name and extension
    path_obj = Path(filename)
    base_name = path_obj.stem
    extension = path_obj.suffix
    
    # Check if file exists
    full_path = Path(directory) / filename
    if not full_path.exists():
        return filename
    
    # Add number suffix
    counter = 1
    while True:
        new_filename = f"{base_name}_{counter}{extension}"
        new_path = Path(directory) / new_filename
        
        if not new_path.exists():
            return new_filename
        
        counter += 1
