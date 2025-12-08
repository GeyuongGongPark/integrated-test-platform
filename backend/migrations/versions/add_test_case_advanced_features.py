"""Add test case advanced features

Revision ID: add_test_case_features_202501
Revises: 354e4022d50d
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_test_case_features_202501'
down_revision = '354e4022d50d'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """테이블 존재 여부 확인"""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name, column_name):
    """컬럼 존재 여부 확인"""
    bind = op.get_bind()
    inspector = inspect(bind)
    if not table_exists(table_name):
        return False
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def index_exists(table_name, index_name):
    """인덱스 존재 여부 확인"""
    bind = op.get_bind()
    inspector = inspect(bind)
    if not table_exists(table_name):
        return False
    indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
    return index_name in indexes


def upgrade():
    # 1. test_case_history 테이블 생성
    if not table_exists('test_case_history'):
        op.create_table('test_case_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('test_case_id', sa.Integer(), nullable=False),
            sa.Column('field_name', sa.String(length=100), nullable=False),
            sa.Column('old_value', sa.Text(), nullable=True),
            sa.Column('new_value', sa.Text(), nullable=True),
            sa.Column('changed_by', sa.Integer(), nullable=False),
            sa.Column('changed_at', sa.DateTime(), nullable=False),
            sa.Column('change_type', sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['test_case_id'], ['TestCases.id'], name='test_case_history_ibfk_1'),
            sa.ForeignKeyConstraint(['changed_by'], ['Users.id'], name='test_case_history_ibfk_2')
        )
        op.create_index('idx_test_case_history_test_case_id', 'test_case_history', ['test_case_id'])
        op.create_index('idx_test_case_history_changed_at', 'test_case_history', ['changed_at'])
        op.create_index('idx_test_case_history_changed_by', 'test_case_history', ['changed_by'])

    # 2. test_case_templates 테이블 생성
    if not table_exists('test_case_templates'):
        op.create_table('test_case_templates',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('main_category', sa.String(length=100), nullable=True),
            sa.Column('sub_category', sa.String(length=100), nullable=True),
            sa.Column('detail_category', sa.String(length=100), nullable=True),
            sa.Column('pre_condition', sa.Text(), nullable=True),
            sa.Column('expected_result', sa.Text(), nullable=True),
            sa.Column('test_steps', sa.Text(), nullable=True),
            sa.Column('automation_code_path', sa.String(length=500), nullable=True),
            sa.Column('automation_code_type', sa.String(length=50), nullable=True, server_default='playwright'),
            sa.Column('tags', sa.Text(), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('is_public', sa.Boolean(), nullable=True, server_default='0'),
            sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['created_by'], ['Users.id'], name='test_case_templates_ibfk_1')
        )
        if not index_exists('test_case_templates', 'idx_templates_created_by'):
            op.create_index('idx_templates_created_by', 'test_case_templates', ['created_by'])
        if not index_exists('test_case_templates', 'idx_templates_is_public'):
            op.create_index('idx_templates_is_public', 'test_case_templates', ['is_public'])

    # 3. test_plans 테이블 생성
    if not table_exists('test_plans'):
        op.create_table('test_plans',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('version', sa.String(length=50), nullable=True),
            sa.Column('environment', sa.String(length=50), nullable=True),
            sa.Column('start_date', sa.Date(), nullable=True),
            sa.Column('end_date', sa.Date(), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True, server_default='draft'),
            sa.Column('priority', sa.String(length=20), nullable=True, server_default='medium'),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['created_by'], ['Users.id'], name='test_plans_ibfk_1')
        )
        if not index_exists('test_plans', 'idx_test_plans_created_by'):
            op.create_index('idx_test_plans_created_by', 'test_plans', ['created_by'])
        if not index_exists('test_plans', 'idx_test_plans_status'):
            op.create_index('idx_test_plans_status', 'test_plans', ['status'])
        if not index_exists('test_plans', 'idx_test_plans_environment'):
            op.create_index('idx_test_plans_environment', 'test_plans', ['environment'])

    # 4. test_plan_test_cases 테이블 생성
    if not table_exists('test_plan_test_cases'):
        op.create_table('test_plan_test_cases',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('test_plan_id', sa.Integer(), nullable=False),
            sa.Column('test_case_id', sa.Integer(), nullable=False),
            sa.Column('execution_order', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('estimated_duration', sa.Integer(), nullable=True),
            sa.Column('assigned_to', sa.Integer(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['test_plan_id'], ['test_plans.id'], name='test_plan_test_cases_ibfk_1'),
            sa.ForeignKeyConstraint(['test_case_id'], ['TestCases.id'], name='test_plan_test_cases_ibfk_2'),
            sa.ForeignKeyConstraint(['assigned_to'], ['Users.id'], name='test_plan_test_cases_ibfk_3')
        )
        if not index_exists('test_plan_test_cases', 'idx_plan_test_cases_plan_id'):
            op.create_index('idx_plan_test_cases_plan_id', 'test_plan_test_cases', ['test_plan_id'])
        if not index_exists('test_plan_test_cases', 'idx_plan_test_cases_case_id'):
            op.create_index('idx_plan_test_cases_case_id', 'test_plan_test_cases', ['test_case_id'])
        if not index_exists('test_plan_test_cases', 'idx_plan_test_cases_assigned'):
            op.create_index('idx_plan_test_cases_assigned', 'test_plan_test_cases', ['assigned_to'])

    # 5. TestResults 테이블에 필드 추가
    if table_exists('TestResults'):
        with op.batch_alter_table('TestResults', schema=None) as batch_op:
            # automation_test_id 추가
            if not column_exists('TestResults', 'automation_test_id'):
                batch_op.add_column(sa.Column('automation_test_id', sa.Integer(), nullable=True))
                # 외래키는 별도로 추가 (테이블이 존재하는 경우에만)
                if table_exists('AutomationTests'):
                    try:
                        batch_op.create_foreign_key('fk_testresults_automation_test', 'AutomationTests', ['automation_test_id'], ['id'])
                    except Exception:
                        pass  # 외래키가 이미 존재할 수 있음
            
            # performance_test_id 추가
            if not column_exists('TestResults', 'performance_test_id'):
                batch_op.add_column(sa.Column('performance_test_id', sa.Integer(), nullable=True))
                # 외래키는 별도로 추가 (테이블이 존재하는 경우에만)
                if table_exists('PerformanceTests'):
                    try:
                        batch_op.create_foreign_key('fk_testresults_performance_test', 'PerformanceTests', ['performance_test_id'], ['id'])
                    except Exception:
                        pass  # 외래키가 이미 존재할 수 있음
            
            # execution_duration 추가
            if not column_exists('TestResults', 'execution_duration'):
                batch_op.add_column(sa.Column('execution_duration', sa.Float(), nullable=True))
            
            # error_message 추가
            if not column_exists('TestResults', 'error_message'):
                batch_op.add_column(sa.Column('error_message', sa.Text(), nullable=True))

    # 6. TestCases 테이블에 assignee_id 컬럼 추가
    if table_exists('TestCases'):
        with op.batch_alter_table('TestCases', schema=None) as batch_op:
            # assignee_id 컬럼 추가 (존재하지 않는 경우에만)
            if not column_exists('TestCases', 'assignee_id'):
                batch_op.add_column(sa.Column('assignee_id', sa.Integer(), nullable=True))
                # 외래키 추가 (Users 테이블이 존재하는 경우에만)
                if table_exists('Users'):
                    try:
                        batch_op.create_foreign_key('fk_testcases_assignee', 'Users', ['assignee_id'], ['id'])
                    except Exception:
                        pass  # 외래키가 이미 존재할 수 있음
    
    # 7. 인덱스 추가 (성능 최적화)
    if table_exists('TestCases'):
        with op.batch_alter_table('TestCases', schema=None) as batch_op:
            # environment 인덱스
            if column_exists('TestCases', 'environment') and not index_exists('TestCases', 'idx_testcases_environment'):
                batch_op.create_index('idx_testcases_environment', ['environment'])
            
            # result_status 인덱스
            if column_exists('TestCases', 'result_status') and not index_exists('TestCases', 'idx_testcases_result_status'):
                batch_op.create_index('idx_testcases_result_status', ['result_status'])
            
            # folder_id 인덱스
            if column_exists('TestCases', 'folder_id') and not index_exists('TestCases', 'idx_testcases_folder_id'):
                batch_op.create_index('idx_testcases_folder_id', ['folder_id'])
            
            # creator_id 인덱스
            if column_exists('TestCases', 'creator_id') and not index_exists('TestCases', 'idx_testcases_creator_id'):
                batch_op.create_index('idx_testcases_creator_id', ['creator_id'])
            
            # assignee_id 인덱스 (컬럼이 존재하는 경우에만)
            if column_exists('TestCases', 'assignee_id') and not index_exists('TestCases', 'idx_testcases_assignee_id'):
                batch_op.create_index('idx_testcases_assignee_id', ['assignee_id'])

    if table_exists('TestResults'):
        with op.batch_alter_table('TestResults', schema=None) as batch_op:
            # executed_at 인덱스
            if column_exists('TestResults', 'executed_at') and not index_exists('TestResults', 'idx_testresults_executed_at'):
                batch_op.create_index('idx_testresults_executed_at', ['executed_at'])
            
            # environment 인덱스
            if column_exists('TestResults', 'environment') and not index_exists('TestResults', 'idx_testresults_environment'):
                batch_op.create_index('idx_testresults_environment', ['environment'])
            
            # result 인덱스
            if column_exists('TestResults', 'result') and not index_exists('TestResults', 'idx_testresults_result'):
                batch_op.create_index('idx_testresults_result', ['result'])


def downgrade():
    # 인덱스 제거
    if table_exists('TestResults'):
        with op.batch_alter_table('TestResults', schema=None) as batch_op:
            if index_exists('TestResults', 'idx_testresults_result'):
                batch_op.drop_index('idx_testresults_result')
            if index_exists('TestResults', 'idx_testresults_environment'):
                batch_op.drop_index('idx_testresults_environment')
            if index_exists('TestResults', 'idx_testresults_executed_at'):
                batch_op.drop_index('idx_testresults_executed_at')

    if table_exists('TestCases'):
        with op.batch_alter_table('TestCases', schema=None) as batch_op:
            if index_exists('TestCases', 'idx_testcases_assignee_id'):
                batch_op.drop_index('idx_testcases_assignee_id')
            if index_exists('TestCases', 'idx_testcases_creator_id'):
                batch_op.drop_index('idx_testcases_creator_id')
            if index_exists('TestCases', 'idx_testcases_folder_id'):
                batch_op.drop_index('idx_testcases_folder_id')
            if index_exists('TestCases', 'idx_testcases_result_status'):
                batch_op.drop_index('idx_testcases_result_status')
            if index_exists('TestCases', 'idx_testcases_environment'):
                batch_op.drop_index('idx_testcases_environment')
            
            # assignee_id 컬럼 제거
            if column_exists('TestCases', 'assignee_id'):
                try:
                    batch_op.drop_constraint('fk_testcases_assignee', type_='foreignkey')
                except:
                    pass
                batch_op.drop_column('assignee_id')

    # TestResults 테이블 필드 제거
    if table_exists('TestResults'):
        with op.batch_alter_table('TestResults', schema=None) as batch_op:
            if column_exists('TestResults', 'error_message'):
                batch_op.drop_column('error_message')
            if column_exists('TestResults', 'execution_duration'):
                batch_op.drop_column('execution_duration')
            if column_exists('TestResults', 'performance_test_id'):
                try:
                    batch_op.drop_constraint('fk_testresults_performance_test', type_='foreignkey')
                except:
                    pass
                batch_op.drop_column('performance_test_id')
            if column_exists('TestResults', 'automation_test_id'):
                try:
                    batch_op.drop_constraint('fk_testresults_automation_test', type_='foreignkey')
                except:
                    pass
                batch_op.drop_column('automation_test_id')

    # 테이블 제거
    if table_exists('test_plan_test_cases'):
        op.drop_table('test_plan_test_cases')
    
    if table_exists('test_plans'):
        op.drop_table('test_plans')
    
    if table_exists('test_case_templates'):
        op.drop_table('test_case_templates')
    
    if table_exists('test_case_history'):
        op.drop_table('test_case_history')
