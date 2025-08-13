from flask import Blueprint, request, jsonify
from models import db, PerformanceTest, TestResult, TestExecution
from utils.cors import add_cors_headers
from engines.k6_engine import k6_engine
import json
from datetime import datetime
import time
import os

# Blueprint 생성
performance_bp = Blueprint('performance', __name__)

# 새로운 성능 테스트 API 엔드포인트들
@performance_bp.route('/performance-tests', methods=['GET'])
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
    response = jsonify(data)
    return add_cors_headers(response), 200

@performance_bp.route('/performance-tests', methods=['POST'])
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
        response = jsonify({'message': '성능 테스트 생성 완료', 'id': pt.id})
        return add_cors_headers(response), 201
    except Exception as e:
        db.session.rollback()
        response = jsonify({'error': f'데이터베이스 오류: {str(e)}'})
        return add_cors_headers(response), 500

@performance_bp.route('/performance-tests/<int:id>', methods=['GET'])
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
    response = jsonify(data)
    return add_cors_headers(response), 200

@performance_bp.route('/performance-tests/<int:id>', methods=['PUT'])
def update_performance_test(id):
    pt = PerformanceTest.query.get_or_404(id)
    data = request.get_json()
    
    pt.name = data.get('name', pt.name)
    pt.description = data.get('description', pt.description)
    pt.k6_script_path = data.get('k6_script_path', pt.k6_script_path)
    pt.environment = data.get('environment', pt.environment)
    pt.parameters = json.dumps(data.get('parameters', {}))
    
    db.session.commit()
    response = jsonify({'message': '성능 테스트 업데이트 완료'})
    return add_cors_headers(response), 200

@performance_bp.route('/performance-tests/<int:id>', methods=['DELETE'])
def delete_performance_test(id):
    pt = PerformanceTest.query.get_or_404(id)
    db.session.delete(pt)
    db.session.commit()
    response = jsonify({'message': '성능 테스트 삭제 완료'})
    return add_cors_headers(response), 200

@performance_bp.route('/performance-tests/<int:id>/execute', methods=['POST'])
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
        perf_result = TestResult(
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
    
    response = jsonify({
        'message': '성능 테스트 실행 완료',
        'execution_id': execution.id,
        'result': result
    })
    return add_cors_headers(response), 200

@performance_bp.route('/performance-tests/<int:id>/results', methods=['GET'])
def get_performance_test_results(id):
    results = TestResult.query.filter_by(performance_test_id=id).all()
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
    response = jsonify(data)
    return add_cors_headers(response), 200

@performance_bp.route('/test-executions', methods=['GET'])
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
    response = jsonify(data)
    return add_cors_headers(response), 200

@performance_bp.route('/test-executions', methods=['POST'])
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
    
    response = jsonify({'message': '테스트 실행 생성 완료', 'id': execution.id})
    return add_cors_headers(response), 201 