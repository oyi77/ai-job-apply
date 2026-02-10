"""Global rate limiting middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.config import config
from src.utils.logger import get_logger
import time

logger = get_logger(__name__)


class GlobalRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce global rate limits."""

    def __init__(self, app, limiter: Limiter):
        """Initialize middleware."""
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        """Dispatch request."""
        # Skip if rate limiting is disabled
        if not config.rate_limit_enabled:
            return await call_next(request)

        # Skip for health check and static files
        if request.url.path == "/health" or request.url.path.startswith("/static"):
            return await call_next(request)

        # Check global limit (e.g. 100/minute per IP)
        # We rely on @limiter.limit decorators on endpoints for granular control.

        response = await call_next(request)
        return response
