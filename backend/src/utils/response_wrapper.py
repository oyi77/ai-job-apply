"""Response wrapper utility for consistent API responses."""

from typing import TypeVar, Generic, Optional, Any, Dict
from pydantic import BaseModel

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """Consistent API response wrapper."""
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None

def success_response(data: T, message: Optional[str] = None) -> ApiResponse[T]:
    """Create a success response."""
    return ApiResponse(
        success=True,
        data=data,
        message=message or "Operation completed successfully"
    )

def error_response(error: str, message: Optional[str] = None) -> ApiResponse[Any]:
    """Create an error response."""
    return ApiResponse(
        success=False,
        error=error,
        message=message or "Operation failed"
    )

def paginated_response(
    data: list, 
    page: int, 
    limit: int, 
    total: int,
    message: Optional[str] = None
) -> ApiResponse[Dict[str, Any]]:
    """Create a paginated response."""
    pagination_data = {
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }
    
    return ApiResponse(
        success=True,
        data=pagination_data,
        message=message or "Data retrieved successfully"
    )
