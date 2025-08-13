from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 사용자 모델
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='User')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

# 프로젝트 모델
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 테스트 케이스 모델
class TestCase(db.Model):
    __tablename__ = 'TestCases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    test_type = db.Column(db.String(50))
    script_path = db.Column(db.String(500))
    folder_id = db.Column(db.Integer, db.ForeignKey('Folders.id'), nullable=True)
    main_category = db.Column(db.String(100))
    sub_category = db.Column(db.String(100))
    detail_category = db.Column(db.String(100))
    pre_condition = db.Column(db.Text)
    expected_result = db.Column(db.Text)
    remark = db.Column(db.Text)
    automation_code_path = db.Column(db.String(500))
    environment = db.Column(db.String(50), default='dev')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 성능 테스트 모델
class PerformanceTest(db.Model):
    __tablename__ = 'PerformanceTests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    script_path = db.Column(db.String(500))
    environment = db.Column(db.String(100))
    parameters = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 자동화 테스트 모델
class AutomationTest(db.Model):
    __tablename__ = 'AutomationTests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    test_type = db.Column(db.String(50))  # playwright, selenium 등
    script_path = db.Column(db.String(500))
    environment = db.Column(db.String(50), default='dev')
    parameters = db.Column(db.Text)  # JSON 형태로 저장
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

# 테스트 결과 모델
class TestResult(db.Model):
    __tablename__ = 'TestResults'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=False)
    result = db.Column(db.String(20))  # Pass, Fail, Skip, Error
    execution_time = db.Column(db.Float)  # 초 단위
    environment = db.Column(db.String(50))
    executed_by = db.Column(db.String(100))
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

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
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# 테스트 실행 기록 모델
class TestExecution(db.Model):
    __tablename__ = 'TestExecutions'
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(50))  # performance, automation, manual
    test_id = db.Column(db.Integer)  # 해당 테스트의 ID
    environment = db.Column(db.String(50))
    executed_by = db.Column(db.String(100))
    status = db.Column(db.String(20))  # running, completed, failed
    result_summary = db.Column(db.Text)  # JSON 형태로 저장
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

# 스크린샷 모델
class Screenshot(db.Model):
    __tablename__ = 'Screenshots'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=False)
    screenshot_path = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
