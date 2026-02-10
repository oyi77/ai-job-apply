from typing import Optional
from datetime import datetime, timezone


class FailureLog:
    """Domain model for failure log entries."""

    def __init__(
        self,
        id: str,
        user_id: str,
        task_name: str,
        platform: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str],
        screenshot: Optional[str],  # Base64 encoded image
        job_id: Optional[str],
        application_id: Optional[str],
        created_at: datetime,
    ):
        self.id = id
        self.user_id = user_id
        self.task_name = task_name
        self.platform = platform
        self.error_type = error_type
        self.error_message = error_message
        self.stack_trace = stack_trace
        self.screenshot = screenshot
        self.job_id = job_id
        self.application_id = application_id
        self.created_at = created_at

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_name": self.task_name,
            "platform": self.platform,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "screenshot": self.screenshot,
            "job_id": self.job_id,
            "application_id": self.application_id,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FailureLog":
        """Create FailureLog from dictionary."""
        return cls(
            id=data.get("id"),
            user_id=data["user_id"],
            task_name=data.get("task_name"),
            platform=data.get("platform"),
            error_type=data.get("error_type"),
            error_message=data.get("error_message"),
            stack_trace=data.get("stack_trace"),
            screenshot=data.get("screenshot"),
            job_id=data.get("job_id"),
            application_id=data.get("application_id"),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(timezone.utc),
        )
