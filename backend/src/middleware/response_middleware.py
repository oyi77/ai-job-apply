"""FastAPI middleware for consistent response wrapping."""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Dict, Any, Union
import json
from loguru import logger

class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    """Middleware to wrap all responses in a consistent format."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and wrap response."""
        # Process the request
        response = await call_next(request)
        
        # Skip wrapping for certain paths (health checks, docs, etc.)
        if self._should_skip_wrapping(request.url.path):
            return response
        
        # Skip if response is already JSONResponse or streaming response
        if isinstance(response, JSONResponse) or hasattr(response, 'body_iterator'):
            return response
        
        # Get response content safely
        try:
            # For streaming responses or responses without body attribute
            if not hasattr(response, 'body'):
                return response
            
            content = response.body.decode('utf-8')
            if content:
                data = json.loads(content)
            else:
                data = None
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            # If content is not JSON or can't be accessed, return as-is
            return response
        
        # Wrap the response
        wrapped_response = self._wrap_response(data, response.status_code)
        
        return JSONResponse(
            content=wrapped_response,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    
    def _should_skip_wrapping(self, path: str) -> bool:
        """Check if response wrapping should be skipped for this path."""
        skip_paths = [
            '/docs',
            '/redoc',
            '/openapi.json',
            '/health',
            '/favicon.ico'
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _wrap_response(self, data: Any, status_code: int) -> Dict[str, Any]:
        """Wrap response data in consistent format."""
        if status_code >= 400:
            # Error response
            return {
                "success": False,
                "error": self._get_error_message(status_code),
                "message": "Request failed",
                "data": None
            }
        else:
            # Success response
            return {
                "success": True,
                "data": data,
                "message": "Request completed successfully",
                "error": None
            }
    
    def _get_error_message(self, status_code: int) -> str:
        """Get error message based on status code."""
        error_messages = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            422: "Validation Error",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable"
        }
        
        return error_messages.get(status_code, "Unknown Error")

def add_response_wrapper_middleware(app):
    """Add response wrapper middleware to FastAPI app."""
    app.add_middleware(ResponseWrapperMiddleware)
    logger.info("Response wrapper middleware added")
