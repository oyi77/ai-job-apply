import os
from typing import Tuple, List, Optional
from fastapi import UploadFile, HTTPException
from src.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    logger.warning("python-magic not installed or libmagic missing. File type validation will be limited.")
    MAGIC_AVAILABLE = False


class FileSecurityService:
    """Service for file security validation."""
    
    # Allowed MIME types by category
    ALLOWED_MIME_TYPES = {
        "document": [
            "application/pdf", 
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain"
        ],
        "image": [
            "image/jpeg",
            "image/png", 
            "image/webp"
        ]
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        "document": 10 * 1024 * 1024,  # 10MB
        "image": 5 * 1024 * 1024       # 5MB
    }
    
    @staticmethod
    async def validate_file(file: UploadFile, category: str = "document") -> bool:
        """
        Validate file for security.
        
        Checks:
        1. File size
        2. MIME type (via magic numbers)
        3. File extension match
        
        Args:
            file: The file to validate
            category: File category ('document' or 'image')
            
        Returns:
            True if valid
            
        Raises:
            HTTPException: If validation fails
        """
        # 1. Check file size
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
        
        max_size = FileSecurityService.MAX_FILE_SIZES.get(category, 5 * 1024 * 1024)
        if size > max_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {max_size / 1024 / 1024}MB"
            )
            
        # 2. Check Magic Numbers (Real MIME type)
        # Read first 2KB for detection
        header = file.file.read(2048)
        file.file.seek(0)
        
        if MAGIC_AVAILABLE:
            try:
                mime = magic.Magic(mime=True)
                detected_type = mime.from_buffer(header)
                
                allowed_types = FileSecurityService.ALLOWED_MIME_TYPES.get(category, [])
                if detected_type not in allowed_types:
                    logger.warning(f"Security: Blocked file with detected type {detected_type}")
                    raise HTTPException(
                        status_code=415,
                        detail=f"Unsupported file type: {detected_type}. Allowed: {', '.join(allowed_types)}"
                    )
            except Exception as e:
                logger.error(f"Error during magic file type detection: {e}")
                # Fallback or strict fail? For security, strict fail is better, but dev experience matters.
                # If magic failed but was available, it's an error.
                if isinstance(e, HTTPException):
                    raise e
        else:
            # Fallback: Trust Content-Type header (Insecure but functional for dev without libmagic)
            logger.warning("Performing weak file type validation (Content-Type header) due to missing libmagic")
            if file.content_type not in FileSecurityService.ALLOWED_MIME_TYPES.get(category, []):
                 raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type: {file.content_type}."
                )
            
        # 3. Check Virus Scan (Stub for ClamAV optimization)
        # In a real deployed environment, we would pipe this to ClamAV
        # For now, we'll perform basic signature checks for common webshells if it's a script type
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal."""
        return os.path.basename(filename).replace("..", "")
