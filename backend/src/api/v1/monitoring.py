"""Monitoring API endpoints for performance metrics and alerting."""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from src.services.monitoring_service import DatabaseMonitoringService
from src.services.service_registry import ServiceRegistry
from src.api.dependencies import get_service_registry
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# Request/Response models
class MetricResponse(BaseModel):
    """Metric response model."""
    id: str
    metric_name: str
    metric_value: float
    tags: dict
    timestamp: str
    created_at: str


class ErrorLogResponse(BaseModel):
    """Error log response model."""
    id: str
    error_type: str
    error_message: str
    stack_trace: Optional[str]
    request_path: Optional[str]
    http_method: Optional[str]
    user_id: Optional[str]
    severity: str
    created_at: str


class AlertRuleRequest(BaseModel):
    """Alert rule request model."""
    rule_name: str = Field(..., description="Name of the alert rule")
    metric_name: str = Field(..., description="Metric name to monitor")
    threshold: float = Field(..., description="Threshold value")
    condition: str = Field(..., description="Condition: gt, gte, lt, lte, eq")
    cooldown_seconds: int = Field(default=300, description="Cooldown period in seconds")


class AlertRuleResponse(BaseModel):
    """Alert rule response model."""
    id: str
    rule_name: str
    metric_name: str
    threshold: float
    condition: str
    enabled: bool
    cooldown_seconds: int
    created_at: str
    updated_at: str


class AlertResponse(BaseModel):
    """Alert response model."""
    id: str
    alert_rule_id: str
    triggered_at: str
    resolved_at: Optional[str]
    status: str
    message: str
    metric_value: Optional[float]


class CurrentMetricsResponse(BaseModel):
    """Current metrics response model."""
    response_time: dict
    throughput: dict
    error_rate: dict
    resources: dict
    timestamp: str


def get_monitoring_service(
    service_registry: ServiceRegistry = Depends(get_service_registry)
) -> DatabaseMonitoringService:
    """Get monitoring service from registry."""
    return service_registry.get_monitoring_service()


@router.get("/metrics", response_model=List[MetricResponse])
async def get_metrics(
    metric_name: Optional[str] = Query(None, description="Filter by metric name"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    monitoring_service: DatabaseMonitoringService = Depends(get_monitoring_service)
):
    """Get performance metrics with optional filtering."""
    try:
        metrics = await monitoring_service.get_metrics(
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/current", response_model=CurrentMetricsResponse)
async def get_current_metrics(
    monitoring_service: DatabaseMonitoringService = Depends(get_monitoring_service)
):
    """Get current system metrics."""
    try:
        metrics = await monitoring_service.get_current_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting current metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors", response_model=List[ErrorLogResponse])
async def get_error_logs(
    error_type: Optional[str] = Query(None, description="Filter by error type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    monitoring_service: DatabaseMonitoringService = Depends(get_monitoring_service)
):
    """Get error logs with optional filtering."""
    try:
        errors = await monitoring_service.get_error_logs(
            error_type=error_type,
            severity=severity,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        return errors
    except Exception as e:
        logger.error(f"Error getting error logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[AlertResponse])
async def get_active_alerts(
    monitoring_service: DatabaseMonitoringService = Depends(get_monitoring_service)
):
    """Get currently active alerts."""
    try:
        alerts = await monitoring_service.get_active_alerts()
        return alerts
    except Exception as e:
        logger.error(f"Error getting active alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    monitoring_service: DatabaseMonitoringService = Depends(get_monitoring_service)
):
    """Resolve an active alert."""
    try:
        success = await monitoring_service.resolve_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"message": "Alert resolved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alert-rules", response_model=List[AlertRuleResponse])
async def get_alert_rules(
    monitoring_service: DatabaseMonitoringService = Depends(get_monitoring_service)
):
    """Get all alert rules."""
    try:
        rules = await monitoring_service.get_alert_rules()
        return rules
    except Exception as e:
        logger.error(f"Error getting alert rules: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alert-rules", response_model=AlertRuleResponse)
async def create_alert_rule(
    rule: AlertRuleRequest,
    monitoring_service: DatabaseMonitoringService = Depends(get_monitoring_service)
):
    """Create a new alert rule."""
    try:
        # Validate condition
        valid_conditions = ["gt", "gte", "lt", "lte", "eq"]
        if rule.condition not in valid_conditions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid condition. Must be one of: {valid_conditions}"
            )
        
        created_rule = await monitoring_service.create_alert_rule(
            rule_name=rule.rule_name,
            metric_name=rule.metric_name,
            threshold=rule.threshold,
            condition=rule.condition,
            cooldown_seconds=rule.cooldown_seconds
        )
        return created_rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert rule: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/alert-rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: str,
    enabled: Optional[bool] = Query(None, description="Enable/disable rule"),
    threshold: Optional[float] = Query(None, description="Update threshold"),
    condition: Optional[str] = Query(None, description="Update condition"),
    cooldown_seconds: Optional[int] = Query(None, description="Update cooldown"),
    monitoring_service: DatabaseMonitoringService = Depends(get_monitoring_service)
):
    """Update an existing alert rule."""
    try:
        updated_rule = await monitoring_service.update_alert_rule(
            rule_id=rule_id,
            enabled=enabled,
            threshold=threshold,
            condition=condition,
            cooldown_seconds=cooldown_seconds
        )
        return updated_rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating alert rule: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/evaluate")
async def evaluate_alerts(
    monitoring_service: DatabaseMonitoringService = Depends(get_monitoring_service)
):
    """Manually trigger alert evaluation."""
    try:
        triggered_alerts = await monitoring_service.evaluate_alerts()
        return {
            "message": f"Evaluated alerts, triggered {len(triggered_alerts)} new alerts",
            "triggered_alerts": triggered_alerts
        }
    except Exception as e:
        logger.error(f"Error evaluating alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/detailed")
async def get_detailed_health(
    monitoring_service: DatabaseMonitoringService = Depends(get_monitoring_service),
    service_registry: ServiceRegistry = Depends(get_service_registry)
):
    """Get detailed system health status."""
    try:
        # Get current metrics
        metrics = await monitoring_service.get_current_metrics()
        
        # Get service health
        service_health = {}
        try:
            ai_service = service_registry.get_ai_service()
            service_health["ai_service"] = {
                "status": "healthy" if await ai_service.is_available() else "unhealthy",
                "available": await ai_service.is_available()
            }
        except Exception as e:
            service_health["ai_service"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Get database health
        database_health = {
            "status": "healthy" if await monitoring_service.is_available() else "unhealthy",
            "available": await monitoring_service.is_available()
        }
        
        # Overall health
        overall_health = "healthy"
        if not database_health["available"]:
            overall_health = "unhealthy"
        elif service_health.get("ai_service", {}).get("status") != "healthy":
            overall_health = "degraded"
        
        return {
            "overall_status": overall_health,
            "database": database_health,
            "services": service_health,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting detailed health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
