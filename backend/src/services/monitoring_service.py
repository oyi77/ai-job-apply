"""Monitoring service implementation for performance monitoring and alerting."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from src.core.monitoring_service import MonitoringService
from src.database.repositories.monitoring_repository import MonitoringRepository
from src.database.config import get_database, database_config
from src.database.models import DBPerformanceMetric
from src.utils.logger import get_logger
from src.config import config


class DatabaseMonitoringService(MonitoringService):
    """Database-backed monitoring service implementation."""
    
    def __init__(self, session: Optional[AsyncSession] = None):
        """Initialize monitoring service."""
        self.session = session
        self.repository: Optional[MonitoringRepository] = None
        self.logger = get_logger(__name__)
        self._metrics_queue: List[Dict[str, Any]] = []
        self._batch_size = 100
        self._batch_interval = 5  # seconds
        
        # Start background task for batch processing
        self._background_task: Optional[asyncio.Task] = None
        self._alert_tasks: set[asyncio.Task] = set()  # Track alert evaluation tasks
        self._max_concurrent_alerts = 5  # Limit concurrent alert evaluations
    
    def _get_repository(self, session: AsyncSession) -> MonitoringRepository:
        """Get or create repository instance with a session.
        
        Args:
            session: Session to use (must be provided).
        
        Note: Caller is responsible for managing session lifecycle using context manager.
        """
        # Create repository with the provided session
        return MonitoringRepository(session)
    
    async def _start_background_task(self):
        """Start background task for batch metric processing."""
        if self._background_task is None or self._background_task.done():
            self._background_task = asyncio.create_task(self._process_metrics_batch())
    
    async def _process_metrics_batch(self):
        """Process metrics in batches using a new session for each batch."""
        while True:
            try:
                await asyncio.sleep(self._batch_interval)
                
                if not self._metrics_queue:
                    continue
                
                # Get batch of metrics
                batch = self._metrics_queue[:self._batch_size]
                self._metrics_queue = self._metrics_queue[self._batch_size:]
                
                # Create a new session for this batch to avoid concurrency issues
                # Use context manager to ensure proper cleanup
                async with database_config.get_session() as session:
                    # Process batch with new session - add all metrics first, then commit once
                    import json
                    
                    for metric_data in batch:
                        try:
                            timestamp = metric_data.get("timestamp") or datetime.now()
                            db_metric = DBPerformanceMetric(
                                metric_name=metric_data["metric_name"],
                                metric_value=metric_data["metric_value"],
                                tags=json.dumps(metric_data.get("tags")) if metric_data.get("tags") else None,
                                timestamp=timestamp
                            )
                            session.add(db_metric)
                        except Exception as e:
                            self.logger.error(f"Error adding metric to batch: {e}", exc_info=True)
                    
                    # Commit all metrics in the batch at once
                    try:
                        await session.commit()
                        self.logger.debug(f"Committed batch of {len(batch)} metrics")
                    except Exception as e:
                        await session.rollback()
                        self.logger.error(f"Error committing metrics batch: {e}", exc_info=True)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in metrics batch processing: {e}", exc_info=True)
    
    async def record_metric(
        self,
        metric_name: str,
        metric_value: float,
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Record a performance metric asynchronously."""
        try:
            # Add to queue for batch processing
            self._metrics_queue.append({
                "metric_name": metric_name,
                "metric_value": metric_value,
                "tags": tags,
                "timestamp": timestamp or datetime.now()
            })
            
            # Start background task if not running
            await self._start_background_task()
            
            # Also evaluate alerts if this is a tracked metric
            # Limit concurrent alert evaluations to prevent thread exhaustion
            try:
                # Clean up completed tasks
                self._alert_tasks = {t for t in self._alert_tasks if not t.done()}
                
                # Only create new task if under limit
                if len(self._alert_tasks) < self._max_concurrent_alerts:
                    task = asyncio.create_task(self._evaluate_metric_alerts(metric_name, metric_value))
                    self._alert_tasks.add(task)
                    # Remove task from set when done (fire-and-forget)
                    task.add_done_callback(self._alert_tasks.discard)
                else:
                    self.logger.debug(f"Skipping alert evaluation - too many concurrent tasks ({len(self._alert_tasks)})")
            except Exception as e:
                self.logger.error(f"Error creating alert evaluation task: {e}", exc_info=True)
            
        except Exception as e:
            self.logger.error(f"Error recording metric: {e}", exc_info=True)
    
    async def _evaluate_metric_alerts(self, metric_name: str, metric_value: float):
        """Evaluate alerts for a specific metric."""
        try:
            # Create a new session for alert evaluation to avoid concurrency issues
            # Use context manager to ensure proper cleanup
            async with database_config.get_session() as session:
                repo = MonitoringRepository(session)
                rules = await repo.get_alert_rules(enabled_only=True)
                
                for rule in rules:
                    if rule.metric_name != metric_name:
                        continue
                    
                    # Check if condition is met
                    condition_met = False
                    if rule.condition == "gt":
                        condition_met = metric_value > rule.threshold
                    elif rule.condition == "gte":
                        condition_met = metric_value >= rule.threshold
                    elif rule.condition == "lt":
                        condition_met = metric_value < rule.threshold
                    elif rule.condition == "lte":
                        condition_met = metric_value <= rule.threshold
                    elif rule.condition == "eq":
                        condition_met = metric_value == rule.threshold
                    
                    if condition_met:
                        # Check cooldown
                        recent_alert = await repo.get_recent_alert_for_rule(
                            rule.id,
                            rule.cooldown_seconds
                        )
                        
                        if recent_alert is None:
                            # Trigger alert
                            message = (
                                f"Alert: {rule.rule_name} - "
                                f"{metric_name} = {metric_value:.2f} "
                                f"{rule.condition} {rule.threshold}"
                            )
                            
                            # create_alert_history already commits in the repository
                            await repo.create_alert_history(
                                alert_rule_id=rule.id
                            )
                            
                            self.logger.warning(f"Alert triggered: {message}")
                            # Note: No need to commit here - repository handles commits
                        
        except Exception as e:
            self.logger.error(f"Error evaluating alerts: {e}", exc_info=True)
    
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
        try:
            # Create a new session for error recording
            # Use context manager to ensure proper cleanup
            async with database_config.get_session() as session:
                repo = MonitoringRepository(session)
                # create_error_log already commits in the repository
                await repo.create_error_log(
                    error_type=error_type,
                    error_message=error_message,
                    stack_trace=stack_trace,
                    request_path=request_path,
                    http_method=http_method,
                    user_id=user_id,
                    severity=severity
                )
                # Note: No need to commit here - repository handles commits
            
            # Check error rate for alerting
            await self._check_error_rate_alert()
            
        except Exception as e:
            self.logger.error(f"Error recording error log: {e}", exc_info=True)
    
    async def _check_error_rate_alert(self):
        """Check if error rate exceeds threshold and trigger alert."""
        try:
            # Use context manager for session
            async with database_config.get_session() as session:
                repo = MonitoringRepository(session)
                
                # Get errors in last 5 minutes
                five_min_ago = datetime.now() - timedelta(minutes=5)
                recent_errors = await repo.get_error_logs(
                    start_time=five_min_ago,
                    limit=1000
                )
                
                # Get total requests in last 5 minutes (approximate)
                recent_metrics = await repo.get_metrics(
                    metric_name="api.request.count",
                    start_time=five_min_ago,
                    limit=1000
                )
                
                total_requests = len(recent_metrics)
                total_errors = len(recent_errors)
                
                if total_requests > 0:
                    error_rate = (total_errors / total_requests) * 100
                    
                    # Check if error rate > 5%
                    if error_rate > 5.0:
                        # Check for existing alert rule
                        rules = await repo.get_alert_rules(enabled_only=True)
                        error_rate_rule = next(
                            (r for r in rules if r.metric_name == "error_rate"),
                            None
                        )
                        
                        if error_rate_rule:
                            recent_alert = await repo.get_recent_alert_for_rule(
                                error_rate_rule.id,
                                error_rate_rule.cooldown_seconds
                            )
                            
                            if recent_alert is None:
                                message = (
                                    f"High error rate detected: {error_rate:.2f}% "
                                    f"({total_errors} errors in {total_requests} requests)"
                                )
                                
                                await repo.create_alert_history(
                                    alert_rule_id=error_rate_rule.id
                                )
                                
                                self.logger.warning(message)
                                
        except Exception as e:
            self.logger.error(f"Error checking error rate: {e}", exc_info=True)
    
    async def get_metrics(
        self,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get metrics with optional filtering."""
        try:
            # Use provided session or create a new one with context manager
            if self.session:
                # Use existing session (don't close it)
                repo = MonitoringRepository(self.session)
                metrics = await repo.get_metrics(
                    metric_name=metric_name,
                    start_time=start_time,
                    end_time=end_time,
                    limit=limit
                )
                return [metric.to_dict() for metric in metrics]
            else:
                # Create new session with context manager
                async with database_config.get_session() as session:
                    repo = MonitoringRepository(session)
                    metrics = await repo.get_metrics(
                        metric_name=metric_name,
                        start_time=start_time,
                        end_time=end_time,
                        limit=limit
                    )
                    return [metric.to_dict() for metric in metrics]
            
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}", exc_info=True)
            return []
    
    async def get_error_logs(
        self,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get error logs with optional filtering."""
        try:
            # Use context manager for session
            if self.session:
                # Use existing session (don't close it)
                repo = self._get_repository(self.session)
                errors = await repo.get_error_logs(
                    error_type=error_type,
                    severity=severity,
                    start_time=start_time,
                    end_time=end_time,
                    limit=limit
                )
                return [error.to_dict() for error in errors]
            else:
                async with database_config.get_session() as session:
                    repo = self._get_repository(session)
                    errors = await repo.get_error_logs(
                        error_type=error_type,
                        severity=severity,
                        start_time=start_time,
                        end_time=end_time,
                        limit=limit
                    )
                    return [error.to_dict() for error in errors]
            
        except Exception as e:
            self.logger.error(f"Error getting error logs: {e}", exc_info=True)
            return []
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            # Use context manager for session
            if self.session:
                repo = self._get_repository(self.session)
                # Get metrics from last 5 minutes
                five_min_ago = datetime.now() - timedelta(minutes=5)
                
                # Response time metrics
                response_time_stats = await repo.get_metric_statistics(
                    "api.response_time",
                    start_time=five_min_ago
                )
                
                # Request count
                request_count_stats = await repo.get_metric_statistics(
                    "api.request.count",
                    start_time=five_min_ago
                )
                
                # Error count
                error_count = len(await repo.get_error_logs(
                    start_time=five_min_ago,
                    limit=1000
                ))
            else:
                async with database_config.get_session() as session:
                    repo = self._get_repository(session)
                    # Get metrics from last 5 minutes
                    five_min_ago = datetime.now() - timedelta(minutes=5)
                    
                    # Response time metrics
                    response_time_stats = await repo.get_metric_statistics(
                        "api.response_time",
                        start_time=five_min_ago
                    )
                    
                    # Request count
                    request_count_stats = await repo.get_metric_statistics(
                        "api.request.count",
                        start_time=five_min_ago
                    )
                    
                    # Error count
                    error_count = len(await repo.get_error_logs(
                        start_time=five_min_ago,
                        limit=1000
                    ))
            
            # Error rate
            total_requests = request_count_stats.get("count", 0)
            error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0.0
            
            # Resource usage (if psutil is available)
            if PSUTIL_AVAILABLE and psutil:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                resources = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used_mb": memory.used / (1024 * 1024),
                    "memory_total_mb": memory.total / (1024 * 1024),
                    "disk_percent": disk.percent,
                    "disk_used_gb": disk.used / (1024 * 1024 * 1024),
                    "disk_total_gb": disk.total / (1024 * 1024 * 1024)
                }
            else:
                resources = {
                    "cpu_percent": 0.0,
                    "memory_percent": 0.0,
                    "memory_used_mb": 0.0,
                    "memory_total_mb": 0.0,
                    "disk_percent": 0.0,
                    "disk_used_gb": 0.0,
                    "disk_total_gb": 0.0,
                    "note": "psutil not available - resource metrics disabled"
                }
            
            return {
                "response_time": {
                    "avg": response_time_stats.get("avg", 0.0),
                    "min": response_time_stats.get("min", 0.0),
                    "max": response_time_stats.get("max", 0.0),
                    "count": response_time_stats.get("count", 0)
                },
                "throughput": {
                    "requests_per_second": request_count_stats.get("count", 0) / 300.0,  # 5 minutes
                    "total_requests": request_count_stats.get("count", 0)
                },
                "error_rate": {
                    "percentage": error_rate,
                    "error_count": error_count,
                    "total_requests": total_requests
                },
                "resources": resources,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting current metrics: {e}", exc_info=True)
            return {}
    
    async def evaluate_alerts(self) -> List[Dict[str, Any]]:
        """Evaluate alert rules and trigger alerts if thresholds are exceeded."""
        try:
            # Use context manager for session
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                rules = await repo.get_alert_rules(enabled_only=True)
                triggered_alerts = []
                
                for rule in rules:
                    # Get recent metric statistics
                    five_min_ago = datetime.now() - timedelta(minutes=5)
                    stats = await repo.get_metric_statistics(
                        rule.metric_name,
                        start_time=five_min_ago
                    )
                    
                    if stats["count"] == 0:
                        continue
                    
                    # Check condition based on average value
                    avg_value = stats["avg"]
                    condition_met = False
                    
                    if rule.condition == "gt":
                        condition_met = avg_value > rule.threshold
                    elif rule.condition == "gte":
                        condition_met = avg_value >= rule.threshold
                    elif rule.condition == "lt":
                        condition_met = avg_value < rule.threshold
                    elif rule.condition == "lte":
                        condition_met = avg_value <= rule.threshold
                    elif rule.condition == "eq":
                        condition_met = avg_value == rule.threshold
                    
                    if condition_met:
                        # Check cooldown
                        recent_alert = await repo.get_recent_alert_for_rule(
                            rule.id,
                            rule.cooldown_seconds
                        )
                        
                        if recent_alert is None:
                            message = (
                                f"Alert: {rule.rule_name} - "
                                f"{rule.metric_name} = {avg_value:.2f} "
                                f"{rule.condition} {rule.threshold}"
                            )
                            
                            alert = await repo.create_alert_history(
                                alert_rule_id=rule.id,
                                message=message,
                                metric_value=avg_value
                            )
                            # Note: create_alert_history already commits in the repository
                            
                            triggered_alerts.append(alert.to_dict())
                            self.logger.warning(f"Alert triggered: {message}")
                
                # Note: No need to commit here - each alert was already committed by repository
                return triggered_alerts
            
        except Exception as e:
            self.logger.error(f"Error evaluating alerts: {e}", exc_info=True)
            return []
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts."""
        try:
            # Use context manager for session
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                alerts = await repo.get_active_alerts()
                
                return [alert.to_dict() for alert in alerts]
            
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}", exc_info=True)
            return []
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert."""
        try:
            # Use context manager for session
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                result = await repo.resolve_alert(alert_id)
                await session.commit()
                return result
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}", exc_info=True)
            return False
    
    async def create_alert_rule(
        self,
        rule_name: str,
        metric_name: str,
        threshold: float,
        condition: str,
        cooldown_seconds: int = 300
    ) -> Dict[str, Any]:
        """Create a new alert rule."""
        try:
            # Use context manager for session
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                rule = await repo.create_alert_rule(
                    rule_name=rule_name,
                    metric_name=metric_name,
                    threshold=threshold,
                    condition=condition,
                    cooldown_seconds=cooldown_seconds
                )
                await session.commit()
                
                return rule.to_dict()
            
        except Exception as e:
            self.logger.error(f"Error creating alert rule: {e}", exc_info=True)
            raise
    
    async def update_alert_rule(
        self,
        rule_id: str,
        enabled: Optional[bool] = None,
        threshold: Optional[float] = None,
        condition: Optional[str] = None,
        cooldown_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update an existing alert rule."""
        try:
            # Use context manager for session
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                rule = await repo.update_alert_rule(
                    rule_id=rule_id,
                    enabled=enabled,
                    threshold=threshold,
                    condition=condition,
                    cooldown_seconds=cooldown_seconds
                )
                
                if rule is None:
                    raise ValueError(f"Alert rule {rule_id} not found")
                
                await session.commit()
                return rule.to_dict()
            
        except Exception as e:
            self.logger.error(f"Error updating alert rule: {e}", exc_info=True)
            raise
    
    async def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get all alert rules."""
        try:
            # Use context manager for session
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                rules = await repo.get_alert_rules()
                
                return [rule.to_dict() for rule in rules]
            
        except Exception as e:
            self.logger.error(f"Error getting alert rules: {e}", exc_info=True)
            return []
    
    async def aggregate_metrics(self, aggregation_type: str = "hourly") -> None:
        """Aggregate metrics (hourly or daily)."""
        try:
            # Use context manager for session
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                
                if aggregation_type == "hourly":
                    # Aggregate last hour's metrics
                    one_hour_ago = datetime.now() - timedelta(hours=1)
                    metrics = await repo.get_metrics(
                        start_time=one_hour_ago,
                        limit=10000
                    )
                    
                    # Group by metric name and hour
                    grouped = {}
                    for metric in metrics:
                        if hasattr(metric, 'timestamp'):
                            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
                        else:
                            # Handle dict format
                            from datetime import datetime
                            hour_key = datetime.fromisoformat(metric.get("timestamp", datetime.now().isoformat())).replace(minute=0, second=0, microsecond=0)
                        
                        metric_name = metric.metric_name if hasattr(metric, 'metric_name') else metric.get("metric_name")
                        metric_value = metric.metric_value if hasattr(metric, 'metric_value') else metric.get("metric_value")
                        
                        key = (metric_name, hour_key.isoformat())
                        
                        if key not in grouped:
                            grouped[key] = []
                        grouped[key].append(metric_value)
                    
                    # Create aggregated metrics
                    for (metric_name, hour_str), values in grouped.items():
                        await repo.create_metric(
                            metric_name=f"{metric_name}.hourly",
                            metric_value=sum(values) / len(values),
                            tags={"aggregation": "hourly", "hour": hour_str},
                            timestamp=datetime.fromisoformat(hour_str)
                        )
                    
                    self.logger.info(f"Aggregated {len(grouped)} hourly metrics")
                    
                elif aggregation_type == "daily":
                    # Similar logic for daily aggregation
                    one_day_ago = datetime.now() - timedelta(days=1)
                    all_metrics = await repo.get_metrics(
                        start_time=one_day_ago,
                        limit=10000
                    )
                    # Filter hourly metrics
                    metrics = [m for m in all_metrics if ".hourly" in (m.metric_name if hasattr(m, 'metric_name') else m.get("metric_name", ""))]
                    
                    # Group by metric name and day
                    grouped = {}
                    for metric in metrics:
                        if hasattr(metric, 'timestamp'):
                            day_key = metric.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                            metric_name = metric.metric_name
                            metric_value = metric.metric_value
                        else:
                            # Handle dict format
                            from datetime import datetime
                            day_key = datetime.fromisoformat(metric.get("timestamp", datetime.now().isoformat())).replace(hour=0, minute=0, second=0, microsecond=0)
                            metric_name = metric.get("metric_name", "")
                            metric_value = metric.get("metric_value", 0.0)
                        
                        metric_base = metric_name.replace(".hourly", "")
                        key = (metric_base, day_key.isoformat())
                        
                        if key not in grouped:
                            grouped[key] = []
                        grouped[key].append(metric_value)
                    
                    # Create aggregated metrics
                    for (metric_name, day_str), values in grouped.items():
                        await repo.create_metric(
                            metric_name=f"{metric_name}.daily",
                            metric_value=sum(values) / len(values),
                            tags={"aggregation": "daily", "day": day_str},
                            timestamp=datetime.fromisoformat(day_str)
                        )
                    
                    self.logger.info(f"Aggregated {len(grouped)} daily metrics")
                
                # Commit aggregated metrics
                await session.commit()
            
        except Exception as e:
            self.logger.error(f"Error aggregating metrics: {e}", exc_info=True)
    
    async def cleanup_old_metrics(self, retention_days: int = 7) -> int:
        """Clean up old metrics based on retention policy."""
        try:
            # Use context manager for session
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                deleted_count = await repo.delete_old_metrics(retention_days)
                await session.commit()
                
                self.logger.info(f"Cleaned up {deleted_count} old metrics")
                
                return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old metrics: {e}", exc_info=True)
            return 0
    
    async def is_available(self) -> bool:
        """Check if the monitoring service is available."""
        try:
            # Use context manager for session
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                # Try a simple query to check database connection
                await repo.get_metrics(limit=1)
                return True
        except Exception as e:
            self.logger.error(f"Monitoring service not available: {e}", exc_info=True)
            return False
    
    async def cleanup(self) -> None:
        """Clean up background tasks and resources."""
        try:
            # Cancel background metrics batch processing task
            if self._background_task and not self._background_task.done():
                self._background_task.cancel()
                try:
                    await self._background_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel all pending alert evaluation tasks
            for task in self._alert_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete cancellation (with timeout)
            if self._alert_tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*self._alert_tasks, return_exceptions=True),
                        timeout=2.0
                    )
                except asyncio.TimeoutError:
                    self.logger.warning("Some alert tasks didn't cancel in time")
                except Exception:
                    pass
            
            self._alert_tasks.clear()
            self._background_task = None
            self.logger.info("Monitoring service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during monitoring service cleanup: {e}", exc_info=True)
