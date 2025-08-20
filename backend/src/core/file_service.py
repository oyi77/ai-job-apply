"""File management service interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, BinaryIO
from pathlib import Path


class FileService(ABC):
    """Abstract interface for file management services."""
    
    @abstractmethod
    async def save_file(self, file_content: BinaryIO, filename: str, directory: str) -> str:
        """Save a file to the specified directory."""
        pass
    
    @abstractmethod
    async def read_file(self, file_path: str) -> Optional[bytes]:
        """Read file content."""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        pass
    
    @abstractmethod
    async def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information (size, type, etc.)."""
        pass
    
    @abstractmethod
    async def list_files(self, directory: str, pattern: Optional[str] = None) -> List[str]:
        """List files in a directory."""
        pass
    
    @abstractmethod
    async def create_directory(self, directory: str) -> bool:
        """Create a directory if it doesn't exist."""
        pass
    
    @abstractmethod
    async def get_file_size(self, file_path: str) -> Optional[int]:
        """Get file size in bytes."""
        pass
    
    @abstractmethod
    async def is_valid_file_type(self, file_path: str, allowed_types: List[str]) -> bool:
        """Check if file type is allowed."""
        pass
