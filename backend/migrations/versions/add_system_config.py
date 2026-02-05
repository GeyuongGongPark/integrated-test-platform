"""add SystemConfig table for TC default prompt etc.

Revision ID: add_system_config
Revises: add_test_steps_to_testcases
Create Date: 2025-02-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'add_system_config'
down_revision = 'add_test_steps_testcases'
branch_labels = None
depends_on = None


def _system_config_table_exists():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = [t.lower() for t in inspector.get_table_names()]
    return 'systemconfig' in tables


def upgrade():
    if not _system_config_table_exists():
        op.create_table(
            'SystemConfig',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('key', sa.String(100), nullable=False),
            sa.Column('value', sa.Text(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('key')
        )


def downgrade():
    if _system_config_table_exists():
        op.drop_table('SystemConfig')
