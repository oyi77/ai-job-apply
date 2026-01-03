"""Local file service implementation for the AI Job Application Assistant."""

import os
import shutil
from pathlib import Path
from typing import List, Optional, BinaryIO
import mimetypes
import hashlib
from datetime import datetime

from src.core.file_service import FileService
from src.config import config
from loguru import logger
from src.utils.file_helpers import (
    get_file_extension, get_file_size, is_valid_file, 
    sanitize_filename, ensure_directory_exists
)


class LocalFileService(FileService):
    """Local file system implementation of FileService."""
    
    def __init__(self):
        """Initialize the local file service."""
        self.logger = logger.bind(module="LocalFileService")
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            config.UPLOAD_DIR,
            config.RESUME_DIR,
            config.OUTPUT_DIR,
            config.TEMPLATES_DIR,
        ]
        
        for directory in directories:
            ensure_directory_exists(directory)
            self.logger.debug(f"Ensured directory exists: {directory}")
    
    async def save_file(self, file_content: BinaryIO, filename: str, directory: str) -> str:
        """Save a file to the specified directory."""
        try:
            # Sanitize filename
            safe_filename = sanitize_filename(filename)
            
            # Ensure directory exists
            ensure_directory_exists(directory)
            
            # Create full path
            file_path = Path(directory) / safe_filename
            
            # Handle duplicate filenames
            counter = 1
            original_path = file_path
            while file_path.exists():
                stem = original_path.stem
                suffix = original_path.suffix
                file_path = original_path.parent / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Save file
            with open(file_path, 'wb') as f:
                # Reset file pointer to beginning
                file_content.seek(0)
                shutil.copyfileobj(file_content, f)
            
            self.logger.info(f"File saved successfully: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error saving file {filename}: {e}", exc_info=True)
            raise
    
    async def read_file(self, file_path: str) -> Optional[bytes]:
        """Read file content."""
        try:
            if not await self.file_exists(file_path):
                self.logger.warning(f"File not found: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.logger.debug(f"File read successfully: {file_path}")
            return content
            
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}", exc_info=True)
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        try:
            if not await self.file_exists(file_path):
                self.logger.warning(f"Cannot delete, file not found: {file_path}")
                return False
            
            os.remove(file_path)
            self.logger.info(f"File deleted successfully: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}", exc_info=True)
            return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        return is_valid_file(file_path)
    
    async def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information (size, type, etc.)."""
        try:
            if not await self.file_exists(file_path):
                return None
            
            path_obj = Path(file_path)
            stat = path_obj.stat()
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Calculate MD5 hash
            md5_hash = await self._calculate_file_hash(file_path, 'md5')
            
            info = {
                "name": path_obj.name,
                "path": str(path_obj.absolute()),
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "extension": path_obj.suffix.lower(),
                "mime_type": mime_type,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "md5": md5_hash,
            }
            
            self.logger.debug(f"File info retrieved: {file_path}")
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting file info {file_path}: {e}", exc_info=True)
            return None
    
    async def list_files(self, directory: str, pattern: Optional[str] = None) -> List[str]:
        """List files in a directory."""
        try:
            if not os.path.exists(directory):
                self.logger.warning(f"Directory not found: {directory}")
                return []
            
            path_obj = Path(directory)
            
            if pattern:
                files = list(path_obj.glob(pattern))
            else:
                files = [f for f in path_obj.iterdir() if f.is_file()]
            
            # Convert to string paths and sort
            file_paths = [str(f) for f in files]
            file_paths.sort()
            
            self.logger.debug(f"Listed {len(file_paths)} files in {directory}")
            return file_paths
            
        except Exception as e:
            self.logger.error(f"Error listing files in {directory}: {e}", exc_info=True)
            return []
    
    async def create_directory(self, directory: str) -> bool:
        """Create a directory if it doesn't exist."""
        try:
            return ensure_directory_exists(directory)
        except Exception as e:
            self.logger.error(f"Error creating directory {directory}: {e}", exc_info=True)
            return False
    
    async def get_file_size(self, file_path: str) -> Optional[int]:
        """Get file size in bytes."""
        return get_file_size(file_path)
    
    async def is_valid_file_type(self, file_path: str, allowed_types: List[str]) -> bool:
        """Check if file type is allowed."""
        try:
            file_extension = get_file_extension(file_path)
            
            # Normalize allowed types
            normalized_types = []
            for ext in allowed_types:
                if not ext.startswith('.'):
                    ext = f".{ext}"
                normalized_types.append(ext.lower())
            
            return file_extension in normalized_types
            
        except Exception as e:
            self.logger.error(f"Error validating file type {file_path}: {e}", exc_info=True)
            return False
    
    async def _calculate_file_hash(self, file_path: str, algorithm: str = 'md5') -> Optional[str]:
        """Calculate file hash for integrity checking."""
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}", exc_info=True)
            return None
    
    async def copy_file(self, source: str, destination: str) -> bool:
        """Copy a file from source to destination."""
        try:
            if not await self.file_exists(source):
                self.logger.warning(f"Source file not found: {source}")
                return False
            
            # Ensure destination directory exists
            dest_path = Path(destination)
            ensure_directory_exists(str(dest_path.parent))
            
            # Copy file
            shutil.copy2(source, destination)
            
            self.logger.info(f"File copied from {source} to {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error copying file from {source} to {destination}: {e}", exc_info=True)
            return False
    
    async def move_file(self, source: str, destination: str) -> bool:
        """Move a file from source to destination."""
        try:
            if not await self.file_exists(source):
                self.logger.warning(f"Source file not found: {source}")
                return False
            
            # Ensure destination directory exists
            dest_path = Path(destination)
            ensure_directory_exists(str(dest_path.parent))
            
            # Move file
            shutil.move(source, destination)
            
            self.logger.info(f"File moved from {source} to {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error moving file from {source} to {destination}: {e}", exc_info=True)
            return False
    
    async def get_directory_size(self, directory: str) -> int:
        """Get total size of all files in a directory."""
        try:
            if not os.path.exists(directory):
                return 0
            
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)
            
            self.logger.debug(f"Directory {directory} size: {total_size} bytes")
            return total_size
            
        except Exception as e:
            self.logger.error(f"Error calculating directory size {directory}: {e}", exc_info=True)
            return 0
    
    async def cleanup_old_files(self, directory: str, days_old: int = 30) -> int:
        """Clean up files older than specified days."""
        try:
            if not os.path.exists(directory):
                return 0
            
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for file_path in await self.list_files(directory):
                stat = os.stat(file_path)
                if stat.st_mtime < cutoff_time:
                    if await self.delete_file(file_path):
                        deleted_count += 1
            
            self.logger.info(f"Cleaned up {deleted_count} old files from {directory}")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old files in {directory}: {e}", exc_info=True)
            return 0
