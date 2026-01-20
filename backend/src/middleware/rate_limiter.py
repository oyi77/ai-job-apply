"""Rate limiting middleware using slowapi.

This module provides configurable rate limiting for API endpoints
with support for different limits per endpoint type.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from src.config import config


def get_remote_address_from_request(request: Request) -> str:
    """Get client IP address from request, handling X-Forwarded-For for proxies."""
    # Check for X-Forwarded-For header (set by proxies/load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain (original client)
        return forwarded_for.split(",")[0].strip()
    return get_remote_address(request)


# Create limiter instances for different use cases
_auth_limiter = Limiter(key_func=get_remote_address_from_request)
_general_limiter = Limiter(key_func=get_remote_address_from_request)
_strict_limiter = Limiter(key_func=get_remote_address_from_request)


def get_auth_limiter(request: Request) -> Limiter:
    """Get the auth-specific rate limiter.

    Returns a rate limiter configured for authentication endpoints
    (login, register, password reset) with stricter limits.
    """
    return _auth_limiter


def get_general_limiter(request: Request) -> Limiter:
    """Get the general-purpose rate limiter.

    Returns a rate limiter configured for general API endpoints
    with moderate limits.
    """
    return _general_limiter


def get_strict_limiter(request: Request) -> Limiter:
    """Get the strict rate limiter.

    Returns a rate limiter configured for sensitive endpoints
    (password change, account deletion) with very strict limits.
    """
    return _strict_limiter


# Pre-configured rate limit strings based on config
_AUTH_LIMIT = (
    f"{config.rate_limit_auth_per_minute}/minute"
    if config.rate_limit_enabled
    else "1000/minute"
)
_GENERAL_LIMIT = (
    f"{config.rate_limit_api_per_minute}/minute"
    if config.rate_limit_enabled
    else "100/minute"
)
_STRICT_LIMIT = "5/minute"  # Hard-coded strict limit for sensitive operations


def auth_rate_limit(limit: str | None = None):
    """Decorator for authentication endpoints rate limiting.

    Args:
        limit: Optional custom limit string (e.g., "5/minute")
              If not provided, uses config-based auth limit
    """
    effective_limit = limit or _AUTH_LIMIT
    return _auth_limiter.limit(effective_limit)


def general_rate_limit(limit: str | None = None):
    """Decorator for general API endpoints rate limiting.

    Args:
        limit: Optional custom limit string
              If not provided, uses config-based general limit
    """
    effective_limit = limit or _GENERAL_LIMIT
    return _general_limiter.limit(effective_limit)


def strict_rate_limit(limit: str | None = None):
    """Decorator for sensitive endpoints rate limiting.

    Args:
        limit: Optional custom limit string
              If not provided, uses hard-coded strict limit
    """
    effective_limit = limit or _STRICT_LIMIT
    return _strict_limiter.limit(effective_limit)
