"""Authentication-related validation helpers."""

from __future__ import annotations

from datetime import datetime, timezone


def ensure_timezone_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware (UTC fallback)."""

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def validate_non_empty_str(value: object, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"Invalid {field_name}")
    return value
