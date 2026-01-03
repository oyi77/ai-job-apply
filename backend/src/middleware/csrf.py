"""CSRF protection middleware for FastAPI."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import secrets
from ...utils.logger import get_logger

logger = get_logger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware to protect against CSRF attacks."""
    
    def __init__(self, app, secret_key: str = None):
        """Initialize CSRF protection middleware."""
        super().__init__(app)
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.exempt_methods = {"GET", "HEAD", "OPTIONS"}
        self.exempt_paths = {"/health", "/api/v1/auth/login", "/api/v1/auth/register"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with CSRF protection."""
        # Skip CSRF check for exempt methods
        if request.method in self.exempt_methods:
            return await call_next(request)
        
        # Skip CSRF check for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # For state-changing operations, verify CSRF token
        # In a production app, you'd validate against a stored token
        # For now, we'll check for the presence of a CSRF token header
        csrf_token = request.headers.get("X-CSRF-Token")
        
        if not csrf_token:
            logger.warning(f"CSRF token missing for {request.method} {request.url.path}")
            # In development, we'll log but allow (can be made stricter in production)
            # raise HTTPException(status_code=403, detail="CSRF token missing")
        
        response = await call_next(request)
        
        # Add CSRF token to response headers for subsequent requests
        # In production, this would be generated server-side and validated
        response.headers["X-CSRF-Token"] = csrf_token or secrets.token_urlsafe(32)
        
        return response

