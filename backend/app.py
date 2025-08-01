from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
import os
import tempfile
import subprocess
import json
import pymysql

# PyMySQL을 MySQLdb로 등록
pymysql.install_as_MySQLdb()

app = Flask(__name__)
CORS(app)

# MySQL 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/testmanager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    main_category = db.Column(db.String(255), nullable=False)
    sub_category = db.Column(db.String(255), nullable=False)
    detail_category = db.Column(db.String(255), nullable=False)
    pre_condition = db.Column(db.Text)
    description = db.Column(db.Text)
    result_status = db.Column(db.String(10), default='N/T')
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'))
    result = db.Column(db.String(10))
    executed_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    notes = db.Column(db.Text)
    screenshot = db.Column(db.String(255))

class Folder(db.Model):
    __tablename__ = 'Folders'
    id = db.Column(db.Integer, primary_key=True)
    folder_name = db.Column(db.String(255), nullable=False)
    parent_folder_id = db.Column(db.Integer, db.ForeignKey('Folders.id'), nullable=True)

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

# k6 실행 엔진
class K6ExecutionEngine:
    def __init__(self, k6_script_dir="test-scripts/performance/clm/nomerl"):
        self.k6_script_dir = k6_script_dir
    
    def execute_test(self, script_name, environment_vars):
        """k6 성능 테스트 실행"""
        script_path = os.path.join(self.k6_script_dir, script_name)
        
        if not os.path.exists(script_path):
            return {"error": f"스크립트 파일을 찾을 수 없습니다: {script_path}"}
        
        env_vars = " ".join([f"-e {k}={v}" for k, v in environment_vars.items()])
        cmd = f"k6 run {env_vars} {script_path}"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            return self.parse_k6_output(result.stdout, result.stderr, result.returncode)
        except subprocess.TimeoutExpired:
            return {"error": "테스트 실행 시간 초과"}
        except Exception as e:
            return {"error": f"테스트 실행 오류: {str(e)}"}
    
    def parse_k6_output(self, stdout, stderr, returncode):
        """k6 출력 결과 파싱"""
        if returncode != 0:
            return {"error": f"k6 실행 실패: {stderr}"}
        
        # 간단한 결과 파싱 (실제로는 더 정교한 파싱 필요)
        lines = stdout.split('\n')
        result = {
            "status": "Pass" if returncode == 0 else "Fail",
            "output": stdout,
            "error": stderr if stderr else None
        }
        
        # 응답 시간, 처리량 등 추출 시도
        for line in lines:
            if "http_req_duration" in line and "avg=" in line:
                try:
                    avg_part = line.split("avg=")[1].split()[0]
                    result["response_time_avg"] = float(avg_part)
                except:
                    pass
        
        return result

# k6 실행 엔진 인스턴스
k6_engine = K6ExecutionEngine()

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
    testcases = TestCase.query.all()
    data = [{
        'id': tc.id,
        'project_id': tc.project_id,
        'main_category': tc.main_category,
        'sub_category': tc.sub_category,
        'detail_category': tc.detail_category,
        'pre_condition': tc.pre_condition,
        'description': tc.description,
        'result_status': tc.result_status,
        'remark': tc.remark,
        'created_at': tc.created_at,
        'updated_at': tc.updated_at
    } for tc in testcases]
    return jsonify(data), 200

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
        'description': tc.description,
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
    
    if not data.get('project_id'):
        return jsonify({'error': 'project_id는 필수입니다'}), 400
    
    tc = TestCase(
        project_id=data.get('project_id'),
        main_category=data.get('main_category', ''),
        sub_category=data.get('sub_category', ''),
        detail_category=data.get('detail_category', ''),
        pre_condition=data.get('pre_condition', ''),
        description=data.get('description', ''),
        result_status=data.get('result_status', 'N/T'),
        remark=data.get('remark', '')
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
    tc.description = data.get('description', tc.description)
    tc.result_status = data.get('result_status', tc.result_status)
    tc.remark = data.get('remark', tc.remark)
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
    results = TestResult.query.filter_by(test_case_id=test_case_id).all()
    data = [{
        'id': r.id,
        'test_case_id': r.test_case_id,
        'result': r.result,
        'executed_at': r.executed_at,
        'notes': r.notes
    } for r in results]
    return jsonify(data), 200

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

# 기존 폴더 관리 API
@app.route('/folders', methods=['GET'])
def get_folders():
    folders = Folder.query.all()
    data = [{'id': f.id, 'folder_name': f.folder_name, 'parent_folder_id': f.parent_folder_id} for f in folders]
    return jsonify(data), 200

@app.route('/folders', methods=['POST'])
def create_folder():
    data = request.get_json()
    folder = Folder(
        folder_name=data.get('folder_name'),
        parent_folder_id=data.get('parent_folder_id')
    )
    db.session.add(folder)
    db.session.commit()
    return jsonify({'message': '폴더 생성 완료', 'id': folder.id}), 201

def init_db():
    """데이터베이스 초기화 및 기본 데이터 생성"""
    with app.app_context():
        print(f"데이터베이스 경로: {db_path}")
        
        # 데이터베이스 디렉토리 권한 확인
        db_dir = os.path.dirname(db_path)
        if not os.access(db_dir, os.W_OK):
            print(f"경고: 데이터베이스 디렉토리에 쓰기 권한이 없습니다: {db_dir}")
            print("임시 디렉토리를 사용합니다.")
        
        # 기존 데이터베이스 파일이 읽기 전용인 경우 삭제
        if os.path.exists(db_path) and not os.access(db_path, os.W_OK):
            try:
                os.remove(db_path)
                print(f"읽기 전용 데이터베이스 파일 삭제: {db_path}")
            except Exception as e:
                print(f"데이터베이스 파일 삭제 실패: {e}")
        
        # 테이블 생성
        db.create_all()
        print("데이터베이스 테이블 생성 완료")
        
        # 기본 프로젝트가 없으면 생성
        if not Project.query.first():
            default_project = Project(
                name="테스트 프로젝트",
                description="테스트 케이스 관리 시스템"
            )
            db.session.add(default_project)
            db.session.commit()
            print("기본 프로젝트가 생성되었습니다.")
        
        # 기본 성능 테스트가 없으면 생성
        if not PerformanceTest.query.first():
            default_perf_test = PerformanceTest(
                name="CLM 계약서 생성 테스트",
                description="LFBZ CLM 시스템 계약서 생성 성능 테스트",
                k6_script_path="clm_draft.js",
                environment="prod",
                parameters=json.dumps({
                    "DRAFT_TYPE": "new",
                    "SECURITY_TYPE": "all",
                    "REVIEW_TYPE": "use"
                })
            )
            db.session.add(default_perf_test)
            db.session.commit()
            print("기본 성능 테스트가 생성되었습니다.")
        
        # 데이터베이스 파일 권한 확인
        if os.path.exists(db_path):
            print(f"데이터베이스 파일 생성됨: {db_path}")
            print(f"파일 권한: {oct(os.stat(db_path).st_mode)[-3:]}")
            print(f"쓰기 권한: {os.access(db_path, os.W_OK)}")
        else:
            print("경고: 데이터베이스 파일이 생성되지 않았습니다!")

# Flask 서버 실행
if __name__ == '__main__':
    init_db()  # 데이터베이스 초기화
    app.run(debug=True, port=8000)

