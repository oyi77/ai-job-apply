"""Database query performance monitoring using SQLAlchemy event listeners."""

import time
from sqlalchemy import event
from sqlalchemy.engine import Engine
from ..utils.logger import get_logger

logger = get_logger(__name__)

def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Event listener executed before a query."""
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug(f"Executing query: {statement}")

def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Event listener executed after a query."""
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    logger.info(f"Query executed in {total_time:.3f}s")
    if total_time > 0.1:  # 100ms threshold
        logger.warning(f"Slow query detected ({total_time:.3f}s): {statement}")

def setup_query_performance_monitoring(engine: Engine):
    """Attach event listeners to the SQLAlchemy engine."""
    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    event.listen(engine, "after_cursor_execute", after_cursor_execute)
    logger.info("Query performance monitoring is active.")