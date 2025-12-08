from datetime import datetime
from utils.timezone_utils import get_kst_now
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')  # admin, user, tester
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정 - 외래키 충돌 방지를 위해 명시적으로 설정
    created_test_cases = db.relationship('TestCase', foreign_keys='TestCase.creator_id', backref='creator', lazy='dynamic')
    assigned_test_cases = db.relationship('TestCase', foreign_keys='TestCase.assignee_id', backref='assignee', lazy='dynamic')
    automation_tests = db.relationship('AutomationTest', foreign_keys='AutomationTest.creator_id', backref='creator', lazy='dynamic')
    created_performance_tests = db.relationship('PerformanceTest', foreign_keys='PerformanceTest.creator_id', backref='creator', lazy='dynamic')
    assigned_performance_tests = db.relationship('PerformanceTest', foreign_keys='PerformanceTest.assignee_id', backref='assignee', lazy='dynamic')
    
    def set_password(self, password):
        """비밀번호 해시화"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """비밀번호 검증"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """사용자 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UserSession(db.Model):
    __tablename__ = 'UserSessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_kst_now)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', backref='sessions')

# 프로젝트 모델
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)

# 폴더 모델
class Folder(db.Model):
    __tablename__ = 'Folders'
    id = db.Column(db.Integer, primary_key=True)
    folder_name = db.Column(db.String(100), nullable=False)
    folder_type = db.Column(db.String(50), default='environment')
    environment = db.Column(db.String(50), default='dev')
    deployment_date = db.Column(db.Date, nullable=True)
    parent_folder_id = db.Column(db.Integer, db.ForeignKey('Folders.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=get_kst_now)

# 테스트 케이스 모델
class TestCase(db.Model):
    __tablename__ = 'TestCases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    test_type = db.Column(db.String(50))  # functional, performance, security
    priority = db.Column(db.String(20))  # low, medium, high, critical
    status = db.Column(db.String(20), default='draft')  # draft, active, inactive
    environment = db.Column(db.String(50))  # prod, staging, dev
    script_path = db.Column(db.String(500))  # 스크립트 경로
    folder_id = db.Column(db.Integer, db.ForeignKey('Folders.id'), nullable=True)  # 폴더 ID
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    creator_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # 프로젝트 ID
    
    # 추가 컬럼들
    main_category = db.Column(db.String(100))  # 메인 카테고리
    sub_category = db.Column(db.String(100))  # 서브 카테고리
    detail_category = db.Column(db.String(100))  # 상세 카테고리
    pre_condition = db.Column(db.Text)  # 사전 조건
    expected_result = db.Column(db.Text)  # 예상 결과
    remark = db.Column(db.Text)  # 비고
    automation_code_path = db.Column(db.String(500))  # 자동화 코드 경로
    automation_code_type = db.Column(db.String(50))  # 자동화 코드 타입
    result_status = db.Column(db.String(20), default='pending')  # pending, passed, failed, blocked
    
    # 관계 설정
    folder = db.relationship('Folder', backref='test_cases')
    project = db.relationship('Project', backref='test_cases')
    # creator와 assignee 관계는 User 모델의 backref로 처리됨

# 테스트 케이스 히스토리 모델
class TestCaseHistory(db.Model):
    """테스트 케이스 변경 히스토리"""
    __tablename__ = 'test_case_history'
    
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)  # 변경된 필드명
    old_value = db.Column(db.Text)  # 이전 값
    new_value = db.Column(db.Text)  # 새로운 값
    changed_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    change_type = db.Column(db.String(50), nullable=False)  # 'create', 'update', 'delete'
    
    # 관계 설정
    test_case = db.relationship('TestCase', backref='history')
    user = db.relationship('User', backref='test_case_changes')
    
    def __repr__(self):
        return f'<TestCaseHistory {self.field_name}: {self.old_value} -> {self.new_value}>'

# 성능 테스트 모델
class PerformanceTest(db.Model):
    __tablename__ = 'PerformanceTests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    test_type = db.Column(db.String(50))  # load, stress, spike, soak
    script_path = db.Column(db.String(255))
    environment = db.Column(db.String(50))
    parameters = db.Column(db.Text)  # JSON 형태로 저장
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    creator_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # 프로젝트 ID
    
    # 관계 설정
    project = db.relationship('Project', backref='performance_tests')
    # creator와 assignee 관계는 User 모델의 backref로 처리됨

# 자동화 테스트 모델
class AutomationTest(db.Model):
    __tablename__ = 'AutomationTests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    test_type = db.Column(db.String(50))  # functional, ui, api
    script_path = db.Column(db.String(255))
    environment = db.Column(db.String(50))
    parameters = db.Column(db.Text)  # JSON 형태로 저장
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    creator_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # 프로젝트 ID
    
    # 관계 설정
    project = db.relationship('Project', backref='automation_tests')
    # creator 관계는 User 모델의 backref로 처리됨

# 테스트 결과 모델
class TestResult(db.Model):
    __tablename__ = 'TestResults'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=True)  # nullable=True로 변경
    result = db.Column(db.String(20))  # Pass, Fail, Skip, Error
    execution_time = db.Column(db.Float)  # 초 단위
    environment = db.Column(db.String(50))
    executed_by = db.Column(db.String(100))
    executed_at = db.Column(db.DateTime, default=get_kst_now)
    notes = db.Column(db.Text)
    # test_case_id는 반드시 있어야 함 (실제 DB 스키마에 맞춤)
    __table_args__ = (
        db.CheckConstraint('test_case_id IS NOT NULL', name='check_test_reference'),
    )

# 대시보드 요약 모델
class DashboardSummary(db.Model):
    __tablename__ = 'DashboardSummaries'
    id = db.Column(db.Integer, primary_key=True)
    environment = db.Column(db.String(50), nullable=False)
    total_tests = db.Column(db.Integer, default=0)
    passed_tests = db.Column(db.Integer, default=0)
    failed_tests = db.Column(db.Integer, default=0)
    skipped_tests = db.Column(db.Integer, default=0)
    pass_rate = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=get_kst_now)

# 테스트 실행 기록 모델
class TestExecution(db.Model):
    __tablename__ = 'TestExecutions'
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(50))  # performance, automation, manual
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=True)
    automation_test_id = db.Column(db.Integer, db.ForeignKey('AutomationTests.id'), nullable=True)
    performance_test_id = db.Column(db.Integer, db.ForeignKey('PerformanceTests.id'), nullable=True)
    environment = db.Column(db.String(50))
    executed_by = db.Column(db.String(100))
    status = db.Column(db.String(20))  # running, completed, failed
    result_summary = db.Column(db.Text)  # JSON 형태로 저장
    started_at = db.Column(db.DateTime, default=get_kst_now)
    completed_at = db.Column(db.DateTime)

# 스크린샷 모델 (alpha DB 스키마에 맞춤)
class Screenshot(db.Model):
    __tablename__ = 'Screenshots'
    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey('TestResults.id'), nullable=False)  # alpha DB는 test_result_id 사용
    file_path = db.Column(db.String(500), nullable=False)  # alpha DB는 file_path 사용
    created_at = db.Column(db.DateTime, default=get_kst_now)  # alpha DB는 created_at 사용

# 테스트 케이스 템플릿 모델
class TestCaseTemplate(db.Model):
    """테스트 케이스 템플릿"""
    __tablename__ = 'test_case_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    main_category = db.Column(db.String(100))
    sub_category = db.Column(db.String(100))
    detail_category = db.Column(db.String(100))
    pre_condition = db.Column(db.Text)
    expected_result = db.Column(db.Text)
    test_steps = db.Column(db.Text)  # 단계별 테스트 절차
    automation_code_path = db.Column(db.String(500))
    automation_code_type = db.Column(db.String(50), default='playwright')
    tags = db.Column(db.Text)  # JSON 형태로 태그 저장
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)  # 공개 템플릿 여부
    usage_count = db.Column(db.Integer, default=0)  # 사용 횟수
    
    # 관계 설정
    creator = db.relationship('User', backref='created_templates')
    
    def __repr__(self):
        return f'<TestCaseTemplate {self.name}>'

# 테스트 계획 모델
class TestPlan(db.Model):
    """테스트 계획"""
    __tablename__ = 'test_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(50))
    environment = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='draft')  # draft, active, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    creator = db.relationship('User', backref='created_test_plans')
    test_cases = db.relationship('TestPlanTestCase', back_populates='test_plan')
    
    def __repr__(self):
        return f'<TestPlan {self.name}>'

# 테스트 계획과 테스트 케이스 연결 테이블
class TestPlanTestCase(db.Model):
    """테스트 계획과 테스트 케이스 연결"""
    __tablename__ = 'test_plan_test_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    test_plan_id = db.Column(db.Integer, db.ForeignKey('test_plans.id'), nullable=False)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=False)
    execution_order = db.Column(db.Integer, default=0)
    estimated_duration = db.Column(db.Integer)  # 분 단위
    assigned_to = db.Column(db.Integer, db.ForeignKey('Users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 관계 설정
    test_plan = db.relationship('TestPlan', back_populates='test_cases')
    test_case = db.relationship('TestCase')
    assignee = db.relationship('User')
    
    def __repr__(self):
        return f'<TestPlanTestCase {self.test_plan_id}:{self.test_case_id}>'

class JiraIssue(db.Model):
    """이슈를 저장하는 모델 (DB 기반)"""
    __tablename__ = 'JiraIssues'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_key = db.Column(db.String(20), nullable=False, unique=True)  # TEST-1
    project_key = db.Column(db.String(20), nullable=False, default='TEST')
    issue_type = db.Column(db.String(50), nullable=False)  # Bug, Task, Story, Epic
    status = db.Column(db.String(50), nullable=False, default='To Do')  # To Do, In Progress, Done
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Critical
    summary = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    assignee_email = db.Column(db.String(100))  # 담당자 이메일
    labels = db.Column(db.Text)  # JSON 형태로 저장
    reporter_email = db.Column(db.String(100), default='admin@example.com')
    # 테스트 케이스 연결 필드
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=True)
    automation_test_id = db.Column(db.Integer, db.ForeignKey('AutomationTests.id'), nullable=True)
    performance_test_id = db.Column(db.Integer, db.ForeignKey('PerformanceTests.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    test_case = db.relationship('TestCase', backref='jira_issues')
    automation_test = db.relationship('AutomationTest', backref='jira_issues')
    performance_test = db.relationship('PerformanceTest', backref='jira_issues')
    
    def to_dict(self):
        """이슈 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'issue_key': self.issue_key,
            'project_key': self.project_key,
            'issue_type': self.issue_type,
            'status': self.status,
            'priority': self.priority,
            'summary': self.summary,
            'description': self.description,
            'assignee_email': self.assignee_email,
            'labels': self.labels,
            'reporter_email': self.reporter_email,
            'test_case_id': self.test_case_id,
            'automation_test_id': self.automation_test_id,
            'performance_test_id': self.performance_test_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<JiraIssue {self.issue_key}>'

# 테스트 스케줄 모델
class TestSchedule(db.Model):
    """테스트 케이스 자동 실행 스케줄"""
    __tablename__ = 'TestSchedules'
    
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)  # 스케줄 이름
    description = db.Column(db.Text)  # 스케줄 설명
    
    # 스케줄 타입: 'daily', 'weekly', 'monthly', 'cron', 'on_event'
    schedule_type = db.Column(db.String(50), nullable=False, default='daily')
    # cron 표현식 또는 이벤트 타입
    schedule_expression = db.Column(db.String(200))  # 예: "0 9 * * *" (매일 9시)
    
    # 스케줄 상태
    enabled = db.Column(db.Boolean, default=True)
    active = db.Column(db.Boolean, default=True)  # 활성화 여부
    
    # 실행 정보
    next_run_at = db.Column(db.DateTime)  # 다음 실행 예정 시간
    last_run_at = db.Column(db.DateTime)  # 마지막 실행 시간
    last_run_status = db.Column(db.String(20))  # 'success', 'failed', 'running'
    last_run_result_id = db.Column(db.Integer, db.ForeignKey('TestResults.id'), nullable=True)
    
    # 실행 환경 및 파라미터
    environment = db.Column(db.String(50), default='dev')
    execution_parameters = db.Column(db.Text)  # JSON 형태로 저장
    
    # 생성자 및 메타 정보
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    test_case = db.relationship('TestCase', backref='schedules')
    creator = db.relationship('User', backref='created_schedules')
    last_run_result = db.relationship('TestResult', foreign_keys=[last_run_result_id])
    
    def to_dict(self):
        """스케줄 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'test_case_id': self.test_case_id,
            'test_case_name': self.test_case.name if self.test_case else None,
            'name': self.name,
            'description': self.description,
            'schedule_type': self.schedule_type,
            'schedule_expression': self.schedule_expression,
            'enabled': self.enabled,
            'active': self.active,
            'next_run_at': self.next_run_at.isoformat() if self.next_run_at else None,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'last_run_status': self.last_run_status,
            'environment': self.environment,
            'execution_parameters': self.execution_parameters,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TestSchedule {self.name} (Test Case: {self.test_case_id})>'

# 알림 모델
class Notification(db.Model):
    """사용자 알림"""
    __tablename__ = 'Notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    
    # 알림 타입: 'test_failed', 'test_completed', 'test_started', 'schedule_run', 'test_assigned', 'comment_added'
    notification_type = db.Column(db.String(50), nullable=False)
    
    # 알림 제목 및 내용
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # 관련 리소스 정보
    related_test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=True)
    related_automation_test_id = db.Column(db.Integer, db.ForeignKey('AutomationTests.id'), nullable=True)
    related_performance_test_id = db.Column(db.Integer, db.ForeignKey('PerformanceTests.id'), nullable=True)
    related_test_result_id = db.Column(db.Integer, db.ForeignKey('TestResults.id'), nullable=True)
    
    # 알림 상태
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # 알림 우선순위: 'low', 'medium', 'high', 'critical'
    priority = db.Column(db.String(20), default='medium')
    
    # 알림 채널: 'in_app', 'email', 'slack', 'all'
    channels = db.Column(db.String(100), default='in_app')  # JSON 형태로 저장 가능
    
    # 생성 시간
    created_at = db.Column(db.DateTime, default=get_kst_now)
    
    # 관계 설정
    user = db.relationship('User', backref='notifications')
    related_test_case = db.relationship('TestCase', foreign_keys=[related_test_case_id])
    related_automation_test = db.relationship('AutomationTest', foreign_keys=[related_automation_test_id])
    related_performance_test = db.relationship('PerformanceTest', foreign_keys=[related_performance_test_id])
    related_test_result = db.relationship('TestResult', foreign_keys=[related_test_result_id])
    
    def to_dict(self):
        """알림 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'related_test_case_id': self.related_test_case_id,
            'related_automation_test_id': self.related_automation_test_id,
            'related_performance_test_id': self.related_performance_test_id,
            'related_test_result_id': self.related_test_result_id,
            'read': self.read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'priority': self.priority,
            'channels': self.channels,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Notification {self.title} (User: {self.user_id})>'

# 알림 설정 모델
class NotificationSettings(db.Model):
    """사용자별 알림 설정"""
    __tablename__ = 'NotificationSettings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False, unique=True)
    
    # 알림 타입별 설정 (JSON 형태로 저장)
    # 예: {"test_failed": {"in_app": true, "email": true, "slack": false}, ...}
    settings = db.Column(db.Text, default='{}')  # JSON 형태
    
    # 전역 설정
    email_enabled = db.Column(db.Boolean, default=True)
    slack_enabled = db.Column(db.Boolean, default=False)
    in_app_enabled = db.Column(db.Boolean, default=True)
    
    # 업데이트 시간
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    user = db.relationship('User', backref='notification_settings')
    
    def to_dict(self):
        """알림 설정을 딕셔너리로 변환"""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'settings': json.loads(self.settings) if self.settings else {},
            'email_enabled': self.email_enabled,
            'slack_enabled': self.slack_enabled,
            'in_app_enabled': self.in_app_enabled,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<NotificationSettings (User: {self.user_id})>'

# CI/CD 통합 모델
class CICDIntegration(db.Model):
    """CI/CD 통합 설정"""
    __tablename__ = 'CICDIntegrations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 통합 이름
    integration_type = db.Column(db.String(50), nullable=False)  # 'github', 'jenkins', 'gitlab', 'custom'
    
    # 웹훅 설정
    webhook_url = db.Column(db.String(500))  # 외부로 전송할 웹훅 URL
    webhook_secret = db.Column(db.String(255))  # 웹훅 서명 검증용 시크릿
    
    # 통합별 설정 (JSON 형태로 저장)
    config = db.Column(db.Text)  # JSON 형태로 저장
    
    # 활성화 상태
    enabled = db.Column(db.Boolean, default=True)
    active = db.Column(db.Boolean, default=True)
    
    # 트리거 설정
    trigger_on_push = db.Column(db.Boolean, default=True)  # Push 이벤트 시 트리거
    trigger_on_pr = db.Column(db.Boolean, default=True)  # PR 이벤트 시 트리거
    trigger_on_tag = db.Column(db.Boolean, default=False)  # Tag 이벤트 시 트리거
    
    # 실행할 테스트 케이스 필터
    test_case_filter = db.Column(db.Text)  # JSON 형태: {"folder_ids": [1,2], "environments": ["dev"]}
    
    # 생성자 및 메타 정보
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    creator = db.relationship('User', backref='cicd_integrations')
    
    def to_dict(self):
        """통합 정보를 딕셔너리로 변환"""
        import json
        return {
            'id': self.id,
            'name': self.name,
            'integration_type': self.integration_type,
            'webhook_url': self.webhook_url,
            'config': json.loads(self.config) if self.config else {},
            'enabled': self.enabled,
            'active': self.active,
            'trigger_on_push': self.trigger_on_push,
            'trigger_on_pr': self.trigger_on_pr,
            'trigger_on_tag': self.trigger_on_tag,
            'test_case_filter': json.loads(self.test_case_filter) if self.test_case_filter else {},
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<CICDIntegration {self.name} ({self.integration_type})>'

# CI/CD 실행 기록 모델
class CICDExecution(db.Model):
    """CI/CD 통합 실행 기록"""
    __tablename__ = 'CICDExecutions'
    
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('CICDIntegrations.id'), nullable=False)
    
    # 트리거 정보
    trigger_type = db.Column(db.String(50))  # 'push', 'pull_request', 'tag', 'manual'
    trigger_source = db.Column(db.String(100))  # GitHub, Jenkins 등
    trigger_event = db.Column(db.Text)  # 원본 이벤트 데이터 (JSON)
    
    # 실행 정보
    status = db.Column(db.String(20), default='running')  # 'running', 'completed', 'failed', 'cancelled'
    started_at = db.Column(db.DateTime, default=get_kst_now)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # 실행된 테스트 정보
    executed_test_cases = db.Column(db.Text)  # JSON 형태로 저장
    test_results = db.Column(db.Text)  # JSON 형태로 저장
    
    # PR 정보 (GitHub의 경우)
    pr_number = db.Column(db.Integer, nullable=True)
    pr_url = db.Column(db.String(500), nullable=True)
    pr_comment_id = db.Column(db.String(100), nullable=True)  # PR 코멘트 ID
    
    # 에러 정보
    error_message = db.Column(db.Text, nullable=True)
    
    # 관계 설정
    integration = db.relationship('CICDIntegration', backref='executions')
    
    def to_dict(self):
        """실행 기록을 딕셔너리로 변환"""
        import json
        return {
            'id': self.id,
            'integration_id': self.integration_id,
            'integration_name': self.integration.name if self.integration else None,
            'trigger_type': self.trigger_type,
            'trigger_source': self.trigger_source,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'executed_test_cases': json.loads(self.executed_test_cases) if self.executed_test_cases else [],
            'test_results': json.loads(self.test_results) if self.test_results else {},
            'pr_number': self.pr_number,
            'pr_url': self.pr_url,
            'error_message': self.error_message
        }
    
    def __repr__(self):
        return f'<CICDExecution {self.trigger_type} (Status: {self.status})>'

# 테스트 데이터 세트 모델
class TestDataSet(db.Model):
    """테스트 데이터 세트"""
    __tablename__ = 'TestDataSets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 데이터 세트 이름
    description = db.Column(db.Text)  # 설명
    
    # 데이터 (JSON 형태로 저장)
    data = db.Column(db.Text, nullable=False)  # JSON 형태
    
    # 데이터 타입 및 구조
    data_type = db.Column(db.String(50), default='json')  # 'json', 'csv', 'xml'
    data_schema = db.Column(db.Text)  # 데이터 스키마 (JSON Schema)
    
    # 환경 및 버전 관리
    environment = db.Column(db.String(50), default='dev')  # dev, alpha, production
    version = db.Column(db.String(50), default='1.0')  # 버전 번호
    parent_version_id = db.Column(db.Integer, db.ForeignKey('TestDataSets.id'), nullable=True)  # 부모 버전
    
    # 데이터 마스킹 설정
    masking_enabled = db.Column(db.Boolean, default=False)  # 마스킹 활성화 여부
    masking_rules = db.Column(db.Text)  # 마스킹 규칙 (JSON 형태)
    
    # 태그 및 분류
    tags = db.Column(db.Text)  # JSON 형태로 저장
    
    # 사용 통계
    usage_count = db.Column(db.Integer, default=0)  # 사용 횟수
    last_used_at = db.Column(db.DateTime, nullable=True)  # 마지막 사용 시간
    
    # 생성자 및 메타 정보
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    creator = db.relationship('User', backref='created_test_data_sets')
    parent_version = db.relationship('TestDataSet', remote_side=[id], backref='child_versions')
    
    def to_dict(self):
        """데이터 세트 정보를 딕셔너리로 변환"""
        import json
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'data': json.loads(self.data) if self.data else {},
            'data_type': self.data_type,
            'data_schema': json.loads(self.data_schema) if self.data_schema else None,
            'environment': self.environment,
            'version': self.version,
            'parent_version_id': self.parent_version_id,
            'masking_enabled': self.masking_enabled,
            'masking_rules': json.loads(self.masking_rules) if self.masking_rules else {},
            'tags': json.loads(self.tags) if self.tags else [],
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_masked_data(self):
        """마스킹된 데이터 반환"""
        import json
        if not self.masking_enabled or not self.masking_rules:
            return json.loads(self.data) if self.data else {}
        
        data = json.loads(self.data) if self.data else {}
        masking_rules = json.loads(self.masking_rules) if self.masking_rules else {}
        
        # 마스킹 규칙 적용
        masked_data = self._apply_masking(data, masking_rules)
        return masked_data
    
    def _apply_masking(self, data, rules):
        """마스킹 규칙 적용"""
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                if key in rules:
                    rule = rules[key]
                    if rule.get('type') == 'mask':
                        masked[key] = self._mask_value(value, rule)
                    elif rule.get('type') == 'remove':
                        continue  # 필드 제거
                    else:
                        masked[key] = self._apply_masking(value, rules) if isinstance(value, (dict, list)) else value
                else:
                    masked[key] = self._apply_masking(value, rules) if isinstance(value, (dict, list)) else value
            return masked
        elif isinstance(data, list):
            return [self._apply_masking(item, rules) for item in data]
        else:
            return data
    
    def _mask_value(self, value, rule):
        """값 마스킹"""
        if not value:
            return value
        
        value_str = str(value)
        mask_char = rule.get('mask_char', '*')
        keep_length = rule.get('keep_length', 0)  # 앞뒤로 유지할 문자 수
        
        if len(value_str) <= keep_length * 2:
            return mask_char * len(value_str)
        
        if keep_length > 0:
            return value_str[:keep_length] + mask_char * (len(value_str) - keep_length * 2) + value_str[-keep_length:]
        else:
            return mask_char * len(value_str)
    
    def __repr__(self):
        return f'<TestDataSet {self.name} (v{self.version})>'

# 테스트 케이스와 데이터 세트 매핑 모델
class TestCaseDataMapping(db.Model):
    """테스트 케이스와 데이터 세트 매핑"""
    __tablename__ = 'TestCaseDataMappings'
    
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=False)
    data_set_id = db.Column(db.Integer, db.ForeignKey('TestDataSets.id'), nullable=False)
    
    # 필드 매핑 정보 (JSON 형태)
    # 예: {"username": "data.user.email", "password": "data.user.password"}
    field_mapping = db.Column(db.Text)  # JSON 형태
    
    # 우선순위 (여러 데이터 세트가 있을 경우)
    priority = db.Column(db.Integer, default=1)
    
    # 활성화 여부
    enabled = db.Column(db.Boolean, default=True)
    
    # 생성 시간
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    test_case = db.relationship('TestCase', backref='data_mappings')
    data_set = db.relationship('TestDataSet', backref='test_case_mappings')
    
    def to_dict(self):
        """매핑 정보를 딕셔너리로 변환"""
        import json
        return {
            'id': self.id,
            'test_case_id': self.test_case_id,
            'test_case_name': self.test_case.name if self.test_case else None,
            'data_set_id': self.data_set_id,
            'data_set_name': self.data_set.name if self.data_set else None,
            'field_mapping': json.loads(self.field_mapping) if self.field_mapping else {},
            'priority': self.priority,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TestCaseDataMapping TestCase:{self.test_case_id} -> DataSet:{self.data_set_id}>'

# 댓글 모델
class Comment(db.Model):
    """테스트 케이스, 테스트 결과 등에 대한 댓글"""
    __tablename__ = 'Comments'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 댓글이 달린 대상 (다형성 관계)
    entity_type = db.Column(db.String(50), nullable=False)  # 'test_case', 'test_result', 'test_plan', 'test_execution'
    entity_id = db.Column(db.Integer, nullable=False)  # 대상 엔티티의 ID
    
    # 댓글 내용
    content = db.Column(db.Text, nullable=False)
    
    # 부모 댓글 (대댓글 지원)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('Comments.id'), nullable=True)
    
    # 작성자
    author_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    
    # 상태
    is_edited = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 타임스탬프
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    author = db.relationship('User', backref='comments')
    parent_comment = db.relationship('Comment', remote_side=[id], backref='replies')
    
    def to_dict(self):
        """댓글 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'content': self.content,
            'parent_comment_id': self.parent_comment_id,
            'author_id': self.author_id,
            'author_name': self.author.username if self.author else None,
            'author_email': self.author.email if self.author else None,
            'is_edited': self.is_edited,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'replies_count': len(self.replies) if self.replies else 0
        }
    
    def __repr__(self):
        return f'<Comment {self.id} on {self.entity_type}:{self.entity_id}>'

# 멘션 모델
class Mention(db.Model):
    """댓글 또는 다른 컨텐츠에서 사용자 멘션"""
    __tablename__ = 'Mentions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 멘션이 포함된 컨텐츠
    entity_type = db.Column(db.String(50), nullable=False)  # 'comment', 'test_case', 'test_result'
    entity_id = db.Column(db.Integer, nullable=False)
    
    # 멘션된 사용자
    mentioned_user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    
    # 멘션 위치 (댓글의 경우)
    comment_id = db.Column(db.Integer, db.ForeignKey('Comments.id'), nullable=True)
    
    # 읽음 여부
    is_read = db.Column(db.Boolean, default=False)
    
    # 생성 시간
    created_at = db.Column(db.DateTime, default=get_kst_now)
    
    # 관계 설정
    mentioned_user = db.relationship('User', backref='mentions')
    comment = db.relationship('Comment', backref='mentions')
    
    def to_dict(self):
        """멘션 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'mentioned_user_id': self.mentioned_user_id,
            'mentioned_user_name': self.mentioned_user.username if self.mentioned_user else None,
            'comment_id': self.comment_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Mention User:{self.mentioned_user_id} in {self.entity_type}:{self.entity_id}>'

# 워크플로우 모델
class Workflow(db.Model):
    """테스트 케이스 워크플로우 정의"""
    __tablename__ = 'Workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # 워크플로우 타입
    workflow_type = db.Column(db.String(50), default='test_case')  # 'test_case', 'test_plan', 'test_execution'
    
    # 초기 상태
    initial_status = db.Column(db.String(50), nullable=False)
    
    # 활성화 여부
    is_active = db.Column(db.Boolean, default=True)
    
    # 프로젝트별 워크플로우
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    
    # 생성자
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    project = db.relationship('Project', backref='workflows')
    creator = db.relationship('User', backref='created_workflows')
    steps = db.relationship('WorkflowStep', backref='workflow', cascade='all, delete-orphan', order_by='WorkflowStep.order')
    
    def to_dict(self):
        """워크플로우 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'workflow_type': self.workflow_type,
            'initial_status': self.initial_status,
            'is_active': self.is_active,
            'project_id': self.project_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'steps': [step.to_dict() for step in self.steps] if self.steps else []
        }
    
    def __repr__(self):
        return f'<Workflow {self.name}>'

# 워크플로우 단계 모델
class WorkflowStep(db.Model):
    """워크플로우의 각 단계"""
    __tablename__ = 'WorkflowSteps'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('Workflows.id'), nullable=False)
    
    # 단계 정보
    name = db.Column(db.String(100), nullable=False)  # 상태 이름 (예: 'draft', 'review', 'approved')
    display_name = db.Column(db.String(200), nullable=False)  # 표시 이름
    description = db.Column(db.Text)
    
    # 순서
    order = db.Column(db.Integer, nullable=False)
    
    # 다음 단계로 이동 가능한 역할
    allowed_roles = db.Column(db.Text)  # JSON 형태로 저장 (예: ['admin', 'tester'])
    
    # 다음 단계로 이동 가능한 사용자 (선택적)
    allowed_user_ids = db.Column(db.Text)  # JSON 형태로 저장
    
    # 다음 단계 목록
    next_steps = db.Column(db.Text)  # JSON 형태로 저장 (예: ['review', 'approved'])
    
    # 자동 전환 조건
    auto_transition_condition = db.Column(db.Text)  # JSON 형태로 저장
    
    def to_dict(self):
        """워크플로우 단계 정보를 딕셔너리로 변환"""
        import json
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'order': self.order,
            'allowed_roles': json.loads(self.allowed_roles) if self.allowed_roles else [],
            'allowed_user_ids': json.loads(self.allowed_user_ids) if self.allowed_user_ids else [],
            'next_steps': json.loads(self.next_steps) if self.next_steps else [],
            'auto_transition_condition': json.loads(self.auto_transition_condition) if self.auto_transition_condition else None
        }
    
    def __repr__(self):
        return f'<WorkflowStep {self.name} (order: {self.order})>'

# 워크플로우 상태 모델
class WorkflowState(db.Model):
    """엔티티의 현재 워크플로우 상태"""
    __tablename__ = 'WorkflowStates'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 상태가 적용된 엔티티
    entity_type = db.Column(db.String(50), nullable=False)  # 'test_case', 'test_plan', 'test_execution'
    entity_id = db.Column(db.Integer, nullable=False)
    
    # 워크플로우 및 현재 단계
    workflow_id = db.Column(db.Integer, db.ForeignKey('Workflows.id'), nullable=False)
    current_step_id = db.Column(db.Integer, db.ForeignKey('WorkflowSteps.id'), nullable=True)
    current_status = db.Column(db.String(50), nullable=False)  # 현재 상태 이름
    
    # 상태 변경 이력
    previous_status = db.Column(db.String(50))
    
    # 상태 변경자
    changed_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    
    # 타임스탬프
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    workflow = db.relationship('Workflow', backref='states')
    current_step = db.relationship('WorkflowStep', backref='active_states')
    changer = db.relationship('User', backref='workflow_state_changes')
    
    def to_dict(self):
        """워크플로우 상태 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'workflow_id': self.workflow_id,
            'workflow_name': self.workflow.name if self.workflow else None,
            'current_step_id': self.current_step_id,
            'current_step_name': self.current_step.display_name if self.current_step else None,
            'current_status': self.current_status,
            'previous_status': self.previous_status,
            'changed_by': self.changed_by,
            'changer_name': self.changer.username if self.changer else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<WorkflowState {self.entity_type}:{self.entity_id} -> {self.current_status}>'

# 테스트 의존성 모델
class TestDependency(db.Model):
    """테스트 케이스 간 의존성"""
    __tablename__ = 'TestDependencies'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 의존성 관계
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=False)  # 의존하는 테스트 케이스
    depends_on_test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=False)  # 의존 대상 테스트 케이스
    
    # 의존성 타입
    dependency_type = db.Column(db.String(50), default='required')  # 'required', 'optional', 'blocking'
    
    # 의존성 조건
    condition = db.Column(db.Text)  # JSON 형태로 저장 (예: {"result": "Pass", "status": "completed"})
    
    # 우선순위 (같은 테스트 케이스에 여러 의존성이 있을 경우)
    priority = db.Column(db.Integer, default=1)
    
    # 활성화 여부
    enabled = db.Column(db.Boolean, default=True)
    
    # 생성 시간
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    test_case = db.relationship('TestCase', foreign_keys=[test_case_id], backref='dependencies')
    depends_on = db.relationship('TestCase', foreign_keys=[depends_on_test_case_id], backref='dependent_tests')
    
    def to_dict(self):
        """의존성 정보를 딕셔너리로 변환"""
        import json
        return {
            'id': self.id,
            'test_case_id': self.test_case_id,
            'test_case_name': self.test_case.name if self.test_case else None,
            'depends_on_test_case_id': self.depends_on_test_case_id,
            'depends_on_test_case_name': self.depends_on.name if self.depends_on else None,
            'dependency_type': self.dependency_type,
            'condition': json.loads(self.condition) if self.condition else None,
            'priority': self.priority,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TestDependency TestCase:{self.test_case_id} depends on TestCase:{self.depends_on_test_case_id}>'

# 커스텀 리포트 모델
class CustomReport(db.Model):
    """커스텀 리포트 정의"""
    __tablename__ = 'CustomReports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # 리포트 타입
    report_type = db.Column(db.String(50), default='test_execution')  # 'test_execution', 'test_coverage', 'trend', 'custom'
    
    # 리포트 설정 (JSON 형태)
    config = db.Column(db.Text, nullable=False)  # JSON 형태로 저장
    
    # 리포트 템플릿 (선택적)
    template = db.Column(db.Text)  # HTML 또는 마크다운 템플릿
    
    # 출력 형식
    output_format = db.Column(db.String(50), default='html')  # 'html', 'pdf', 'json', 'csv', 'excel'
    
    # 스케줄 설정
    schedule_enabled = db.Column(db.Boolean, default=False)
    schedule_expression = db.Column(db.String(200))  # cron 표현식
    
    # 필터 설정
    filters = db.Column(db.Text)  # JSON 형태로 저장
    
    # 공유 설정
    is_public = db.Column(db.Boolean, default=False)
    shared_with_user_ids = db.Column(db.Text)  # JSON 형태로 저장
    
    # 프로젝트
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    
    # 생성자
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    project = db.relationship('Project', backref='custom_reports')
    creator = db.relationship('User', backref='created_reports')
    
    def to_dict(self):
        """리포트 정보를 딕셔너리로 변환"""
        import json
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'report_type': self.report_type,
            'config': json.loads(self.config) if self.config else {},
            'template': self.template,
            'output_format': self.output_format,
            'schedule_enabled': self.schedule_enabled,
            'schedule_expression': self.schedule_expression,
            'filters': json.loads(self.filters) if self.filters else {},
            'is_public': self.is_public,
            'shared_with_user_ids': json.loads(self.shared_with_user_ids) if self.shared_with_user_ids else [],
            'project_id': self.project_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<CustomReport {self.name}>'

# 리포트 실행 기록 모델
class ReportExecution(db.Model):
    """리포트 실행 기록"""
    __tablename__ = 'ReportExecutions'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('CustomReports.id'), nullable=False)
    
    # 실행 정보
    status = db.Column(db.String(20), default='running')  # 'running', 'completed', 'failed'
    started_at = db.Column(db.DateTime, default=get_kst_now)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # 결과 파일 경로
    result_file_path = db.Column(db.String(500))
    
    # 실행 파라미터
    execution_params = db.Column(db.Text)  # JSON 형태로 저장
    
    # 오류 정보
    error_message = db.Column(db.Text)
    
    # 실행자
    executed_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    
    # 관계 설정
    report = db.relationship('CustomReport', backref='executions')
    executor = db.relationship('User', backref='executed_reports')
    
    def to_dict(self):
        """실행 기록 정보를 딕셔너리로 변환"""
        import json
        return {
            'id': self.id,
            'report_id': self.report_id,
            'report_name': self.report.name if self.report else None,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result_file_path': self.result_file_path,
            'execution_params': json.loads(self.execution_params) if self.execution_params else {},
            'error_message': self.error_message,
            'executed_by': self.executed_by,
            'executor_name': self.executor.username if self.executor else None
        }
    
    def __repr__(self):
        return f'<ReportExecution Report:{self.report_id} (Status: {self.status})>'

# 기존 JiraIntegration 모델은 호환성을 위해 유지 (deprecated)
class JiraIntegration(db.Model):
    """JIRA 연동 정보를 저장하는 모델 (deprecated - JiraIssue 사용 권장)"""
    __tablename__ = 'JiraIntegrations'
    
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=True)
    automation_test_id = db.Column(db.Integer, db.ForeignKey('AutomationTests.id'), nullable=True)
    performance_test_id = db.Column(db.Integer, db.ForeignKey('PerformanceTests.id'), nullable=True)
    jira_issue_key = db.Column(db.String(20), nullable=False)  # PROJECT-123
    jira_issue_id = db.Column(db.String(50), nullable=False)  # 내부 ID
    jira_project_key = db.Column(db.String(20), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)  # Bug, Task, Story, Epic
    status = db.Column(db.String(50), nullable=False)  # To Do, In Progress, Done
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Critical
    summary = db.Column(db.Text)
    description = db.Column(db.Text)
    assignee_account_id = db.Column(db.String(100))  # JIRA 사용자 계정 ID
    labels = db.Column(db.Text)  # JSON 형태로 저장
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    last_sync_at = db.Column(db.DateTime)  # 마지막 동기화 시간
    
    # 관계 설정
    test_case = db.relationship('TestCase', backref='jira_integrations')
    automation_test = db.relationship('AutomationTest', backref='jira_integrations')
    performance_test = db.relationship('PerformanceTest', backref='jira_integrations')
    
    def to_dict(self):
        """JIRA 연동 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'test_case_id': self.test_case_id,
            'automation_test_id': self.automation_test_id,
            'performance_test_id': self.performance_test_id,
            'jira_issue_key': self.jira_issue_key,
            'jira_issue_id': self.jira_issue_id,
            'jira_project_key': self.jira_project_key,
            'issue_type': self.issue_type,
            'status': self.status,
            'priority': self.priority,
            'summary': self.summary,
            'description': self.description,
            'assignee_account_id': self.assignee_account_id,
            'labels': self.labels,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None
        }
    
    def __repr__(self):
        return f'<JiraIntegration {self.jira_issue_key}>'


class JiraComment(db.Model):
    """JIRA 댓글을 저장하는 모델"""
    __tablename__ = 'JiraComments'
    
    id = db.Column(db.Integer, primary_key=True)
    jira_issue_id = db.Column(db.Integer, db.ForeignKey('JiraIssues.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)  # 댓글 내용
    author_email = db.Column(db.String(100), nullable=False)  # 작성자 이메일
    created_at = db.Column(db.DateTime, default=get_kst_now)
    updated_at = db.Column(db.DateTime, default=get_kst_now, onupdate=get_kst_now)
    
    # 관계 설정
    jira_issue = db.relationship('JiraIssue', backref='comments')
    
    def to_dict(self):
        """댓글 정보를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'body': self.body,
            'author_email': self.author_email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<JiraComment {self.id}: {self.body[:50]}...>'
