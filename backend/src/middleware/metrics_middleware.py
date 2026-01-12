"""Metrics middleware for FastAPI to track request performance."""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.services.monitoring_service import DatabaseMonitoringService
from src.utils.logger import get_logger


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics."""
    
    def __init__(self, app: ASGIApp, monitoring_service: DatabaseMonitoringService):
        """Initialize metrics middleware."""
        super().__init__(app)
        self.monitoring_service = monitoring_service
        self.logger = get_logger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()
        
        # Skip metrics for health checks and monitoring endpoints
        if request.url.path in ["/health", "/metrics", "/api/v1/monitoring/health"]:
            return await call_next(request)
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            duration = time.time() - start_time
            
            # Record metrics asynchronously
            try:
                # Request count
                await self.monitoring_service.record_metric(
                    metric_name="api.request.count",
                    metric_value=1.0,
                    tags={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": str(response.status_code)
                    }
                )
                
                # Response time
                await self.monitoring_service.record_metric(
                    metric_name="api.response_time",
                    metric_value=duration * 1000,  # Convert to milliseconds
                    tags={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": str(response.status_code)
                    }
                )
                
                # Error count if status code >= 400
                if response.status_code >= 400:
                    await self.monitoring_service.record_metric(
                        metric_name="api.error.count",
                        metric_value=1.0,
                        tags={
                            "method": request.method,
                            "path": request.url.path,
                            "status_code": str(response.status_code)
                        }
                    )
                
            except Exception as e:
                # Don't fail the request if metrics recording fails
                self.logger.error(f"Error recording metrics: {e}", exc_info=True)
            
            return response
            
        except Exception as e:
            # Record error
            duration = time.time() - start_time
            
            try:
                await self.monitoring_service.record_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=None,  # Can be enhanced to capture full traceback
                    request_path=request.url.path,
                    http_method=request.method,
                    severity="error"
                )
            except Exception as metrics_error:
                self.logger.error(f"Error recording error: {metrics_error}", exc_info=True)
            
            # Re-raise the original exception
            raise
