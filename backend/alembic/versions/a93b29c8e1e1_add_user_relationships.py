"""add_user_relationships

Revision ID: a93b29c8e1e1
Revises: 47efb524293a
Create Date: 2025-12-28 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a93b29c8e1e1'
down_revision: Union[str, Sequence[str], None] = '47efb524293a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check current tables
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    
    # 1. Update job_searches table
    if 'job_searches' in tables:
        columns = [col['name'] for col in inspector.get_columns('job_searches')]
        if 'user_id' not in columns:
            with op.batch_alter_table('job_searches', schema=None) as batch_op:
                batch_op.add_column(sa.Column('user_id', sa.String(), nullable=True))
                batch_op.create_foreign_key('fk_job_searches_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')
                batch_op.create_index('idx_job_search_user_id', ['user_id'], unique=False)

    # 2. Update file_metadata table
    if 'file_metadata' in tables:
        columns = [col['name'] for col in inspector.get_columns('file_metadata')]
        if 'user_id' not in columns:
            with op.batch_alter_table('file_metadata', schema=None) as batch_op:
                batch_op.add_column(sa.Column('user_id', sa.String(), nullable=True))
                batch_op.create_foreign_key('fk_file_metadata_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')
                batch_op.create_index('idx_file_metadata_user_id', ['user_id'], unique=False)

    # 3. Update ai_activities table (add foreign key to existing user_id)
    if 'ai_activities' in tables:
        fks = inspector.get_foreign_keys('ai_activities')
        fk_names = [fk.get('name') for fk in fks if fk.get('name')]
        if 'fk_ai_activities_user_id' not in fk_names:
            with op.batch_alter_table('ai_activities', schema=None) as batch_op:
                batch_op.create_foreign_key('fk_ai_activities_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    # Downgrade ai_activities
    with op.batch_alter_table('ai_activities', schema=None) as batch_op:
        batch_op.drop_constraint('fk_ai_activities_user_id', type_='foreignkey')

    # Downgrade file_metadata
    with op.batch_alter_table('file_metadata', schema=None) as batch_op:
        batch_op.drop_index('idx_file_metadata_user_id')
        batch_op.drop_constraint('fk_file_metadata_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    # Downgrade job_searches
    with op.batch_alter_table('job_searches', schema=None) as batch_op:
        batch_op.drop_index('idx_job_search_user_id')
        batch_op.drop_constraint('fk_job_searches_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')
