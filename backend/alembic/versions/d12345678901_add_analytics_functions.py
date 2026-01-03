"""add_analytics_functions

Revision ID: d12345678901
Revises: c12345678901
Create Date: 2025-12-28 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd12345678901'
down_revision: Union[str, Sequence[str], None] = 'c12345678901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create database functions for analytics."""
    
    # Function to calculate success rate for a user
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_user_success_rate(p_user_id VARCHAR)
        RETURNS NUMERIC AS $$
        DECLARE
            v_total INTEGER;
            v_successful INTEGER;
        BEGIN
            SELECT COUNT(*) INTO v_total
            FROM job_applications
            WHERE user_id = p_user_id;
            
            IF v_total = 0 THEN
                RETURN 0;
            END IF;
            
            SELECT COUNT(*) INTO v_successful
            FROM job_applications
            WHERE user_id = p_user_id
            AND status IN ('OFFER_RECEIVED', 'OFFER_ACCEPTED');
            
            RETURN ROUND((v_successful::NUMERIC / v_total::NUMERIC) * 100, 2);
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Function to calculate average response time for a user
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_avg_response_time(p_user_id VARCHAR)
        RETURNS NUMERIC AS $$
        DECLARE
            v_avg_days NUMERIC;
        BEGIN
            SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 86400)
            INTO v_avg_days
            FROM job_applications
            WHERE user_id = p_user_id
            AND status != 'DRAFT'
            AND updated_at IS NOT NULL
            AND created_at IS NOT NULL;
            
            RETURN COALESCE(ROUND(v_avg_days, 1), 0);
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Function to get interview conversion rate
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_interview_conversion_rate(p_user_id VARCHAR)
        RETURNS NUMERIC AS $$
        DECLARE
            v_interviews INTEGER;
            v_offers INTEGER;
        BEGIN
            SELECT COUNT(*) INTO v_interviews
            FROM job_applications
            WHERE user_id = p_user_id
            AND status IN ('INTERVIEW_SCHEDULED', 'INTERVIEW_COMPLETED', 'OFFER_RECEIVED', 'OFFER_ACCEPTED');
            
            IF v_interviews = 0 THEN
                RETURN 0;
            END IF;
            
            SELECT COUNT(*) INTO v_offers
            FROM job_applications
            WHERE user_id = p_user_id
            AND status IN ('OFFER_RECEIVED', 'OFFER_ACCEPTED');
            
            RETURN ROUND((v_offers::NUMERIC / v_interviews::NUMERIC) * 100, 2);
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Function to get top companies by success rate
    op.execute("""
        CREATE OR REPLACE FUNCTION get_top_companies_by_success(p_limit INTEGER DEFAULT 10)
        RETURNS TABLE(
            company_name VARCHAR,
            total_apps BIGINT,
            success_rate NUMERIC
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                a.company,
                COUNT(*) as total_apps,
                ROUND(
                    (COUNT(CASE WHEN a.status IN ('OFFER_RECEIVED', 'OFFER_ACCEPTED') THEN 1 END)::NUMERIC / 
                    COUNT(*)::NUMERIC) * 100, 
                    2
                ) as success_rate
            FROM job_applications a
            WHERE a.company IS NOT NULL
            GROUP BY a.company
            HAVING COUNT(*) >= 3
            ORDER BY success_rate DESC, total_apps DESC
            LIMIT p_limit;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Function to refresh materialized views
    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_analytics_views()
        RETURNS VOID AS $$
        BEGIN
            REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_application_stats;
            REFRESH MATERIALIZED VIEW CONCURRENTLY mv_company_stats;
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    """Remove database functions."""
    op.execute("DROP FUNCTION IF EXISTS refresh_analytics_views();")
    op.execute("DROP FUNCTION IF EXISTS get_top_companies_by_success(INTEGER);")
    op.execute("DROP FUNCTION IF EXISTS calculate_interview_conversion_rate(VARCHAR);")
    op.execute("DROP FUNCTION IF EXISTS calculate_avg_response_time(VARCHAR);")
    op.execute("DROP FUNCTION IF EXISTS calculate_user_success_rate(VARCHAR);")
