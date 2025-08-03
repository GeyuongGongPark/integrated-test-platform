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

# .env 파일 로드 (절대 경로로 명시적 로드)
import os.path
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    CORS(app, origins=os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(','))
    
    # 추가 CORS 설정
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
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
    main_category = db.Column(db.String(255), nullable=False)
    sub_category = db.Column(db.String(255), nullable=False)
    detail_category = db.Column(db.String(255), nullable=False)
    pre_condition = db.Column(db.Text)
    description = db.Column(db.Text)
    result_status = db.Column(db.String(10), default='N/T')
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # 새로운 필드들 추가
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
        
        tree = []
        for env_folder in environment_folders:
            env_node = {
                'id': env_folder.id,
                'name': env_folder.folder_name,
                'type': 'environment',
                'environment': env_folder.environment,
                'children': []
            }
            
            # 해당 환경의 배포일자별 폴더 조회
            deployment_folders = Folder.query.filter_by(
                folder_type='deployment_date',
                parent_folder_id=env_folder.id
            ).all()
            
            for dep_folder in deployment_folders:
                dep_node = {
                    'id': dep_folder.id,
                    'name': dep_folder.folder_name,
                    'type': 'deployment_date',
                    'deployment_date': dep_folder.deployment_date.strftime('%Y-%m-%d'),
                    'children': []
                }
                
                # 해당 배포일자의 테스트 케이스 조회
                test_cases = TestCase.query.filter_by(
                    folder_id=dep_folder.id
                ).all()
                
                for tc in test_cases:
                    tc_node = {
                        'id': tc.id,
                        'name': tc.description[:50] + '...' if len(tc.description) > 50 else tc.description,
                        'type': 'test_case',
                        'status': tc.result_status,
                        'automation_code_path': tc.automation_code_path
                    }
                    dep_node['children'].append(tc_node)
                
                env_node['children'].append(dep_node)
            
            tree.append(env_node)
        
        return jsonify(tree), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
        
        if not file.filename.endswith('.xlsx'):
            return jsonify({'error': '엑셀 파일(.xlsx)만 업로드 가능합니다'}), 400
        
        # 엑셀 파일 읽기
        df = pd.read_excel(file)
        
        created_count = 0
        for _, row in df.iterrows():
            test_case = TestCase(
                project_id=row.get('project_id', 1),
                main_category=row.get('main_category', ''),
                sub_category=row.get('sub_category', ''),
                detail_category=row.get('detail_category', ''),
                pre_condition=row.get('pre_condition', ''),
                description=row.get('description', ''),
                result_status=row.get('result_status', 'N/T'),
                remark=row.get('remark', ''),
                environment=row.get('environment', 'dev'),
                automation_code_path=row.get('automation_code_path', ''),
                automation_code_type=row.get('automation_code_type', '')
            )
            db.session.add(test_case)
            created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'{created_count}개의 테스트 케이스가 업로드되었습니다',
            'created_count': created_count
        }), 201
        
    except Exception as e:
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
                'description': tc.description,
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
        return jsonify({'error': str(e)}), 500

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
        script_type = test_case.automation_code_type
        
        if script_type == 'k6':
            # k6 성능 테스트 실행
            engine = K6ExecutionEngine()
            result = engine.execute_test(script_path, {})
        elif script_type in ['selenium', 'playwright']:
            # UI 테스트 실행
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
        else:
            return jsonify({'error': '지원하지 않는 자동화 코드 타입입니다'}), 400
        
        # 실행 결과 저장
        test_result = TestResult(
            test_case_id=id,
            result='Pass' if result.returncode == 0 else 'Fail',
            environment=test_case.environment,
            execution_duration=0.0,  # 실제 실행 시간 계산 필요
            error_message=result.stderr if result.returncode != 0 else None
        )
        db.session.add(test_result)
        db.session.commit()
        
        return jsonify({
            'message': '자동화 코드 실행 완료',
            'result': 'Pass' if result.returncode == 0 else 'Fail',
            'output': result.stdout,
            'error': result.stderr
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def init_db():
    """데이터베이스 초기화 및 기본 데이터 생성"""
    with app.app_context():
        # 현재 사용 중인 데이터베이스 확인
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'postgresql' in db_uri:
            print("Neon PostgreSQL 데이터베이스 초기화 시작...")
            # PostgreSQL의 경우 기존 테이블이 있으므로 테이블 생성 건너뛰기
            print("기존 테이블 사용 (마이그레이션된 데이터 활용)")
        elif 'sqlite' in db_uri:
            print("SQLite 데이터베이스 초기화 시작...")
            # SQLite의 경우 테이블 생성
            db.create_all()
            print("데이터베이스 테이블 생성 완료")
        else:
            print("데이터베이스 초기화 시작...")
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
        
        # 기본 폴더가 없으면 생성
        if not Folder.query.first():
            default_folder = Folder(
                folder_name="기본 폴더",
                folder_type="environment",
                environment="dev",
                deployment_date=datetime.utcnow().date()
            )
            db.session.add(default_folder)
            db.session.commit()
            print("기본 폴더가 생성되었습니다.")
        
        # 기본 대시보드 요약이 없으면 생성
        if not DashboardSummary.query.first():
            default_summary = DashboardSummary(
                environment="dev",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                pass_rate=0.0
            )
            db.session.add(default_summary)
            db.session.commit()
            print("기본 대시보드 요약이 생성되었습니다.")
        
        if 'postgresql' in db_uri:
            print("Neon PostgreSQL 데이터베이스 초기화 완료!")
        elif 'sqlite' in db_uri:
            print("SQLite 데이터베이스 초기화 완료!")
        else:
            print("데이터베이스 초기화 완료!")

# 헬스체크 엔드포인트 추가
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'message': 'Test Platform Backend is running - Auto Deploy Test',
        'version': '1.0.1',
        'timestamp': datetime.now().isoformat(),
        'deploy_test': 'GitHub Actions CI/CD working!'
    }), 200

# Flask 서버 실행
if __name__ == '__main__':
    init_db()  # 데이터베이스 초기화
    app.run(host='0.0.0.0', port=8000, debug=True)

