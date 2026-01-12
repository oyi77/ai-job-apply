"""add_analytics_indexes

Revision ID: c12345678901
Revises: b12345678901
Create Date: 2025-12-28 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c12345678901'
down_revision: Union[str, Sequence[str], None] = 'b12345678901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes for analytics queries."""
    # Add index on created_at for time-based queries
    op.create_index(
        'ix_job_applications_created_at',
        'job_applications',
        ['created_at'],
        unique=False
    )
    
    # Add index on updated_at for response time analysis
    op.create_index(
        'ix_job_applications_updated_at',
        'job_applications',
        ['updated_at'],
        unique=False
    )
    
    # Add index on status for filtering
    op.create_index(
        'ix_job_applications_status',
        'job_applications',
        ['status'],
        unique=False
    )
    
    # Add composite index on user_id and created_at for user-specific queries
    op.create_index(
        'ix_job_applications_user_created',
        'job_applications',
        ['user_id', 'created_at'],
        unique=False
    )
    
    # Add composite index on user_id and status for filtering
    op.create_index(
        'ix_job_applications_user_status',
        'job_applications',
        ['user_id', 'status'],
        unique=False
    )
    
    # Add index on company for company analysis
    op.create_index(
        'ix_job_applications_company',
        'job_applications',
        ['company'],
        unique=False
    )


def downgrade() -> None:
    """Remove analytics indexes."""
    op.drop_index('ix_job_applications_company', table_name='job_applications')
    op.drop_index('ix_job_applications_user_status', table_name='job_applications')
    op.drop_index('ix_job_applications_user_created', table_name='job_applications')
    op.drop_index('ix_job_applications_status', table_name='job_applications')
    op.drop_index('ix_job_applications_updated_at', table_name='job_applications')
    op.drop_index('ix_job_applications_created_at', table_name='job_applications')
