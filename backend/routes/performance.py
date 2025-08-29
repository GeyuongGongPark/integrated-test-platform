from flask import Blueprint, request, jsonify
from models import db, PerformanceTest, TestResult, TestExecution
from utils.cors import add_cors_headers
from utils.auth_decorators import guest_allowed, user_required, admin_required
from engines.k6_engine import k6_engine
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
import json
from datetime import datetime
import time
import os

logger = get_logger(__name__)

# Blueprint 생성
performance_bp = Blueprint('performance', __name__)

# 새로운 성능 테스트 API 엔드포인트들
@performance_bp.route('/performance-tests', methods=['GET'])
@guest_allowed
def get_performance_tests():
    try:
        # 페이징 파라미터 처리
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 페이지 번호와 per_page 유효성 검사
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        # 전체 성능 테스트 수 조회
        total_count = PerformanceTest.query.count()
        
        # 페이징된 성능 테스트 조회
        offset = (page - 1) * per_page
        tests = PerformanceTest.query.offset(offset).limit(per_page).all()
        
        # 총 페이지 수 계산
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        next_num = page + 1 if has_next else None
        prev_num = page - 1 if has_prev else None
        
        data = [{
            'id': pt.id,
            'name': pt.name,
            'description': pt.description,
            'script_path': pt.script_path,
            'environment': pt.environment,
            'parameters': pt.parameters,
            'created_at': pt.created_at,
            'updated_at': pt.updated_at
        } for pt in tests]
        
        # 페이징 정보 포함 응답
        response_data = {
            'items': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev,
                'next_num': next_num,
                'prev_num': prev_num
            }
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@performance_bp.route('/performance-tests', methods=['POST'])
@user_required
def create_performance_test():
    data = request.get_json()
    
    pt = PerformanceTest(
        name=data.get('name'),
        description=data.get('description'),
        script_path=data.get('script_path'),
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
@guest_allowed
def get_performance_test(id):
    pt = PerformanceTest.query.get_or_404(id)
    data = {
        'id': pt.id,
        'name': pt.name,
        'description': pt.description,
        'script_path': pt.script_path,
        'environment': pt.environment,
        'parameters': json.loads(pt.parameters) if pt.parameters else {},
        'created_at': pt.created_at,
        'updated_at': pt.updated_at
    }
    response = jsonify(data)
    return add_cors_headers(response), 200

@performance_bp.route('/performance-tests/<int:id>', methods=['PUT'])
@user_required
def update_performance_test(id):
    pt = PerformanceTest.query.get_or_404(id)
    data = request.get_json()
    
    pt.name = data.get('name', pt.name)
    pt.description = data.get('description', pt.description)
    pt.script_path = data.get('script_path', pt.script_path)
    pt.environment = data.get('environment', pt.environment)
    pt.parameters = json.dumps(data.get('parameters', {}))
    
    db.session.commit()
    response = jsonify({'message': '성능 테스트 업데이트 완료'})
    return add_cors_headers(response), 200

@performance_bp.route('/performance-tests/<int:id>', methods=['DELETE'])
@admin_required
def delete_performance_test(id):
    pt = PerformanceTest.query.get_or_404(id)
    db.session.delete(pt)
    db.session.commit()
    response = jsonify({'message': '성능 테스트 삭제 완료'})
    return add_cors_headers(response), 200

@performance_bp.route('/performance-tests/<int:id>/execute', methods=['POST'])
@user_required
def execute_performance_test(id):
    pt = PerformanceTest.query.get_or_404(id)
    data = request.get_json()
    
    # 환경 변수 설정
    env_vars = data.get('environment_vars', {})
    if pt.parameters:
        try:
            base_params = json.loads(pt.parameters)
            # base_params가 딕셔너리인지 확인하고 안전하게 업데이트
            if isinstance(base_params, dict):
                env_vars.update(base_params)
            else:
                logger.warning(f"pt.parameters is not a dictionary: {type(base_params)}")
                logger.debug(f"pt.parameters content: {pt.parameters}")
                # 기본 환경 변수 설정
                env_vars.update({
                    'BASE_URL': 'http://localhost:3000',
                    'ENVIRONMENT': pt.environment or 'dev'
                })
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error parsing pt.parameters: {e}")
            logger.debug(f"pt.parameters content: {pt.parameters}")
            # 파싱 실패 시 기본 환경 변수 설정
            env_vars.update({
                'BASE_URL': 'http://localhost:3000',
                'ENVIRONMENT': pt.environment or 'dev'
            })
    else:
        # parameters가 없을 때 기본 환경 변수 설정
        env_vars.update({
            'BASE_URL': 'http://localhost:3000',
            'ENVIRONMENT': pt.environment or 'dev'
        })
    
    # k6 테스트 실행
    result = k6_engine.execute_test(pt.script_path, env_vars)
    
    # 실행 결과 저장
    execution = TestExecution(
        performance_test_id=pt.id,
        test_type='performance',
        status=result.get('status', 'Error'),
        result_summary=json.dumps(result)
    )
    
    if result.get('status') == 'Pass':
        # 성능 테스트 결과 저장 - TestResult 모델의 실제 필드 사용
        perf_result = TestResult(
            performance_test_id=pt.id,
            result=result.get('status'),
            execution_time=result.get('execution_time', 0.0),
            environment=pt.environment,
            executed_by='system',
            executed_at=get_kst_now(),
            notes=json.dumps(result)  # 성능 테스트 결과를 notes에 JSON으로 저장
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
        'result': r.result,
        'execution_time': r.execution_time,
        'environment': r.environment,
        'executed_by': r.executed_by,
                    'executed_at': r.executed_at.isoformat() if r.executed_at else None,
        'notes': r.notes
    } for r in results]
    response = jsonify(data)
    return add_cors_headers(response), 200

@performance_bp.route('/test-executions', methods=['GET'])
def get_test_executions():
    try:
        # 페이징 파라미터 처리
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 페이지 번호와 per_page 유효성 검사
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        # 전체 테스트 실행 수 조회
        total_count = TestExecution.query.count()
        
        # 페이징된 테스트 실행 조회
        offset = (page - 1) * per_page
        executions = TestExecution.query.offset(offset).limit(per_page).all()
        
        # 총 페이지 수 계산
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        next_num = page + 1 if has_next else None
        prev_num = page - 1 if has_prev else None
        
        data = [{
            'id': e.id,
            'test_case_id': e.test_case_id,
            'automation_test_id': e.automation_test_id,
            'performance_test_id': e.performance_test_id,
            'test_type': e.test_type,
            'started_at': e.started_at.isoformat() if e.started_at else None,
            'completed_at': e.completed_at.isoformat() if e.completed_at else None,
            'status': e.status,
            'result_summary': json.loads(e.result_summary) if e.result_summary else None
        } for e in executions]
        
        # 페이징 정보 포함 응답
        response_data = {
            'items': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev,
                'next_num': next_num,
                'prev_num': prev_num
            }
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@performance_bp.route('/test-executions', methods=['POST'])
def create_test_execution():
    data = request.get_json()
    
    execution = TestExecution(
        test_case_id=data.get('test_case_id'),
        automation_test_id=data.get('automation_test_id'),
        performance_test_id=data.get('performance_test_id'),
        test_type=data.get('test_type'),
        status=data.get('status', 'Running'),
        result_summary=json.dumps(data.get('result_data', {}))
    )
    
    db.session.add(execution)
    db.session.commit()
    
    response = jsonify({'message': '테스트 실행 생성 완료', 'id': execution.id})
    return add_cors_headers(response), 201 