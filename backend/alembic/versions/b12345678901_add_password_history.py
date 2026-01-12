"""add_password_history

Revision ID: b12345678901
Revises: a93b29c8e1e1
Create Date: 2025-12-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b12345678901'
down_revision: Union[str, Sequence[str], None] = 'a93b29c8e1e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create password history table."""
    op.create_table(
        'password_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_password_history_user_id'), 'password_history', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop password history table."""
    op.drop_index(op.f('ix_password_history_user_id'), table_name='password_history')
    op.drop_table('password_history')
