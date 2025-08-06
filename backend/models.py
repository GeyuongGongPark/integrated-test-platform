from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

# 사용자 모델
class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='User')  # Administrator, User, Guest
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """비밀번호를 해시화하여 저장"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """비밀번호 검증"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def has_permission(self, permission):
        """사용자의 권한을 확인하는 메서드"""
        if self.role == 'Administrator':
            return True  # Administrator는 모든 권한을 가짐
        elif self.role == 'User':
            # User는 삭제 권한을 제외한 모든 권한을 가짐
            return permission != 'delete'
        elif self.role == 'Guest':
            # Guest는 view 권한만 가짐
            return permission == 'view'
        return False

# 기존 TCM 모델들
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class TestCase(db.Model):
    __tablename__ = 'TestCases'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    main_category = db.Column(db.String(255), nullable=False)  # 대분류
    sub_category = db.Column(db.String(255), nullable=False)   # 중분류
    detail_category = db.Column(db.String(255), nullable=False) # 소분류
    pre_condition = db.Column(db.Text)                         # 사전조건
    expected_result = db.Column(db.Text)                       # 기대결과
    remark = db.Column(db.Text)                               # 비고
    result_status = db.Column(db.String(10), default='N/T')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # 기존 필드들 (선택사항)
    environment = db.Column(db.String(50), default='dev')  # dev, alpha, production
    deployment_date = db.Column(db.Date)  # 배포일자
    folder_id = db.Column(db.Integer, db.ForeignKey('Folders.id'), nullable=True)
    automation_code_path = db.Column(db.String(512))  # 자동화 코드 경로
    automation_code_type = db.Column(db.String(50))  # selenium, playwright, k6 등

class TestResult(db.Model):
    __tablename__ = 'test_result'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'))
    result = db.Column(db.String(10))
    executed_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    notes = db.Column(db.Text)
    screenshot = db.Column(db.String(255))
    # 새로운 필드들 추가
    environment = db.Column(db.String(50), default='dev')  # dev, alpha, production
    execution_duration = db.Column(db.Float)  # 실행 시간 (초)
    error_message = db.Column(db.Text)  # 오류 메시지

class Folder(db.Model):
    __tablename__ = 'Folders'
    id = db.Column(db.Integer, primary_key=True)
    folder_name = db.Column(db.String(255), nullable=False)
    parent_folder_id = db.Column(db.Integer, db.ForeignKey('Folders.id'), nullable=True)
    # 새로운 필드들 추가
    folder_type = db.Column(db.String(50), default='environment')  # environment, deployment_date
    environment = db.Column(db.String(50))  # dev, alpha, production
    deployment_date = db.Column(db.Date)  # 배포일자
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Screenshot(db.Model):
    __tablename__ = 'Screenshots'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id', ondelete='CASCADE'))
    screenshot_path = db.Column(db.String(512), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 새로운 성능 테스트 모델들
class PerformanceTest(db.Model):
    __tablename__ = 'PerformanceTests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    k6_script_path = db.Column(db.String(512), nullable=False)
    environment = db.Column(db.String(100), default='prod')
    parameters = db.Column(db.Text)  # JSON 문자열로 저장
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PerformanceTestResult(db.Model):
    __tablename__ = 'PerformanceTestResults'
    id = db.Column(db.Integer, primary_key=True)
    performance_test_id = db.Column(db.Integer, db.ForeignKey('PerformanceTests.id'))
    execution_time = db.Column(db.DateTime, default=datetime.utcnow)
    response_time_avg = db.Column(db.Float)
    response_time_p95 = db.Column(db.Float)
    throughput = db.Column(db.Float)
    error_rate = db.Column(db.Float)
    status = db.Column(db.String(20))  # Pass, Fail, Running
    report_path = db.Column(db.String(512))
    result_data = db.Column(db.Text)  # JSON 문자열로 저장

class TestExecution(db.Model):
    __tablename__ = 'TestExecutions'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=True)
    performance_test_id = db.Column(db.Integer, db.ForeignKey('PerformanceTests.id'), nullable=True)
    test_type = db.Column(db.String(50))  # 'ui', 'performance'
    execution_start = db.Column(db.DateTime, default=datetime.utcnow)
    execution_end = db.Column(db.DateTime)
    status = db.Column(db.String(20))  # Running, Pass, Fail, Error
    result_data = db.Column(db.Text)  # JSON 문자열로 저장
    report_path = db.Column(db.String(512))

# 새로운 대시보드 요약 모델
class DashboardSummary(db.Model):
    __tablename__ = 'DashboardSummaries'
    id = db.Column(db.Integer, primary_key=True)
    environment = db.Column(db.String(50), nullable=False)  # dev, alpha, production
    total_tests = db.Column(db.Integer, default=0)
    passed_tests = db.Column(db.Integer, default=0)
    failed_tests = db.Column(db.Integer, default=0)
    skipped_tests = db.Column(db.Integer, default=0)
    pass_rate = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class AutomationTest(db.Model):
    __tablename__ = 'AutomationTests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    test_type = db.Column(db.String(50), nullable=False)  # selenium, playwright, cypress, puppeteer
    script_path = db.Column(db.String(512), nullable=False)
    environment = db.Column(db.String(50), default='dev')
    parameters = db.Column(db.Text)  # JSON 문자열로 저장
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AutomationTestResult(db.Model):
    __tablename__ = 'AutomationTestResults'
    id = db.Column(db.Integer, primary_key=True)
    automation_test_id = db.Column(db.Integer, db.ForeignKey('AutomationTests.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Pass, Fail, Error, Running
    execution_start = db.Column(db.DateTime, default=datetime.utcnow)
    execution_end = db.Column(db.DateTime)
    execution_duration = db.Column(db.Float)  # 실행 시간 (초)
    output = db.Column(db.Text)  # 실행 출력
    error_message = db.Column(db.Text)  # 오류 메시지
    screenshot_path = db.Column(db.String(512))  # 스크린샷 경로
    result_data = db.Column(db.Text)  # JSON 형태의 상세 결과 데이터
    environment = db.Column(db.String(50), default='dev')
    notes = db.Column(db.Text)  # 추가 메모 