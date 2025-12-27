"""Monitoring service interface for performance monitoring and alerting."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class MonitoringService(ABC):
    """Abstract interface for monitoring and performance tracking."""
    
    @abstractmethod
    async def record_metric(
        self,
        metric_name: str,
        metric_value: float,
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Record a performance metric."""
        pass
    
    @abstractmethod
    async def record_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        request_path: Optional[str] = None,
        http_method: Optional[str] = None,
        user_id: Optional[str] = None,
        severity: str = "error"
    ) -> None:
        """Record an error for tracking."""
        pass
    
    @abstractmethod
    async def get_metrics(
        self,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get metrics with optional filtering."""
        pass
    
    @abstractmethod
    async def get_error_logs(
        self,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get error logs with optional filtering."""
        pass
    
    @abstractmethod
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics (response times, error rates, throughput)."""
        pass
    
    @abstractmethod
    async def evaluate_alerts(self) -> List[Dict[str, Any]]:
        """Evaluate alert rules and trigger alerts if thresholds are exceeded."""
        pass
    
    @abstractmethod
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts."""
        pass
    
    @abstractmethod
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert."""
        pass
    
    @abstractmethod
    async def create_alert_rule(
        self,
        rule_name: str,
        metric_name: str,
        threshold: float,
        condition: str,
        cooldown_seconds: int = 300
    ) -> Dict[str, Any]:
        """Create a new alert rule."""
        pass
    
    @abstractmethod
    async def update_alert_rule(
        self,
        rule_id: str,
        enabled: Optional[bool] = None,
        threshold: Optional[float] = None,
        condition: Optional[str] = None,
        cooldown_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update an existing alert rule."""
        pass
    
    @abstractmethod
    async def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get all alert rules."""
        pass
    
    @abstractmethod
    async def aggregate_metrics(
        self,
        aggregation_type: str = "hourly"
    ) -> None:
        """Aggregate metrics (hourly or daily)."""
        pass
    
    @abstractmethod
    async def cleanup_old_metrics(self, retention_days: int = 7) -> int:
        """Clean up old metrics based on retention policy."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the monitoring service is available."""
        pass
