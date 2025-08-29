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
    performance_tests = db.relationship('PerformanceTest', foreign_keys='PerformanceTest.creator_id', backref='creator', lazy='dynamic')
    
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
    # creator와 assignee 관계는 User 모델에서 이미 설정됨

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
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # 프로젝트 ID
    
    # 관계 설정
    project = db.relationship('Project', backref='performance_tests')

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
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # 프로젝트 ID
    
    # 관계 설정
    project = db.relationship('Project', backref='automation_tests')

# 테스트 결과 모델
class TestResult(db.Model):
    __tablename__ = 'TestResults'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=True)  # nullable=True로 변경
    automation_test_id = db.Column(db.Integer, db.ForeignKey('AutomationTests.id'), nullable=True)  # 자동화 테스트 ID 추가
    performance_test_id = db.Column(db.Integer, db.ForeignKey('PerformanceTests.id'), nullable=True)  # 성능 테스트 ID 추가
    result = db.Column(db.String(20))  # Pass, Fail, Skip, Error
    status = db.Column(db.String(20))  # Pass, Fail, N/T, N/A, Block (코드와 일치)
    execution_time = db.Column(db.Float)  # 초 단위
    environment = db.Column(db.String(50))
    executed_by = db.Column(db.String(100))
    executed_at = db.Column(db.DateTime, default=get_kst_now)
    notes = db.Column(db.Text)
    result_data = db.Column(db.Text)  # 결과 데이터 저장용
    
    # test_case_id, automation_test_id, performance_test_id 중 하나는 반드시 있어야 함
    __table_args__ = (
        db.CheckConstraint('test_case_id IS NOT NULL OR automation_test_id IS NOT NULL OR performance_test_id IS NOT NULL', name='check_test_reference'),
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
