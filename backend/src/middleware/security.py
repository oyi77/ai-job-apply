"""
Security middleware consolidation for FastAPI.

This module provides a centralized setup function for all security-related
middleware including CORS, security headers, rate limiting, and trusted hosts.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from src.config import config
from src.middleware.security_headers import SecurityHeadersMiddleware
from src.middleware.rate_limiter import (
    _auth_limiter,
    _general_limiter,
    _strict_limiter,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def setup_security_middleware(app: FastAPI) -> None:
    """
    Setup all security middleware for the FastAPI application.

    This function consolidates security middleware setup including:
    - CORS (Cross-Origin Resource Sharing)
    - Security Headers (CSP, X-Frame-Options, etc.)
    - Rate Limiting (auth, general, strict)
    - Trusted Host validation

    Args:
        app: FastAPI application instance

    Note:
        Middleware is added in reverse order of execution.
        The last middleware added is the first to execute.
        Order: TrustedHost -> RateLimiter -> SecurityHeaders -> CORS
    """

    # 1. Add CORS middleware (outermost, executes last)
    _setup_cors_middleware(app)

    # 2. Add Security Headers middleware
    _setup_security_headers_middleware(app)

    # 3. Add Rate Limiting (via state, not as middleware)
    _setup_rate_limiting(app)

    # 4. Add Trusted Host middleware (innermost, executes first)
    _setup_trusted_host_middleware(app)

    logger.info("Security middleware setup completed successfully")


def _setup_cors_middleware(app: FastAPI) -> None:
    """
    Setup CORS middleware with secure defaults.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
    logger.debug(f"CORS middleware configured with origins: {config.cors_origins}")


def _setup_security_headers_middleware(app: FastAPI) -> None:
    """
    Setup security headers middleware.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(SecurityHeadersMiddleware)
    logger.debug("Security headers middleware added")


def _setup_rate_limiting(app: FastAPI) -> None:
    """
    Setup rate limiting by attaching limiters to app state.

    The actual rate limiting is applied via decorators on endpoints.
    This function ensures the limiters are available in app state.

    Args:
        app: FastAPI application instance
    """
    app.state.auth_limiter = _auth_limiter
    app.state.general_limiter = _general_limiter
    app.state.strict_limiter = _strict_limiter

    if config.rate_limit_enabled:
        logger.debug(
            f"Rate limiting enabled: "
            f"auth={config.rate_limit_auth_per_minute}/min, "
            f"api={config.rate_limit_api_per_minute}/min"
        )
    else:
        logger.debug("Rate limiting is disabled")


def _setup_trusted_host_middleware(app: FastAPI) -> None:
    """
    Setup trusted host middleware to prevent Host header attacks.

    Args:
        app: FastAPI application instance
    """
    # Get allowed hosts from config
    allowed_hosts = _get_allowed_hosts()

    if allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts,
        )
        logger.debug(f"Trusted host middleware configured with: {allowed_hosts}")
    else:
        logger.warning(
            "No trusted hosts configured. "
            "Consider setting HOST or ALLOWED_HOSTS in environment."
        )


def _get_allowed_hosts() -> list[str]:
    """
    Get list of allowed hosts from configuration.

    Returns:
        List of allowed hostnames
    """
    allowed_hosts = []

    # Add configured host
    if hasattr(config, "host") and config.host:
        allowed_hosts.append(config.host)

    # Add localhost variants for development
    if config.debug or config.ENVIRONMENT == "development":
        allowed_hosts.extend(
            [
                "localhost",
                "127.0.0.1",
                "*.localhost",
            ]
        )

    # Add frontend URL host if configured
    if hasattr(config, "frontend_url") and config.frontend_url:
        try:
            from urllib.parse import urlparse

            parsed = urlparse(config.frontend_url)
            if parsed.hostname:
                allowed_hosts.append(parsed.hostname)
        except Exception as e:
            logger.warning(f"Could not parse frontend_url: {e}")

    return list(set(allowed_hosts))  # Remove duplicates
