"""Add test_steps to TestCases (for code-free Playwright execution)

Revision ID: add_test_steps_testcases
Revises: add_slack_webhook_url
Create Date: 2025-02-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'add_test_steps_testcases'
down_revision = 'add_slack_webhook_url'
branch_labels = None
depends_on = None


def table_exists(table_name):
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name, column_name):
    if not table_exists(table_name):
        return False
    bind = op.get_bind()
    inspector = inspect(bind)
    return column_name in [c['name'] for c in inspector.get_columns(table_name)]


def upgrade():
    if table_exists('TestCases') and not column_exists('TestCases', 'test_steps'):
        op.add_column('TestCases', sa.Column('test_steps', sa.Text(), nullable=True))


def downgrade():
    if table_exists('TestCases') and column_exists('TestCases', 'test_steps'):
        op.drop_column('TestCases', 'test_steps')
