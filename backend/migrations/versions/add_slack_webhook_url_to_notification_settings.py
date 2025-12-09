"""Add slack_webhook_url to NotificationSettings

Revision ID: add_slack_webhook_url
Revises: add_test_case_features_202501
Create Date: 2025-01-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'add_slack_webhook_url'
down_revision = 'add_test_case_features_202501'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """테이블 존재 여부 확인"""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name, column_name):
    """컬럼 존재 여부 확인"""
    if not table_exists(table_name):
        return False
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    """slack_webhook_url 컬럼 추가"""
    if table_exists('NotificationSettings'):
        if not column_exists('NotificationSettings', 'slack_webhook_url'):
            with op.batch_alter_table('NotificationSettings', schema=None) as batch_op:
                batch_op.add_column(sa.Column('slack_webhook_url', sa.String(length=500), nullable=True))
            print("✅ slack_webhook_url 컬럼이 NotificationSettings 테이블에 추가되었습니다.")
        else:
            print("ℹ️ slack_webhook_url 컬럼이 이미 존재합니다.")
    else:
        print("⚠️ NotificationSettings 테이블이 존재하지 않습니다.")


def downgrade():
    """slack_webhook_url 컬럼 제거"""
    if table_exists('NotificationSettings'):
        if column_exists('NotificationSettings', 'slack_webhook_url'):
            with op.batch_alter_table('NotificationSettings', schema=None) as batch_op:
                batch_op.drop_column('slack_webhook_url')
            print("✅ slack_webhook_url 컬럼이 NotificationSettings 테이블에서 제거되었습니다.")
        else:
            print("ℹ️ slack_webhook_url 컬럼이 존재하지 않습니다.")
    else:
        print("⚠️ NotificationSettings 테이블이 존재하지 않습니다.")

