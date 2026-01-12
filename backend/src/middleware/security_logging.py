"""
Security logging middleware and utilities.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from src.utils.logger import get_logger

logger = get_logger("security_audit")


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log security-relevant events."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request details for security audit trail (simplified)
        # In production this might go to a SIEM
        client_ip = request.client.host if request.client else "unknown"
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log 401/403 as potential security events
        if response.status_code in [401, 403]:
            logger.warning(
                "Security Event: Unauthorized/Forbidden access attempt",
                extra={
                    "ip": client_ip,
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration": process_time
                }
            )
            
        return response
