"""Database query performance monitoring using SQLAlchemy event listeners."""

import time
from typing import Optional, Union
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Global monitoring service instance (set by setup function)
_monitoring_service: Optional[object] = None

def set_monitoring_service(monitoring_service):
    """Set the monitoring service instance."""
    global _monitoring_service
    _monitoring_service = monitoring_service

def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Event listener executed before a query."""
    conn.info.setdefault('query_start_time', []).append(time.time())
    # Only log query start at DEBUG level to reduce noise
    logger.debug(f"Executing query: {statement[:100]}")

async def _record_query_metric(query_time: float, statement: str):
    """Record query metric asynchronously."""
    if _monitoring_service is None:
        return
    
    try:
        # Extract table name from statement (simple heuristic)
        table_name = "unknown"
        statement_lower = statement.lower().strip()
        if "from" in statement_lower:
            parts = statement_lower.split("from")
            if len(parts) > 1:
                table_part = parts[1].split()[0]
                table_name = table_part.strip("()")
        
        # Record query time metric
        await _monitoring_service.record_metric(
            metric_name="database.query_time",
            metric_value=query_time * 1000,  # Convert to milliseconds
            tags={
                "table": table_name,
                "query_type": statement_lower.split()[0] if statement_lower else "unknown"
            }
        )
        
        # Tag slow queries
        if query_time > 0.1:  # 100ms threshold
            await _monitoring_service.record_metric(
                metric_name="database.slow_query",
                metric_value=1.0,
                tags={
                    "table": table_name,
                    "query_time_ms": str(query_time * 1000)
                }
            )
            
    except Exception as e:
        logger.error(f"Error recording query metric: {e}", exc_info=True)

def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Event listener executed after a query."""
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    # Use DEBUG level for normal queries to reduce log noise
    logger.debug(f"Query executed in {total_time:.3f}s: {statement[:100]}")
    
    if total_time > 0.1:  # 100ms threshold
        logger.warning(f"Slow query detected ({total_time:.3f}s): {statement}")
    
    # Record metric asynchronously if monitoring service is available
    if _monitoring_service is not None:
        import asyncio
        try:
            # Try to get running event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule coroutine
                asyncio.create_task(_record_query_metric(total_time, statement))
            else:
                # Run in new event loop
                asyncio.run(_record_query_metric(total_time, statement))
        except RuntimeError:
            # No event loop, create one
            asyncio.run(_record_query_metric(total_time, statement))
        except Exception as e:
            logger.error(f"Error scheduling query metric: {e}", exc_info=True)

def setup_query_performance_monitoring(engine: Union[Engine, AsyncEngine], monitoring_service=None):
    """Attach event listeners to the SQLAlchemy engine."""
    if monitoring_service:
        set_monitoring_service(monitoring_service)
    
    # For async engines, we need to use sync_engine for event listeners
    if isinstance(engine, AsyncEngine):
        sync_engine = engine.sync_engine
        logger.info("Using sync_engine for async engine event listeners")
    else:
        sync_engine = engine
    
    try:
        event.listen(sync_engine, "before_cursor_execute", before_cursor_execute)
        event.listen(sync_engine, "after_cursor_execute", after_cursor_execute)
        logger.info("Query performance monitoring is active.")
    except Exception as e:
        logger.warning(f"Could not setup query performance monitoring: {e}")
        # Don't raise - allow app to continue without monitoring