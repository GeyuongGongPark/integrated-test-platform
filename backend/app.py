from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
import os
import tempfile
import subprocess
import json
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
from config import config

# k6 엔진 클래스 정의
class K6Engine:
    def __init__(self):
        self.k6_path = 'k6'  # k6 실행 파일 경로
    
    def execute_test(self, script_path, env_vars=None):
        """k6 성능 테스트 실행"""
        try:
            # 환경 변수 설정
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # k6 명령어 구성
            cmd = [self.k6_path, 'run', script_path, '--out', 'json=result.json']
            
            # k6 실행
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            # 결과 파싱
            if result.returncode == 0:
                return {
                    'status': 'Pass',
                    'output': result.stdout,
                    'response_time_avg': 0.0,  # 실제로는 JSON 결과에서 파싱
                    'throughput': 0.0,
                    'error_rate': 0.0
                }
            else:
                return {
                    'status': 'Fail',
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'Error',
                'error': 'k6 실행 시간 초과'
            }
        except Exception as e:
            return {
                'status': 'Error',
                'error': str(e)
            }

# k6 엔진 인스턴스 생성
k6_engine = K6Engine()

# .env 파일 로드 (절대 경로로 명시적 로드)
import os.path
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

def create_app(config_name=None):
    if config_name is None:
        # 환경 감지 개선
        if os.environ.get('VERCEL'):
            config_name = 'production'
            print("🌐 Vercel 환경 감지됨 - Production 설정 사용")
        elif os.environ.get('FLASK_ENV') == 'production':
            config_name = 'production'
            print("🏭 Production 환경 감지됨")
        else:
            config_name = 'development'
            print("💻 Development 환경 감지됨")
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 데이터베이스 URI 로깅 (민감한 정보는 마스킹)
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri:
        masked_uri = db_uri.split('@')[0].split('://')[0] + '://***@' + db_uri.split('@')[1] if '@' in db_uri else db_uri
        print(f"🗄️ Database URI: {masked_uri}")
    
    # CORS 설정 - 필요한 URL만 포함
    cors_origins = [
        'http://localhost:3000',  # 개발 환경
        'https://frontend-alpha-jade-15.vercel.app',  # 현재 프론트엔드 URL
        # Vercel URL 패턴 (와일드카드로 대체)
        'https://*.vercel.app'
    ]
    
    # 환경 변수에서 추가 CORS 설정 가져오기
    env_cors = os.environ.get('CORS_ORIGINS', '')
    if env_cors:
        cors_origins.extend(env_cors.split(','))
    
    print(f"🌐 CORS Origins: {cors_origins}")
    
    # CORS 설정 - 명시적 헤더 설정
    CORS(app, 
         origins=['*'], 
         supports_credentials=False, 
         allow_headers=['*'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'],
         expose_headers=['*'],
         max_age=86400)
    
    # 명시적 CORS 헤더 설정
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        
        # 모든 Origin 허용 (더 구체적으로 설정)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = '*'
        
        # CORS 헤더 설정
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Access-Control-Allow-Origin'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        response.headers['Access-Control-Max-Age'] = '86400'
        response.headers['Access-Control-Expose-Headers'] = '*'
        
        # Vercel 환경에서 추가 헤더
        if os.environ.get('VERCEL'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # 디버깅을 위한 로깅
        if request.method == 'OPTIONS':
            print(f"🌐 CORS Preflight Request - Origin: {origin}, Method: {request.method}")
            print(f"🔧 Preflight Response Headers: {dict(response.headers)}")
        else:
            print(f"🌐 CORS Request - Origin: {origin}, Method: {request.method}, Path: {request.path}")
        
        return response
    
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    return app, db, migrate

app, db, migrate = create_app()

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



# 기존 TCM API 엔드포인트들
@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    data = [{
        'id': p.id,
        'name': p.name,
        'description': p.description
    } for p in projects]
    return jsonify(data), 200

@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    project = Project(
        name=data.get('name'),
        description=data.get('description')
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({'message': '프로젝트 생성 완료', 'id': project.id}), 201

@app.route('/testcases', methods=['GET'])
def get_testcases():
    try:
        testcases = TestCase.query.all()
        print(f"🧪 전체 테스트 케이스 수: {len(testcases)}")
        
        # 폴더 ID별 테스트 케이스 수 확인
        folder_counts = {}
        for tc in testcases:
            folder_id = tc.folder_id
            if folder_id not in folder_counts:
                folder_counts[folder_id] = 0
            folder_counts[folder_id] += 1
        
        print(f"📁 폴더별 테스트 케이스 수: {folder_counts}")
        
        data = [{
            'id': tc.id,
            'project_id': tc.project_id,
            'main_category': tc.main_category,
            'sub_category': tc.sub_category,
            'detail_category': tc.detail_category,
            'pre_condition': tc.pre_condition,
            'expected_result': tc.expected_result,
            'result_status': tc.result_status,
            'remark': tc.remark,
            'folder_id': tc.folder_id,
            'automation_code_path': tc.automation_code_path,
            'automation_code_type': tc.automation_code_type,
            'environment': tc.environment,
            'created_at': tc.created_at,
            'updated_at': tc.updated_at
        } for tc in testcases]
        response = jsonify(data)
        
        # 명시적 CORS 헤더 설정
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        
        return response, 200
    except Exception as e:
        print(f"❌ TestCases 조회 오류: {str(e)}")
        response = jsonify({
            'error': '데이터베이스 연결 오류',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        })
        
        # 오류 응답에도 CORS 헤더 설정
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        
        return response, 500

@app.route('/testcases/<int:id>', methods=['GET'])
def get_testcase(id):
    tc = TestCase.query.get_or_404(id)
    screenshots = Screenshot.query.filter_by(test_case_id=id).all()
    screenshot_data = [{'id': ss.id, 'screenshot_path': ss.screenshot_path, 'timestamp': ss.timestamp} for ss in screenshots]
    data = {
        'id': tc.id,
        'project_id': tc.project_id,
        'main_category': tc.main_category,
        'sub_category': tc.sub_category,
        'detail_category': tc.detail_category,
        'pre_condition': tc.pre_condition,
        'expected_result': tc.expected_result,
        'result_status': tc.result_status,
        'remark': tc.remark,
        'screenshots': screenshot_data,
        'created_at': tc.created_at,
        'updated_at': tc.updated_at
    }
    return jsonify(data), 200

@app.route('/testcases', methods=['POST'])
def create_testcase():
    data = request.get_json()
    print("Received data:", data)
    print("자동화 코드 경로:", data.get('automation_code_path'))
    print("자동화 코드 타입:", data.get('automation_code_type'))
    
    # project_id가 없으면 기본 프로젝트 사용
    project_id = data.get('project_id')
    if not project_id:
        default_project = Project.query.filter_by(name='Test Management System').first()
        if default_project:
            project_id = default_project.id
        else:
            return jsonify({'error': '기본 프로젝트가 없습니다. 먼저 프로젝트를 생성해주세요.'}), 400
    
    # folder_id가 없으면 기본 폴더 사용
    folder_id = data.get('folder_id')
    if not folder_id:
        # DEV 환경의 첫 번째 배포일자 폴더를 기본으로 사용
        dev_folder = Folder.query.filter_by(folder_type='environment', environment='dev').first()
        if dev_folder:
            default_deployment_folder = Folder.query.filter_by(
                folder_type='deployment_date', 
                parent_folder_id=dev_folder.id
            ).first()
            if default_deployment_folder:
                folder_id = default_deployment_folder.id
    
    tc = TestCase(
        project_id=project_id,
        main_category=data.get('main_category', ''),
        sub_category=data.get('sub_category', ''),
        detail_category=data.get('detail_category', ''),
        pre_condition=data.get('pre_condition', ''),
        expected_result=data.get('expected_result', ''),
        result_status=data.get('result_status', 'N/T'),
        remark=data.get('remark', ''),
        environment=data.get('environment', 'dev'),
        folder_id=folder_id,
        automation_code_path=data.get('automation_code_path', ''),
        automation_code_type=data.get('automation_code_type', 'playwright')
    )

    try:
        db.session.add(tc)
        db.session.commit()
        return jsonify({'message': '테스트 케이스 생성 완료', 'id': tc.id}), 201
    except Exception as e:
        print("Error saving to database:", e)
        db.session.rollback()
        return jsonify({'error': f'데이터베이스 오류: {str(e)}'}), 500

@app.route('/testcases/<int:id>/status', methods=['PUT'])
def update_testcase_status(id):
    tc = TestCase.query.get_or_404(id)
    data = request.get_json()
    tc.result_status = data.get('status', tc.result_status)
    db.session.commit()
    return jsonify({'message': '테스트 케이스 상태 업데이트 완료'}), 200

@app.route('/testcases/<int:id>', methods=['PUT'])
def update_testcase(id):
    tc = TestCase.query.get_or_404(id)
    data = request.get_json()
    tc.main_category = data.get('main_category', tc.main_category)
    tc.sub_category = data.get('sub_category', tc.sub_category)
    tc.detail_category = data.get('detail_category', tc.detail_category)
    tc.pre_condition = data.get('pre_condition', tc.pre_condition)
    tc.expected_result = data.get('expected_result', tc.expected_result)
    tc.result_status = data.get('result_status', tc.result_status)
    tc.remark = data.get('remark', tc.remark)
    tc.environment = data.get('environment', tc.environment)
    tc.folder_id = data.get('folder_id', tc.folder_id)
    tc.automation_code_path = data.get('automation_code_path', tc.automation_code_path)
    tc.automation_code_type = data.get('automation_code_type', tc.automation_code_type)
    db.session.commit()
    return jsonify({'message': '테스트 케이스 업데이트 완료'}), 200

@app.route('/testcases/<int:id>', methods=['DELETE'])
def delete_testcase(id):
    tc = TestCase.query.get_or_404(id)
    db.session.delete(tc)
    db.session.commit()
    return jsonify({'message': '테스트 케이스 삭제 완료'}), 200

@app.route('/testresults/<int:test_case_id>', methods=['GET'])
def get_test_results(test_case_id):
    """특정 테스트 케이스의 실행 결과 조회"""
    try:
        results = TestResult.query.filter_by(test_case_id=test_case_id).order_by(TestResult.executed_at.desc()).all()
        
        result_list = []
        for result in results:
            result_data = {
                'id': result.id,
                'test_case_id': result.test_case_id,
                'result': result.result,
                'executed_at': result.executed_at.isoformat() if result.executed_at else None,
                'notes': result.notes,
                'screenshot': result.screenshot,
                'environment': result.environment,
                'execution_duration': result.execution_duration,
                'error_message': result.error_message
            }
            result_list.append(result_data)
        
        return jsonify(result_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/testcases/<int:id>/screenshots', methods=['GET'])
def get_testcase_screenshots(id):
    """테스트 케이스의 스크린샷 목록 조회"""
    try:
        test_case = TestCase.query.get_or_404(id)
        screenshots = Screenshot.query.filter_by(test_case_id=id).order_by(Screenshot.timestamp.desc()).all()
        
        screenshot_list = []
        for screenshot in screenshots:
            screenshot_data = {
                'id': screenshot.id,
                'screenshot_path': screenshot.screenshot_path,
                'timestamp': screenshot.timestamp.isoformat() if screenshot.timestamp else None
            }
            screenshot_list.append(screenshot_data)
        
        return jsonify(screenshot_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/screenshots/<path:filename>', methods=['GET'])
def get_screenshot(filename):
    """스크린샷 파일 조회"""
    try:
        import os
        screenshot_path = os.path.join('screenshots', filename)
        if os.path.exists(screenshot_path):
            return send_file(screenshot_path, mimetype='image/png')
        else:
            return jsonify({'error': '스크린샷 파일을 찾을 수 없습니다'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/testresults', methods=['POST'])
def create_test_result():
    data = request.get_json()
    result = TestResult(
        test_case_id=data.get('test_case_id'),
        result=data.get('result'),
        notes=data.get('notes')
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({'message': '테스트 결과 생성 완료', 'id': result.id}), 201

# 새로운 성능 테스트 API 엔드포인트들
@app.route('/performance-tests', methods=['GET'])
def get_performance_tests():
    tests = PerformanceTest.query.all()
    data = [{
        'id': pt.id,
        'name': pt.name,
        'description': pt.description,
        'k6_script_path': pt.k6_script_path,
        'environment': pt.environment,
        'parameters': pt.parameters,
        'created_at': pt.created_at,
        'updated_at': pt.updated_at
    } for pt in tests]
    return jsonify(data), 200

@app.route('/performance-tests', methods=['POST'])
def create_performance_test():
    data = request.get_json()
    
    pt = PerformanceTest(
        name=data.get('name'),
        description=data.get('description'),
        k6_script_path=data.get('k6_script_path'),
        environment=data.get('environment', 'prod'),
        parameters=json.dumps(data.get('parameters', {}))
    )
    
    try:
        db.session.add(pt)
        db.session.commit()
        return jsonify({'message': '성능 테스트 생성 완료', 'id': pt.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'데이터베이스 오류: {str(e)}'}), 500

@app.route('/performance-tests/<int:id>', methods=['GET'])
def get_performance_test(id):
    pt = PerformanceTest.query.get_or_404(id)
    data = {
        'id': pt.id,
        'name': pt.name,
        'description': pt.description,
        'k6_script_path': pt.k6_script_path,
        'environment': pt.environment,
        'parameters': json.loads(pt.parameters) if pt.parameters else {},
        'created_at': pt.created_at,
        'updated_at': pt.updated_at
    }
    return jsonify(data), 200

@app.route('/performance-tests/<int:id>', methods=['PUT'])
def update_performance_test(id):
    pt = PerformanceTest.query.get_or_404(id)
    data = request.get_json()
    
    pt.name = data.get('name', pt.name)
    pt.description = data.get('description', pt.description)
    pt.k6_script_path = data.get('k6_script_path', pt.k6_script_path)
    pt.environment = data.get('environment', pt.environment)
    pt.parameters = json.dumps(data.get('parameters', {}))
    
    db.session.commit()
    return jsonify({'message': '성능 테스트 업데이트 완료'}), 200

@app.route('/performance-tests/<int:id>', methods=['DELETE'])
def delete_performance_test(id):
    pt = PerformanceTest.query.get_or_404(id)
    db.session.delete(pt)
    db.session.commit()
    return jsonify({'message': '성능 테스트 삭제 완료'}), 200

@app.route('/performance-tests/<int:id>/execute', methods=['POST'])
def execute_performance_test(id):
    pt = PerformanceTest.query.get_or_404(id)
    data = request.get_json()
    
    # 환경 변수 설정
    env_vars = data.get('environment_vars', {})
    if pt.parameters:
        base_params = json.loads(pt.parameters)
        env_vars.update(base_params)
    
    # k6 테스트 실행
    result = k6_engine.execute_test(pt.k6_script_path, env_vars)
    
    # 실행 결과 저장
    execution = TestExecution(
        performance_test_id=pt.id,
        test_type='performance',
        status=result.get('status', 'Error'),
        result_data=json.dumps(result)
    )
    
    if result.get('status') == 'Pass':
        # 성능 테스트 결과 저장
        perf_result = PerformanceTestResult(
            performance_test_id=pt.id,
            status=result.get('status'),
            response_time_avg=result.get('response_time_avg'),
            throughput=result.get('throughput'),
            error_rate=result.get('error_rate', 0.0),
            result_data=json.dumps(result)
        )
        db.session.add(perf_result)
    
    db.session.add(execution)
    db.session.commit()
    
    return jsonify({
        'message': '성능 테스트 실행 완료',
        'execution_id': execution.id,
        'result': result
    }), 200

@app.route('/performance-tests/<int:id>/results', methods=['GET'])
def get_performance_test_results(id):
    results = PerformanceTestResult.query.filter_by(performance_test_id=id).all()
    data = [{
        'id': r.id,
        'performance_test_id': r.performance_test_id,
        'execution_time': r.execution_time,
        'response_time_avg': r.response_time_avg,
        'response_time_p95': r.response_time_p95,
        'throughput': r.throughput,
        'error_rate': r.error_rate,
        'status': r.status,
        'report_path': r.report_path
    } for r in results]
    return jsonify(data), 200

# 자동화 테스트 API
@app.route('/automation-tests', methods=['GET'])
def get_automation_tests():
    """모든 자동화 테스트 조회"""
    try:
        tests = AutomationTest.query.all()
        return jsonify([{
            'id': test.id,
            'name': test.name,
            'description': test.description,
            'test_type': test.test_type,
            'script_path': test.script_path,
            'environment': test.environment,
            'parameters': test.parameters,
            'created_at': test.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': test.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } for test in tests])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/automation-tests', methods=['POST'])
def create_automation_test():
    """자동화 테스트 생성"""
    try:
        data = request.get_json()
        
        new_test = AutomationTest(
            name=data['name'],
            description=data.get('description', ''),
            test_type=data['test_type'],
            script_path=data['script_path'],
            environment=data.get('environment', 'dev'),
            parameters=data.get('parameters', '')
        )
        
        db.session.add(new_test)
        db.session.commit()
        
        return jsonify({
            'id': new_test.id,
            'name': new_test.name,
            'message': '자동화 테스트가 성공적으로 생성되었습니다.'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/automation-tests/<int:id>', methods=['GET'])
def get_automation_test(id):
    """특정 자동화 테스트 조회"""
    try:
        test = AutomationTest.query.get_or_404(id)
        return jsonify({
            'id': test.id,
            'name': test.name,
            'description': test.description,
            'test_type': test.test_type,
            'script_path': test.script_path,
            'environment': test.environment,
            'parameters': test.parameters,
            'created_at': test.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': test.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/automation-tests/<int:id>', methods=['PUT'])
def update_automation_test(id):
    """자동화 테스트 수정"""
    try:
        test = AutomationTest.query.get_or_404(id)
        data = request.get_json()
        
        test.name = data['name']
        test.description = data.get('description', '')
        test.test_type = data['test_type']
        test.script_path = data['script_path']
        test.environment = data.get('environment', 'dev')
        test.parameters = data.get('parameters', '')
        test.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': '자동화 테스트가 성공적으로 수정되었습니다.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/automation-tests/<int:id>', methods=['DELETE'])
def delete_automation_test(id):
    """자동화 테스트 삭제"""
    try:
        test = AutomationTest.query.get_or_404(id)
        db.session.delete(test)
        db.session.commit()
        
        return jsonify({
            'message': '자동화 테스트가 성공적으로 삭제되었습니다.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/automation-tests/<int:id>/execute', methods=['POST'])
def execute_automation_test(id):
    """자동화 테스트 실행"""
    try:
        test = AutomationTest.query.get_or_404(id)
        
        # 실행 시작 시간
        execution_start = datetime.utcnow()
        
        # 실제로는 여기서 자동화 테스트를 실행
        # 현재는 시뮬레이션
        import time
        time.sleep(2)  # 실행 시간 시뮬레이션
        
        # 실행 종료 시간
        execution_end = datetime.utcnow()
        execution_duration = (execution_end - execution_start).total_seconds()
        
        # 시뮬레이션된 결과 (실제로는 테스트 실행 결과)
        status = 'Pass'  # 또는 'Fail', 'Error'
        output = f"테스트 '{test.name}' 실행 완료"
        error_message = None
        
        # 결과 저장
        result = AutomationTestResult(
            automation_test_id=test.id,
            status=status,
            execution_start=execution_start,
            execution_end=execution_end,
            execution_duration=execution_duration,
            output=output,
            error_message=error_message,
            environment=test.environment
        )
        
        db.session.add(result)
        db.session.commit()
        
        return jsonify({
            'message': '자동화 테스트 실행이 완료되었습니다.',
            'test_name': test.name,
            'status': status,
            'execution_duration': execution_duration,
            'result_id': result.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/automation-tests/<int:id>/results', methods=['GET'])
def get_automation_test_results(id):
    """자동화 테스트의 실행 결과 조회"""
    try:
        results = AutomationTestResult.query.filter_by(automation_test_id=id).order_by(AutomationTestResult.execution_start.desc()).all()
        
        result_list = []
        for result in results:
            result_data = {
                'id': result.id,
                'automation_test_id': result.automation_test_id,
                'status': result.status,
                'execution_start': result.execution_start.isoformat() if result.execution_start else None,
                'execution_end': result.execution_end.isoformat() if result.execution_end else None,
                'execution_duration': result.execution_duration,
                'output': result.output,
                'error_message': result.error_message,
                'screenshot_path': result.screenshot_path,
                'result_data': result.result_data,
                'environment': result.environment,
                'notes': result.notes
            }
            result_list.append(result_data)
        
        return jsonify(result_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/automation-tests/<int:id>/results/<int:result_id>', methods=['GET'])
def get_automation_test_result_detail(id, result_id):
    """특정 자동화 테스트 실행 결과 상세 조회"""
    try:
        result = AutomationTestResult.query.filter_by(
            automation_test_id=id, 
            id=result_id
        ).first_or_404()
        
        result_data = {
            'id': result.id,
            'automation_test_id': result.automation_test_id,
            'status': result.status,
            'execution_start': result.execution_start.isoformat() if result.execution_start else None,
            'execution_end': result.execution_end.isoformat() if result.execution_end else None,
            'execution_duration': result.execution_duration,
            'output': result.output,
            'error_message': result.error_message,
            'screenshot_path': result.screenshot_path,
            'result_data': result.result_data,
            'environment': result.environment,
            'notes': result.notes
        }
        
        return jsonify(result_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-executions', methods=['GET'])
def get_test_executions():
    executions = TestExecution.query.all()
    data = [{
        'id': e.id,
        'test_case_id': e.test_case_id,
        'performance_test_id': e.performance_test_id,
        'test_type': e.test_type,
        'execution_start': e.execution_start,
        'execution_end': e.execution_end,
        'status': e.status,
        'result_data': json.loads(e.result_data) if e.result_data else None
    } for e in executions]
    return jsonify(data), 200

@app.route('/test-executions', methods=['POST'])
def create_test_execution():
    data = request.get_json()
    
    execution = TestExecution(
        test_case_id=data.get('test_case_id'),
        performance_test_id=data.get('performance_test_id'),
        test_type=data.get('test_type'),
        status=data.get('status', 'Running'),
        result_data=json.dumps(data.get('result_data', {}))
    )
    
    db.session.add(execution)
    db.session.commit()
    
    return jsonify({'message': '테스트 실행 생성 완료', 'id': execution.id}), 201

# 폴더 관리 API
@app.route('/folders', methods=['GET'])
def get_folders():
    try:
        folders = Folder.query.all()
        data = [{
            'id': f.id, 
            'folder_name': f.folder_name, 
            'parent_folder_id': f.parent_folder_id,
            'folder_type': f.folder_type,
            'environment': f.environment,
            'deployment_date': f.deployment_date.strftime('%Y-%m-%d') if f.deployment_date else None,
            'created_at': f.created_at.strftime('%Y-%m-%d %H:%M:%S') if f.created_at else None
        } for f in folders]
        
        response = jsonify(data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        
        return response, 200
    except Exception as e:
        print(f"❌ 폴더 조회 오류: {str(e)}")
        response = jsonify({'error': '폴더 조회 오류', 'message': str(e)})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        return response, 500

@app.route('/folders', methods=['POST'])
def create_folder():
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('folder_name'):
            return jsonify({'error': '폴더명은 필수입니다'}), 400
        
        folder = Folder(
            folder_name=data.get('folder_name'),
            parent_folder_id=data.get('parent_folder_id'),
            folder_type=data.get('folder_type', 'environment'),
            environment=data.get('environment'),
            deployment_date=datetime.strptime(data.get('deployment_date'), '%Y-%m-%d').date() if data.get('deployment_date') else None
        )
        
        db.session.add(folder)
        db.session.commit()
        
        response = jsonify({
            'message': '폴더 생성 완료', 
            'id': folder.id,
            'folder_name': folder.folder_name,
            'folder_type': folder.folder_type,
            'environment': folder.environment
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        
        return response, 201
    except Exception as e:
        print(f"❌ 폴더 생성 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': '폴더 생성 오류', 'message': str(e)})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        return response, 500

@app.route('/folders/<int:id>', methods=['GET'])
def get_folder(id):
    try:
        folder = Folder.query.get_or_404(id)
        data = {
            'id': folder.id,
            'folder_name': folder.folder_name,
            'parent_folder_id': folder.parent_folder_id,
            'folder_type': folder.folder_type,
            'environment': folder.environment,
            'deployment_date': folder.deployment_date.strftime('%Y-%m-%d') if folder.deployment_date else None,
            'created_at': folder.created_at.strftime('%Y-%m-%d %H:%M:%S') if folder.created_at else None
        }
        
        response = jsonify(data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        
        return response, 200
    except Exception as e:
        print(f"❌ 폴더 조회 오류: {str(e)}")
        response = jsonify({'error': '폴더 조회 오류', 'message': str(e)})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        return response, 500

@app.route('/folders/<int:id>', methods=['PUT'])
def update_folder(id):
    try:
        folder = Folder.query.get_or_404(id)
        data = request.get_json()
        
        folder.folder_name = data.get('folder_name', folder.folder_name)
        folder.parent_folder_id = data.get('parent_folder_id', folder.parent_folder_id)
        folder.folder_type = data.get('folder_type', folder.folder_type)
        folder.environment = data.get('environment', folder.environment)
        
        if data.get('deployment_date'):
            folder.deployment_date = datetime.strptime(data.get('deployment_date'), '%Y-%m-%d').date()
        
        db.session.commit()
        
        response = jsonify({'message': '폴더 업데이트 완료'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        
        return response, 200
    except Exception as e:
        print(f"❌ 폴더 업데이트 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': '폴더 업데이트 오류', 'message': str(e)})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        return response, 500

@app.route('/folders/<int:id>', methods=['DELETE'])
def delete_folder(id):
    try:
        folder = Folder.query.get_or_404(id)
        
        # 하위 폴더가 있는지 확인
        child_folders = Folder.query.filter_by(parent_folder_id=id).all()
        if child_folders:
            return jsonify({'error': '하위 폴더가 있어서 삭제할 수 없습니다. 먼저 하위 폴더를 삭제해주세요.'}), 400
        
        # 해당 폴더에 속한 테스트 케이스가 있는지 확인
        test_cases = TestCase.query.filter_by(folder_id=id).all()
        if test_cases:
            return jsonify({'error': '테스트 케이스가 있어서 삭제할 수 없습니다. 먼저 테스트 케이스를 이동하거나 삭제해주세요.'}), 400
        
        db.session.delete(folder)
        db.session.commit()
        
        response = jsonify({'message': '폴더 삭제 완료'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        
        return response, 200
    except Exception as e:
        print(f"❌ 폴더 삭제 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': '폴더 삭제 오류', 'message': str(e)})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        return response, 500

# 새로운 대시보드 요약 API
@app.route('/dashboard-summaries', methods=['GET'])
def get_dashboard_summaries():
    summaries = DashboardSummary.query.all()
    data = [{
        'id': s.id,
        'environment': s.environment,
        'total_tests': s.total_tests,
        'passed_tests': s.passed_tests,
        'failed_tests': s.failed_tests,
        'skipped_tests': s.skipped_tests,
        'pass_rate': s.pass_rate,
        'last_updated': s.last_updated
    } for s in summaries]
    return jsonify(data), 200

@app.route('/dashboard-summaries', methods=['POST'])
def create_dashboard_summary():
    data = request.get_json()
    summary = DashboardSummary(
        environment=data.get('environment'),
        total_tests=data.get('total_tests', 0),
        passed_tests=data.get('passed_tests', 0),
        failed_tests=data.get('failed_tests', 0),
        skipped_tests=data.get('skipped_tests', 0),
        pass_rate=data.get('pass_rate', 0.0)
    )
    db.session.add(summary)
    db.session.commit()
    return jsonify({'message': '대시보드 요약 생성 완료', 'id': summary.id}), 201

@app.route('/dashboard-summaries/<int:id>', methods=['PUT'])
def update_dashboard_summary(id):
    summary = DashboardSummary.query.get_or_404(id)
    data = request.get_json()
    summary.environment = data.get('environment', summary.environment)
    summary.total_tests = data.get('total_tests', summary.total_tests)
    summary.passed_tests = data.get('passed_tests', summary.passed_tests)
    summary.failed_tests = data.get('failed_tests', summary.failed_tests)
    summary.skipped_tests = data.get('skipped_tests', summary.skipped_tests)
    summary.pass_rate = data.get('pass_rate', summary.pass_rate)
    db.session.commit()
    return jsonify({'message': '대시보드 요약 업데이트 완료'}), 200

@app.route('/dashboard-summaries/<int:id>', methods=['DELETE'])
def delete_dashboard_summary(id):
    summary = DashboardSummary.query.get_or_404(id)
    db.session.delete(summary)
    db.session.commit()
    return jsonify({'message': '대시보드 요약 삭제 완료'}), 200

# 폴더 트리 구조 API
@app.route('/folders/tree', methods=['GET'])
def get_folder_tree():
    """환경별 → 배포일자별 폴더 트리 구조 반환"""
    try:
        # 환경별 폴더 조회
        environment_folders = Folder.query.filter_by(
            folder_type='environment'
        ).all()
        
        print(f"🔍 환경 폴더 수: {len(environment_folders)}")
        
        tree = []
        for env_folder in environment_folders:
            env_node = {
                'id': env_folder.id,
                'name': env_folder.folder_name,
                'type': 'environment',
                'environment': env_folder.environment,
                'children': []
            }
            
            print(f"🌍 환경 폴더: {env_folder.folder_name} (ID: {env_folder.id})")
            
            # 해당 환경의 배포일자별 폴더 조회
            deployment_folders = Folder.query.filter_by(
                folder_type='deployment_date',
                parent_folder_id=env_folder.id
            ).all()
            
            print(f"📅 배포일자 폴더 수: {len(deployment_folders)}")
            
            for dep_folder in deployment_folders:
                dep_node = {
                    'id': dep_folder.id,
                    'name': dep_folder.folder_name,
                    'type': 'deployment_date',
                    'deployment_date': dep_folder.deployment_date.strftime('%Y-%m-%d'),
                    'children': []
                }
                
                print(f"📅 배포일자 폴더: {dep_folder.folder_name} (ID: {dep_folder.id})")
                
                # 테스트 케이스는 제외하고 폴더만 반환
                env_node['children'].append(dep_node)
            
            tree.append(env_node)
        
        response = jsonify(tree)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        
        return response, 200
        
    except Exception as e:
        print(f"❌ 폴더 트리 조회 오류: {str(e)}")
        response = jsonify({'error': '폴더 트리 조회 오류', 'message': str(e)})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        return response, 500

# 환경별 테스트 결과 요약 API
@app.route('/test-results/summary/<environment>', methods=['GET'])
def get_test_results_summary(environment):
    """특정 환경의 테스트 결과 요약"""
    try:
        # 해당 환경의 모든 테스트 결과 조회
        results = TestResult.query.filter_by(environment=environment).all()
        
        total = len(results)
        passed = len([r for r in results if r.result == 'Pass'])
        failed = len([r for r in results if r.result == 'Fail'])
        skipped = len([r for r in results if r.result == 'Skip'])
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        summary = {
            'environment': environment,
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': failed,
            'skipped_tests': skipped,
            'pass_rate': round(pass_rate, 2),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 엑셀 업로드 API
@app.route('/testcases/upload', methods=['POST'])
def upload_testcases_excel():
    """엑셀 파일에서 테스트 케이스 업로드"""
    try:
        print("=== 파일 업로드 디버깅 ===")
        print(f"Content-Type: {request.headers.get('Content-Type')}")
        print(f"Files: {list(request.files.keys())}")
        print(f"Form data: {list(request.form.keys())}")
        
        if 'file' not in request.files:
            print("❌ 'file' 키가 request.files에 없음")
            print(f"사용 가능한 키들: {list(request.files.keys())}")
            return jsonify({'error': '파일이 없습니다'}), 400
        
        file = request.files['file']
        print(f"파일명: {file.filename}")
        print(f"파일 크기: {len(file.read()) if file else 'N/A'}")
        file.seek(0)  # 파일 포인터를 다시 처음으로
        
        if file.filename == '':
            print("❌ 파일명이 비어있음")
            return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
        
        if not file.filename.endswith('.xlsx'):
            print(f"❌ 지원하지 않는 파일 형식: {file.filename}")
            return jsonify({'error': '엑셀 파일(.xlsx)만 업로드 가능합니다'}), 400
        
        print("✅ 파일 검증 통과")
        
        # 엑셀 파일 읽기
        df = pd.read_excel(file)
        print(f"✅ 엑셀 파일 읽기 성공, 행 수: {len(df)}")
        print(f"📊 컬럼명: {list(df.columns)}")
        print(f"📋 첫 번째 행 데이터: {df.iloc[0].to_dict()}")
        
        created_count = 0
        for index, row in df.iterrows():
            print(f"🔍 처리 중인 행 {index + 1}: {row.to_dict()}")
            
            test_case = TestCase(
                project_id=row.get('project_id', 1),
                main_category=row.get('main_category', ''),
                sub_category=row.get('sub_category', ''),
                detail_category=row.get('detail_category', ''),
                pre_condition=row.get('pre_condition', ''),
                expected_result=row.get('expected_result', ''),
                result_status=row.get('result_status', 'N/T'),
                remark=row.get('remark', ''),
                environment=row.get('environment', 'dev'),
                automation_code_path=row.get('automation_code_path', ''),
                automation_code_type=row.get('automation_code_type', '')
            )
            
            print(f"📝 생성된 테스트 케이스: main_category='{test_case.main_category}', expected_result='{test_case.expected_result}'")
            
            db.session.add(test_case)
            created_count += 1
        
        try:
            db.session.commit()
            print(f"✅ {created_count}개의 테스트 케이스 생성 완료")
        except Exception as commit_error:
            print(f"❌ 데이터베이스 커밋 오류: {str(commit_error)}")
            db.session.rollback()
            raise commit_error
        
        return jsonify({
            'message': f'{created_count}개의 테스트 케이스가 업로드되었습니다',
            'created_count': created_count
        }), 201
        
    except Exception as e:
        print(f"❌ 파일 업로드 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 엑셀 다운로드 API
@app.route('/testcases/download', methods=['GET'])
def download_testcases_excel():
    """테스트 케이스를 엑셀 파일로 다운로드"""
    try:
        # 모든 테스트 케이스 조회
        test_cases = TestCase.query.all()
        
        # DataFrame 생성
        data = []
        for tc in test_cases:
            data.append({
                'id': tc.id,
                'project_id': tc.project_id,
                'main_category': tc.main_category,
                'sub_category': tc.sub_category,
                'detail_category': tc.detail_category,
                'pre_condition': tc.pre_condition,
                'expected_result': tc.expected_result,
                'result_status': tc.result_status,
                'remark': tc.remark,
                'environment': tc.environment,
                'automation_code_path': tc.automation_code_path,
                'automation_code_type': tc.automation_code_type,
                'created_at': tc.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(data)
        
        # 엑셀 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='TestCases')
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'testcases_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
    except Exception as e:
        print(f"다운로드 에러: {str(e)}")
        return jsonify({'error': f'파일 다운로드 중 오류가 발생했습니다: {str(e)}'}), 500

# 자동화 코드 실행 API
@app.route('/testcases/<int:id>/execute', methods=['POST'])
def execute_automation_code(id):
    """테스트 케이스의 자동화 코드 실행"""
    try:
        test_case = TestCase.query.get_or_404(id)
        
        if not test_case.automation_code_path:
            return jsonify({'error': '자동화 코드 경로가 설정되지 않았습니다'}), 400
        
        # 자동화 코드 실행
        script_path = test_case.automation_code_path
        script_type = test_case.automation_code_type or 'playwright'
        
        import time
        start_time = time.time()
        
        if script_type == 'k6':
            # k6 성능 테스트 실행
            result = k6_engine.execute_test(script_path, {})
            execution_duration = time.time() - start_time
            
            # 실행 결과 저장
            test_result = TestResult(
                test_case_id=id,
                result=result['status'],
                environment=test_case.environment,
                execution_duration=execution_duration,
                error_message=result.get('error')
            )
            db.session.add(test_result)
            db.session.commit()
            
            return jsonify({
                'message': '자동화 코드 실행 완료',
                'result': result['status'],
                'output': result.get('output', ''),
                'error': result.get('error', ''),
                'execution_duration': execution_duration
            }), 200
            
        elif script_type in ['selenium', 'playwright', 'k6']:
            # UI 테스트 실행
            if script_type == 'k6':
                # k6 실행
                import os
                # 스크립트 경로를 절대 경로로 변환
                if not os.path.isabs(script_path):
                    # 백엔드 디렉토리에서 상위 디렉토리로 이동
                    backend_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(backend_dir)
                    script_path = os.path.join(project_root, script_path)
                
                print(f"🔍 k6 실행 경로: {script_path}")
                print(f"📁 파일 존재 여부: {os.path.exists(script_path)}")
                print(f"📁 프로젝트 루트: {project_root}")
                print(f"📁 현재 작업 디렉토리: {os.getcwd()}")
                
                # 절대 경로 사용
                absolute_script_path = os.path.abspath(script_path)
                print(f"🔍 절대 경로: {absolute_script_path}")
                print(f"📁 절대 경로 파일 존재 여부: {os.path.exists(absolute_script_path)}")
                
                # 환경 변수 설정
                env = os.environ.copy()
                env['K6_BROWSER_ENABLED'] = 'true'
                env['K6_BROWSER_HEADLESS'] = 'true'
                
                result = subprocess.run(
                    ['k6', 'run', absolute_script_path],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5분 타임아웃
                    cwd=project_root,  # 프로젝트 루트에서 실행
                    env=env
                )
            elif script_type == 'playwright':
                # Playwright 실행
                import os
                # 스크립트 경로를 절대 경로로 변환
                if not os.path.isabs(script_path):
                    script_path = os.path.join(os.getcwd(), script_path)
                
                result = subprocess.run(
                    ['npx', 'playwright', 'test', script_path, '--reporter=json'],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5분 타임아웃
                    cwd=os.path.dirname(script_path) if os.path.dirname(script_path) else None
                )
            else:
                # Selenium 실행
                import os
                # 스크립트 경로를 절대 경로로 변환
                if not os.path.isabs(script_path):
                    script_path = os.path.join(os.getcwd(), script_path)
                
                result = subprocess.run(
                    ['python', script_path],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5분 타임아웃
                    cwd=os.path.dirname(script_path) if os.path.dirname(script_path) else None
                )
            
            execution_duration = time.time() - start_time
            
            # 스크린샷 경로 생성 (Playwright의 경우)
            screenshot_path = None
            if script_type == 'playwright' and result.returncode == 0:
                # Playwright 테스트 결과에서 스크린샷 경로 추출
                try:
                    import json
                    import os
                    from datetime import datetime
                    
                    # 테스트 결과 디렉토리 생성
                    screenshot_dir = os.path.join('screenshots', f'testcase_{id}')
                    os.makedirs(screenshot_dir, exist_ok=True)
                    
                    # 스크린샷 파일명 생성
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    screenshot_path = os.path.join(screenshot_dir, f'screenshot_{timestamp}.png')
                    
                    # Playwright 실행 결과에서 스크린샷 복사 (실제 구현에서는 더 복잡)
                    if os.path.exists('test-results'):
                        import shutil
                        for root, dirs, files in os.walk('test-results'):
                            for file in files:
                                if file.endswith('.png'):
                                    shutil.copy2(os.path.join(root, file), screenshot_path)
                                    break
                except Exception as e:
                    print(f"스크린샷 처리 중 오류: {e}")
            
            # 실행 결과 저장
            test_result = TestResult(
                test_case_id=id,
                result='Pass' if result.returncode == 0 else 'Fail',
                environment=test_case.environment,
                execution_duration=execution_duration,
                error_message=result.stderr if result.returncode != 0 else None,
                screenshot=screenshot_path
            )
            db.session.add(test_result)
            db.session.commit()
            
            return jsonify({
                'message': '자동화 코드 실행 완료',
                'result': 'Pass' if result.returncode == 0 else 'Fail',
                'output': result.stdout,
                'error': result.stderr,
                'execution_duration': execution_duration,
                'screenshot_path': screenshot_path
            }), 200
        else:
            return jsonify({'error': '지원하지 않는 자동화 코드 타입입니다'}), 400
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': '자동화 코드 실행 시간이 초과되었습니다'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def init_db():
    """데이터베이스 초기화 및 기본 데이터 생성"""
    with app.app_context():
        try:
            # 데이터베이스 연결 테스트
            db.session.execute('SELECT 1')
            print("✅ 데이터베이스 연결 성공")
            
            # 테이블 생성
            db.create_all()
            print("✅ PostgreSQL 테이블 생성 완료")
            
            # 기본 프로젝트가 없으면 생성
            default_project = Project.query.filter_by(name='Test Management System').first()
            if not default_project:
                default_project = Project(
                    name='Test Management System',
                    description='통합 테스트 관리 시스템'
                )
                db.session.add(default_project)
                db.session.commit()
                print("✅ 기본 프로젝트 생성 완료")
            
            # 기본 폴더 구조가 없으면 생성
            if not Folder.query.first():
                # DEV 환경 폴더
                dev_folder = Folder(
                    folder_name='DEV 환경',
                    folder_type='environment',
                    environment='dev'
                )
                db.session.add(dev_folder)
                db.session.flush()  # ID 생성
                
                # DEV 환경의 배포일자 폴더
                dev_deployment = Folder(
                    folder_name='2024-01-15',
                    folder_type='deployment_date',
                    parent_folder_id=dev_folder.id,
                    environment='dev',
                    deployment_date=datetime.strptime('2024-01-15', '%Y-%m-%d').date()
                )
                db.session.add(dev_deployment)
                
                # ALPHA 환경 폴더
                alpha_folder = Folder(
                    folder_name='ALPHA 환경',
                    folder_type='environment',
                    environment='alpha'
                )
                db.session.add(alpha_folder)
                db.session.flush()
                
                # ALPHA 환경의 배포일자 폴더
                alpha_deployment = Folder(
                    folder_name='2024-01-20',
                    folder_type='deployment_date',
                    parent_folder_id=alpha_folder.id,
                    environment='alpha',
                    deployment_date=datetime.strptime('2024-01-20', '%Y-%m-%d').date()
                )
                db.session.add(alpha_deployment)
                
                # PRODUCTION 환경 폴더
                prod_folder = Folder(
                    folder_name='PRODUCTION 환경',
                    folder_type='environment',
                    environment='production'
                )
                db.session.add(prod_folder)
                db.session.flush()
                
                # PRODUCTION 환경의 배포일자 폴더
                prod_deployment = Folder(
                    folder_name='2024-01-25',
                    folder_type='deployment_date',
                    parent_folder_id=prod_folder.id,
                    environment='production',
                    deployment_date=datetime.strptime('2024-01-25', '%Y-%m-%d').date()
                )
                db.session.add(prod_deployment)
                
                db.session.commit()
                print("✅ 기본 폴더 구조 생성 완료")
            
            # 기존 테스트 케이스들에 기본 폴더 설정
            orphaned_testcases = TestCase.query.filter_by(folder_id=None).all()
            if orphaned_testcases:
                # DEV 환경의 첫 번째 배포일자 폴더를 기본으로 사용
                dev_folder = Folder.query.filter_by(folder_type='environment', environment='dev').first()
                if dev_folder:
                    default_deployment_folder = Folder.query.filter_by(
                        folder_type='deployment_date', 
                        parent_folder_id=dev_folder.id
                    ).first()
                    if default_deployment_folder:
                        for tc in orphaned_testcases:
                            tc.folder_id = default_deployment_folder.id
                        db.session.commit()
                        print(f"✅ {len(orphaned_testcases)}개의 테스트 케이스에 기본 폴더 설정 완료")
            
            print("Neon PostgreSQL 데이터베이스 초기화 완료!")
            
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 중 오류: {str(e)}")
            db.session.rollback()
            # 오류가 있어도 앱은 계속 실행
            print("⚠️ 데이터베이스 초기화 실패했지만 앱은 계속 실행됩니다.")

# 헬스체크 엔드포인트 추가
@app.route('/health', methods=['GET'])
def health_check():
    response = jsonify({
        'status': 'healthy', 
        'message': 'Test Platform Backend is running - Auto Deploy Test',
        'version': '1.0.1',
        'timestamp': datetime.now().isoformat(),
        'deploy_test': 'GitHub Actions CI/CD working!',
        'cors_enabled': True,
        'environment': 'production' if os.environ.get('VERCEL') else 'development'
    })
    
    # 명시적 CORS 헤더 설정
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
    response.headers['Access-Control-Allow-Credentials'] = 'false'
    
    return response, 200

# 간단한 테스트 엔드포인트 추가
@app.route('/test', methods=['GET'])
def test_endpoint():
    response = jsonify({
        'message': 'CORS test successful',
        'timestamp': datetime.now().isoformat(),
        'origin': request.headers.get('Origin', 'unknown'),
        'headers': {
            'origin': request.headers.get('Origin'),
            'host': request.headers.get('Host'),
            'user_agent': request.headers.get('User-Agent'),
            'referer': request.headers.get('Referer')
        }
    })
    
    # 명시적 CORS 헤더 설정
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
    response.headers['Access-Control-Allow-Credentials'] = 'false'
    
    return response, 200

# CORS 전용 테스트 엔드포인트
@app.route('/cors-test', methods=['GET', 'POST', 'OPTIONS'])
def cors_test():
    """CORS 전용 테스트 엔드포인트"""
    response = jsonify({
        'message': 'CORS test endpoint working',
        'method': request.method,
        'timestamp': datetime.now().isoformat(),
        'origin': request.headers.get('Origin', 'unknown'),
        'headers': dict(request.headers)
    })
    
    # 명시적 CORS 헤더 설정
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
    response.headers['Access-Control-Allow-Credentials'] = 'false'
    
    return response, 200

# CORS preflight 요청 처리
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """CORS preflight 요청 처리"""
    origin = request.headers.get('Origin')
    
    response = jsonify({'status': 'preflight_ok'})
    
    # 명시적 CORS 헤더 설정
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Access-Control-Allow-Origin'
    response.headers['Access-Control-Allow-Credentials'] = 'false'
    response.headers['Access-Control-Max-Age'] = '86400'
    response.headers['Access-Control-Expose-Headers'] = '*'
    
    # Vercel 환경에서 추가 헤더
    if os.environ.get('VERCEL'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 디버깅을 위한 로그
    print(f"🌐 CORS Preflight - Origin: {origin}, Path: {path}")
    print(f"🔧 Preflight Headers set: {dict(response.headers)}")
    
    return response, 200

# 환경 진단 엔드포인트 추가
@app.route('/debug/environment', methods=['GET'])
def debug_environment():
    """환경 설정 진단 엔드포인트"""
    try:
        # 데이터베이스 연결 테스트
        db_status = "unknown"
        try:
            db.session.execute('SELECT 1')
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # 폴더 및 테스트 케이스 정보
        folders = Folder.query.all()
        testcases = TestCase.query.all()
        
        folder_info = [{
            'id': f.id,
            'name': f.folder_name,
            'type': f.folder_type,
            'environment': f.environment,
            'parent_id': f.parent_folder_id
        } for f in folders]
        
        testcase_info = [{
            'id': tc.id,
            'folder_id': tc.folder_id,
            'main_category': tc.main_category,
            'sub_category': tc.sub_category
        } for tc in testcases]
        
        # CORS 헤더 정보 수집
        cors_headers = {
            'origin': request.headers.get('Origin'),
            'host': request.headers.get('Host'),
            'user_agent': request.headers.get('User-Agent'),
            'referer': request.headers.get('Referer')
        }
        
        return jsonify({
            'environment': {
                'vercel': bool(os.environ.get('VERCEL')),
                'flask_env': os.environ.get('FLASK_ENV'),
                'node_env': os.environ.get('NODE_ENV'),
                'database_uri_type': 'postgresql' if 'postgresql' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'sqlite' if 'sqlite' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'unknown'
            },
            'database': {
                'status': db_status,
                'uri_masked': app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[0].split('://')[0] + '://***@' + app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[1] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else app.config.get('SQLALCHEMY_DATABASE_URI', '')
            },
            'folders': {
                'count': len(folders),
                'data': folder_info
            },
            'testcases': {
                'count': len(testcases),
                'data': testcase_info
            },
            'cors': {
                'origins': [
                    'http://localhost:3000',
                    'https://frontend-alpha-jade-15.vercel.app',
                    'https://*.vercel.app'
                ],
                'request_headers': cors_headers,
                'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'],
                'allowed_headers': ['*']
            },
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Flask 서버 실행
if __name__ == '__main__':
    init_db()  # 데이터베이스 초기화
    app.run(host='0.0.0.0', port=8000, debug=True)

