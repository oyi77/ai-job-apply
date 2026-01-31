"""merge_branches

Revision ID: 4c0fcbbc115f
Revises: 001_add_failure_logs, 0fb9d7724c92
Create Date: 2026-01-31 15:30:19.070075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c0fcbbc115f'
down_revision: Union[str, Sequence[str], None] = ('001_add_failure_logs', '0fb9d7724c92')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
