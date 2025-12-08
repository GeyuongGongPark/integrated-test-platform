"""
공통 헬퍼 함수들
"""
from flask import jsonify
from models import Project, Folder, TestCase, TestResult
from utils.cors import add_cors_headers
from utils.logger import get_logger

logger = get_logger(__name__)

def get_or_create_default_project():
    """기본 프로젝트 조회 또는 생성"""
    default_project = Project.query.filter_by(name='Test Management System').first()
    if not default_project:
        default_project = Project(
            name='Test Management System',
            description='기본 테스트 관리 시스템 프로젝트'
        )
        from models import db
        db.session.add(default_project)
        db.session.flush()  # ID 생성을 위해 flush
        logger.info(f"기본 프로젝트 생성됨: {default_project.name} (ID: {default_project.id})")
    return default_project

def get_or_create_default_folder():
    """기본 폴더 조회 또는 생성"""
    # DEV 환경의 첫 번째 배포일자 폴더를 기본으로 사용
    dev_folder = Folder.query.filter_by(folder_type='environment', environment='dev').first()
    if dev_folder:
        default_deployment_folder = Folder.query.filter_by(
            folder_type='deployment_date', 
            parent_folder_id=dev_folder.id
        ).first()
        if default_deployment_folder:
            return default_deployment_folder
    return None

def validate_required_fields(data, required_fields):
    """필수 필드 검증"""
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        response = jsonify({'error': f'필수 필드가 누락되었습니다: {", ".join(missing_fields)}'})
        return add_cors_headers(response), 400
    return None

def create_error_response(message, status_code=400):
    """에러 응답 생성"""
    response = jsonify({'error': message})
    return add_cors_headers(response), status_code

def create_success_response(data, status_code=200):
    """성공 응답 생성"""
    response = jsonify(data)
    return add_cors_headers(response), status_code

def create_cors_response(data=None, status_code=200):
    """CORS 헤더가 포함된 응답 생성"""
    if data is None:
        data = {'status': 'preflight_ok'}
    response = jsonify(data)
    from utils.cors import add_cors_headers
    return add_cors_headers(response), status_code

def handle_options_request():
    """OPTIONS 요청 처리"""
    return create_cors_response()

def get_environment_folders(env):
    """환경별 폴더 ID 목록 반환"""
    if env == 'dev':
        return [1, 4, 7, 8, 9, 10, 11, 12, 13]
    elif env == 'alpha':
        return [2, 5]
    else:  # production
        return [3, 6]

def calculate_test_results(env_folders):
    """환경별 테스트 결과 계산"""
    try:
        from models import db
        passed_tests = db.session.query(TestResult).join(TestCase).filter(
            TestCase.folder_id.in_(env_folders),
            TestResult.result == 'Pass'
        ).count()
        failed_tests = db.session.query(TestResult).join(TestCase).filter(
            TestCase.folder_id.in_(env_folders),
            TestResult.result == 'Fail'
        ).count()
        nt_tests = db.session.query(TestResult).join(TestCase).filter(
            TestCase.folder_id.in_(env_folders),
            TestResult.result == 'N/T'
        ).count()
        na_tests = db.session.query(TestResult).join(TestCase).filter(
            TestCase.folder_id.in_(env_folders),
            TestResult.result == 'N/A'
        ).count()
        blocked_tests = db.session.query(TestResult).join(TestCase).filter(
            TestCase.folder_id.in_(env_folders),
            TestResult.result == 'Block'
        ).count()
        return passed_tests, failed_tests, nt_tests, na_tests, blocked_tests
    except Exception:
        return 0, 0, 0, 0, 0

def generate_realistic_test_distribution(total_testcases):
    """현실적인 테스트 분포 생성"""
    nt_tests = int(total_testcases * 0.7)  # 70%는 아직 테스트하지 않음
    na_tests = int(total_testcases * 0.1)  # 10%는 N/A
    passed_tests = int(total_testcases * 0.15)  # 15%는 Pass
    failed_tests = int(total_testcases * 0.03)  # 3%는 Fail
    blocked_tests = int(total_testcases * 0.02)  # 2%는 Block
    
    # 남은 테스트 케이스들을 N/T에 추가
    remaining = total_testcases - (nt_tests + na_tests + passed_tests + failed_tests + blocked_tests)
    nt_tests += remaining
    
    return passed_tests, failed_tests, nt_tests, na_tests, blocked_tests
