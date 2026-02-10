"""API package for the AI Job Application Assistant."""

from typing import Any

__all__ = ["app", "create_app"]


def __getattr__(name: str) -> Any:
    """Lazily import app objects to avoid import side effects."""
    if name in __all__:
        from src.api.app import app, create_app

        return {"app": app, "create_app": create_app}[name]
    raise AttributeError(f"module 'src.api' has no attribute {name!r}")


def __dir__() -> list[str]:
    """Return available attributes for dir()."""
    return sorted(list(globals().keys()) + __all__)
