"""Pydantic models for Web Push subscriptions and payloads."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class PushSubscriptionKeys(BaseModel):
    """Keys portion of a Web Push subscription."""

    p256dh: str = Field(..., description="Base64-encoded p256dh key")
    auth: str = Field(..., description="Base64-encoded auth secret")

    @field_validator("p256dh", "auth")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Key must be non-empty")
        return v


class PushSubscriptionCreate(BaseModel):
    """Create/update a push subscription for a user."""

    endpoint: str = Field(..., description="Push service endpoint URL")
    keys: PushSubscriptionKeys

    @field_validator("endpoint")
    @classmethod
    def _validate_endpoint(cls, v: str) -> str:
        endpoint = v.strip()
        if not endpoint:
            raise ValueError("Endpoint must be provided")
        if not endpoint.startswith("https://"):
            raise ValueError("Endpoint must start with https://")
        return endpoint


class PushSubscriptionDelete(BaseModel):
    """Delete a push subscription by endpoint."""

    endpoint: str = Field(..., description="Push service endpoint URL")

    @field_validator("endpoint")
    @classmethod
    def _validate_endpoint(cls, v: str) -> str:
        endpoint = v.strip()
        if not endpoint:
            raise ValueError("Endpoint must be provided")
        return endpoint


class PushMessage(BaseModel):
    """A minimal push message payload.

    The frontend Service Worker usually expects JSON.
    """

    title: str = Field(..., max_length=120)
    body: str = Field(..., max_length=500)
    data: Optional[Dict[str, Any]] = None
