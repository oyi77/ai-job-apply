"""Add failure_logs table for error tracking with screenshot capture.

Revision ID: add_failure_logs
Revises: 001
Create Date: 2026-01-29

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# import revision identifier to avoid issues
from alembic.config import Config

# Set meta data
revision = "001_add_failure_logs"
down_revision = None  # Will be set by Alembic
branch_labels = None


def upgrade() -> None:
    """Upgrade: Create failure_logs table."""
    # Create table with indexes
    op.create_table(
        "failure_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("task_name", sa.String(), nullable=False, index=True),
        sa.Column("platform", sa.String(), nullable=False, index=True),
        sa.Column("error_type", sa.String(), nullable=False, index=True),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        sa.Column("screenshot", sa.Text(), nullable=True),  # Base64 encoded image
        sa.Column("job_id", sa.String(), nullable=True, index=True),
        sa.Column("application_id", sa.String(), nullable=True, index=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )

    # Create indexes for performance
    op.create_index("idx_failure_user_task", "failure_logs", ["user_id", "task_name"])
    op.create_index("idx_failure_platform", "failure_logs", ["platform"])
    op.create_index("idx_failure_error_type", "failure_logs", ["error_type"])
    op.create_index("idx_failure_created", "failure_logs", ["created_at"])
    op.create_index("idx_failure_job_id", "failure_logs", ["job_id"])
    op.create_index("idx_failure_application_id", "failure_logs", ["application_id"])

    # Add foreign key constraint to users table
    op.create_foreign_key("failure_logs", "user_id", "users", "id", ondelete="CASCADE")


def downgrade() -> None:
    """Downgrade: Drop failure_logs table."""
    op.drop_index("idx_failure_application_id", "failure_logs")
    op.drop_index("idx_failure_job_id", "failure_logs")
    op.drop_index("idx_failure_created", "failure_logs")
    op.drop_index("idx_failure_error_type", "failure_logs")
    op.drop_index("idx_failure_platform", "failure_logs")
    op.drop_index("idx_failure_user_task", "failure_logs")
    op.drop_foreign_key("failure_logs", "user_id", "users")
    op.drop_table("failure_logs")
