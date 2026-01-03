"""Monitoring repository for database operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from src.database.models import (
    DBPerformanceMetric,
    DBErrorLog,
    DBAlertRule,
    DBAlertHistory
)
from src.utils.logger import get_logger


class MonitoringRepository:
    """Repository for monitoring database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
        self.logger = get_logger(__name__)
    
    # Metrics operations
    async def create_metric(
        self,
        metric_name: str,
        metric_value: float,
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> DBPerformanceMetric:
        """Create a new performance metric."""
        try:
            import json
            
            if timestamp is None:
                timestamp = datetime.now()
            
            db_metric = DBPerformanceMetric(
                metric_name=metric_name,
                metric_value=metric_value,
                tags=json.dumps(tags) if tags else None,
                timestamp=timestamp
            )
            self.session.add(db_metric)
            await self.session.commit()
            await self.session.refresh(db_metric)
            
            return db_metric
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating metric: {e}", exc_info=True)
            raise
    
    async def get_metrics(
        self,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DBPerformanceMetric]:
        """Get metrics with optional filtering."""
        try:
            stmt = select(DBPerformanceMetric)
            
            if metric_name:
                stmt = stmt.where(DBPerformanceMetric.metric_name == metric_name)
            
            if start_time:
                stmt = stmt.where(DBPerformanceMetric.timestamp >= start_time)
            
            if end_time:
                stmt = stmt.where(DBPerformanceMetric.timestamp <= end_time)
            
            stmt = stmt.order_by(desc(DBPerformanceMetric.timestamp)).limit(limit)
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}", exc_info=True)
            raise
    
    async def get_metric_statistics(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get aggregated statistics for a metric."""
        try:
            stmt = select(
                func.avg(DBPerformanceMetric.metric_value).label("avg"),
                func.min(DBPerformanceMetric.metric_value).label("min"),
                func.max(DBPerformanceMetric.metric_value).label("max"),
                func.count(DBPerformanceMetric.id).label("count")
            ).where(DBPerformanceMetric.metric_name == metric_name)
            
            if start_time:
                stmt = stmt.where(DBPerformanceMetric.timestamp >= start_time)
            
            if end_time:
                stmt = stmt.where(DBPerformanceMetric.timestamp <= end_time)
            
            result = await self.session.execute(stmt)
            row = result.first()
            
            if row and row.count > 0:
                return {
                    "avg": float(row.avg) if row.avg else 0.0,
                    "min": float(row.min) if row.min else 0.0,
                    "max": float(row.max) if row.max else 0.0,
                    "count": int(row.count)
                }
            
            return {"avg": 0.0, "min": 0.0, "max": 0.0, "count": 0}
            
        except Exception as e:
            self.logger.error(f"Error getting metric statistics: {e}", exc_info=True)
            raise
    
    async def delete_old_metrics(self, retention_days: int = 7) -> int:
        """Delete metrics older than retention period."""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            stmt = delete(DBPerformanceMetric).where(
                DBPerformanceMetric.timestamp < cutoff_date
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            deleted_count = result.rowcount
            self.logger.info(f"Deleted {deleted_count} old metrics")
            
            return deleted_count
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error deleting old metrics: {e}", exc_info=True)
            raise
    
    # Error log operations
    async def create_error_log(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        request_path: Optional[str] = None,
        http_method: Optional[str] = None,
        user_id: Optional[str] = None,
        severity: str = "error"
    ) -> DBErrorLog:
        """Create a new error log entry."""
        try:
            db_error = DBErrorLog(
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                request_path=request_path,
                http_method=http_method,
                user_id=user_id,
                severity=severity
            )
            self.session.add(db_error)
            await self.session.commit()
            await self.session.refresh(db_error)
            
            return db_error
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating error log: {e}", exc_info=True)
            raise
    
    async def get_error_logs(
        self,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DBErrorLog]:
        """Get error logs with optional filtering."""
        try:
            stmt = select(DBErrorLog)
            
            if error_type:
                stmt = stmt.where(DBErrorLog.error_type == error_type)
            
            if severity:
                stmt = stmt.where(DBErrorLog.severity == severity)
            
            if start_time:
                stmt = stmt.where(DBErrorLog.created_at >= start_time)
            
            if end_time:
                stmt = stmt.where(DBErrorLog.created_at <= end_time)
            
            stmt = stmt.order_by(desc(DBErrorLog.created_at)).limit(limit)
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            self.logger.error(f"Error getting error logs: {e}", exc_info=True)
            raise
    
    # Alert rule operations
    async def create_alert_rule(
        self,
        rule_name: str,
        metric_name: str,
        threshold: float,
        condition: str,
        cooldown_seconds: int = 300
    ) -> DBAlertRule:
        """Create a new alert rule."""
        try:
            db_rule = DBAlertRule(
                rule_name=rule_name,
                metric_name=metric_name,
                threshold=threshold,
                condition=condition,
                cooldown_seconds=cooldown_seconds,
                enabled=True
            )
            self.session.add(db_rule)
            await self.session.commit()
            await self.session.refresh(db_rule)
            
            return db_rule
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating alert rule: {e}", exc_info=True)
            raise
    
    async def get_alert_rules(self, enabled_only: bool = False) -> List[DBAlertRule]:
        """Get all alert rules."""
        try:
            stmt = select(DBAlertRule)
            
            if enabled_only:
                stmt = stmt.where(DBAlertRule.enabled == True)
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            self.logger.error(f"Error getting alert rules: {e}", exc_info=True)
            raise
    
    async def update_alert_rule(
        self,
        rule_id: str,
        enabled: Optional[bool] = None,
        threshold: Optional[float] = None,
        condition: Optional[str] = None,
        cooldown_seconds: Optional[int] = None
    ) -> Optional[DBAlertRule]:
        """Update an existing alert rule."""
        try:
            stmt = select(DBAlertRule).where(DBAlertRule.id == rule_id)
            result = await self.session.execute(stmt)
            db_rule = result.scalar_one_or_none()
            
            if not db_rule:
                return None
            
            if enabled is not None:
                db_rule.enabled = enabled
            if threshold is not None:
                db_rule.threshold = threshold
            if condition is not None:
                db_rule.condition = condition
            if cooldown_seconds is not None:
                db_rule.cooldown_seconds = cooldown_seconds
            
            db_rule.updated_at = datetime.now()
            
            await self.session.commit()
            await self.session.refresh(db_rule)
            
            return db_rule
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating alert rule: {e}", exc_info=True)
            raise
    
    # Alert history operations
    async def create_alert_history(
        self,
        alert_rule_id: str,
        message: Optional[str] = None,
        metric_value: Optional[float] = None
    ) -> DBAlertHistory:
        """Create a new alert history entry.
        
        Note: DBAlertHistory model only stores alert_rule_id, triggered_at, and resolved_at.
        The message and metric_value parameters are logged but not stored.
        
        Args:
            alert_rule_id: ID of the alert rule that triggered
            message: Optional message for logging (not stored in DB)
            metric_value: Optional metric value for logging (not stored in DB)
        """
        try:
            db_alert = DBAlertHistory(
                alert_rule_id=alert_rule_id,
                triggered_at=datetime.now(timezone.utc),
                resolved_at=None  # Active alerts have resolved_at = None
            )
            # Log message and metric_value for debugging (not stored in DB)
            if message:
                self.logger.debug(f"Creating alert history for rule {alert_rule_id}: {message}, metric_value={metric_value}")
            else:
                self.logger.debug(f"Creating alert history for rule {alert_rule_id}")
            self.session.add(db_alert)
            await self.session.commit()
            await self.session.refresh(db_alert)
            
            return db_alert
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating alert history: {e}", exc_info=True)
            raise
    
    async def get_active_alerts(self) -> List[DBAlertHistory]:
        """Get all active alerts."""
        try:
            stmt = select(DBAlertHistory).options(
                selectinload(DBAlertHistory.alert_rule)
            ).where(
                DBAlertHistory.resolved_at.is_(None)  # Active = not resolved
            ).order_by(desc(DBAlertHistory.triggered_at))
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}", exc_info=True)
            raise
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert."""
        try:
            stmt = select(DBAlertHistory).where(DBAlertHistory.id == alert_id)
            result = await self.session.execute(stmt)
            db_alert = result.scalar_one_or_none()
            
            if not db_alert:
                return False
            
            db_alert.resolved_at = datetime.now(timezone.utc)  # Resolve by setting resolved_at
            
            await self.session.commit()
            
            return True
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error resolving alert: {e}", exc_info=True)
            raise
    
    async def get_recent_alert_for_rule(
        self,
        alert_rule_id: str,
        cooldown_seconds: int
    ) -> Optional[DBAlertHistory]:
        """Get the most recent alert for a rule within the cooldown period."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=cooldown_seconds)
            
            # An alert is "active" if resolved_at is None (not yet resolved)
            stmt = select(DBAlertHistory).where(
                and_(
                    DBAlertHistory.alert_rule_id == alert_rule_id,
                    DBAlertHistory.triggered_at >= cutoff_time,
                    DBAlertHistory.resolved_at.is_(None)  # Active = not resolved
                )
            ).order_by(desc(DBAlertHistory.triggered_at)).limit(1)
            
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            self.logger.error(f"Error getting recent alert: {e}", exc_info=True)
            raise
