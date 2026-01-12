"""add_analytics_mvs

Revision ID: e12345678901
Revises: d12345678901
Create Date: 2025-12-28 12:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e12345678901'
down_revision: Union[str, Sequence[str], None] = 'd12345678901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create materialized views for analytics."""
    
    # Materialized view for user application statistics
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_user_application_stats AS
        SELECT 
            user_id,
            COUNT(*) as total_applications,
            COUNT(CASE WHEN status IN ('OFFER_RECEIVED', 'OFFER_ACCEPTED') THEN 1 END) as successful_applications,
            COUNT(CASE WHEN status IN ('INTERVIEW_SCHEDULED', 'INTERVIEW_COMPLETED', 'OFFER_RECEIVED', 'OFFER_ACCEPTED') THEN 1 END) as interviews,
            COUNT(CASE WHEN status = 'REJECTED' THEN 1 END) as rejections,
            ROUND(
                CAST(COUNT(CASE WHEN status IN ('OFFER_RECEIVED', 'OFFER_ACCEPTED') THEN 1 END) AS FLOAT) / 
                NULLIF(COUNT(*), 0) * 100, 
                2
            ) as success_rate,
            MAX(updated_at) as last_updated
        FROM job_applications
        GROUP BY user_id;
    """)
    
    # Create index on materialized view
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_user_stats_user_id 
        ON mv_user_application_stats(user_id);
    """)
    
    # Materialized view for company statistics
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_company_stats AS
        SELECT 
            company,
            COUNT(*) as total_applications,
            COUNT(DISTINCT user_id) as unique_applicants,
            COUNT(CASE WHEN status IN ('INTERVIEW_SCHEDULED', 'INTERVIEW_COMPLETED', 'OFFER_RECEIVED', 'OFFER_ACCEPTED') THEN 1 END) as interviews,
            COUNT(CASE WHEN status IN ('OFFER_RECEIVED', 'OFFER_ACCEPTED') THEN 1 END) as offers,
            ROUND(
                CAST(COUNT(CASE WHEN status IN ('OFFER_RECEIVED', 'OFFER_ACCEPTED') THEN 1 END) AS FLOAT) / 
                NULLIF(COUNT(*), 0) * 100, 
                2
            ) as success_rate,
            AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 86400) as avg_response_days
        FROM job_applications
        WHERE company IS NOT NULL
        GROUP BY company
        HAVING COUNT(*) >= 3;
    """)
    
    # Create index on company materialized view
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_mv_company_stats_name 
        ON mv_company_stats(company);
    """)


def downgrade() -> None:
    """Remove materialized views."""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_company_stats;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_user_application_stats;")
