from flask import Blueprint, request, jsonify
from models import db, AutomationTest, AutomationTestResult
from utils.cors import add_cors_headers
from datetime import datetime
import time

# Blueprint 생성
automation_bp = Blueprint('automation', __name__)

# 자동화 테스트 API
@automation_bp.route('/automation-tests', methods=['GET'])
def get_automation_tests():
    """모든 자동화 테스트 조회"""
    try:
        tests = AutomationTest.query.all()
        response = jsonify([{
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
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/automation-tests', methods=['POST'])
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
        
        response = jsonify({
            'id': new_test.id,
            'name': new_test.name,
            'message': '자동화 테스트가 성공적으로 생성되었습니다.'
        })
        return add_cors_headers(response), 201
    except Exception as e:
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/automation-tests/<int:id>', methods=['GET'])
def get_automation_test(id):
    """특정 자동화 테스트 조회"""
    try:
        test = AutomationTest.query.get_or_404(id)
        response = jsonify({
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
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/automation-tests/<int:id>', methods=['PUT'])
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
        
        response = jsonify({
            'message': '자동화 테스트가 성공적으로 수정되었습니다.'
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/automation-tests/<int:id>', methods=['DELETE'])
def delete_automation_test(id):
    """자동화 테스트 삭제"""
    try:
        test = AutomationTest.query.get_or_404(id)
        db.session.delete(test)
        db.session.commit()
        
        response = jsonify({
            'message': '자동화 테스트가 성공적으로 삭제되었습니다.'
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/automation-tests/<int:id>/execute', methods=['POST'])
def execute_automation_test(id):
    """자동화 테스트 실행"""
    try:
        test = AutomationTest.query.get_or_404(id)
        
        # 실행 시작 시간
        execution_start = datetime.utcnow()
        
        # 실제로는 여기서 자동화 테스트를 실행
        # 현재는 시뮬레이션
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
        
        response = jsonify({
            'message': '자동화 테스트 실행이 완료되었습니다.',
            'test_name': test.name,
            'status': status,
            'execution_duration': execution_duration,
            'result_id': result.id
        })
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/automation-tests/<int:id>/results', methods=['GET'])
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
        
        response = jsonify(result_list)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/automation-tests/<int:id>/results/<int:result_id>', methods=['GET'])
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
        
        response = jsonify(result_data)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500 