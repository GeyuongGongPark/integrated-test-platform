"""
테스트 의존성 관리 API
"""
from flask import Blueprint, request, jsonify
from models import db, TestDependency, TestCase
from utils.cors import add_cors_headers
from utils.auth_decorators import user_required, guest_allowed
from utils.logger import get_logger
from services.dependency_service import dependency_service

logger = get_logger(__name__)

dependencies_bp = Blueprint('dependencies', __name__)

@dependencies_bp.route('/dependencies', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_dependencies():
    """의존성 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        test_case_id = request.args.get('test_case_id', type=int)
        depends_on_test_case_id = request.args.get('depends_on_test_case_id', type=int)
        
        query = TestDependency.query.filter_by(enabled=True)
        
        if test_case_id:
            query = query.filter(TestDependency.test_case_id == test_case_id)
        if depends_on_test_case_id:
            query = query.filter(TestDependency.depends_on_test_case_id == depends_on_test_case_id)
        
        dependencies = query.order_by(TestDependency.priority.asc()).all()
        
        data = [d.to_dict() for d in dependencies]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"의존성 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@dependencies_bp.route('/dependencies', methods=['POST', 'OPTIONS'])
@user_required
def create_dependency():
    """의존성 생성"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('test_case_id') or not data.get('depends_on_test_case_id'):
            response = jsonify({'error': 'test_case_id와 depends_on_test_case_id는 필수입니다'})
            return add_cors_headers(response), 400
        
        dependency = dependency_service.create_dependency(
            test_case_id=data['test_case_id'],
            depends_on_test_case_id=data['depends_on_test_case_id'],
            dependency_type=data.get('dependency_type', 'required'),
            condition=data.get('condition'),
            priority=data.get('priority', 1)
        )
        
        response = jsonify({
            'message': '의존성이 생성되었습니다',
            'dependency': dependency.to_dict()
        })
        return add_cors_headers(response), 201
        
    except ValueError as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 400
    except Exception as e:
        logger.error(f"의존성 생성 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@dependencies_bp.route('/dependencies/<int:id>', methods=['PUT', 'OPTIONS'])
@user_required
def update_dependency(id):
    """의존성 수정"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        dependency = TestDependency.query.get_or_404(id)
        data = request.get_json()
        
        import json
        if 'dependency_type' in data:
            dependency.dependency_type = data['dependency_type']
        if 'condition' in data:
            dependency.condition = json.dumps(data['condition']) if data['condition'] else None
        if 'priority' in data:
            dependency.priority = data['priority']
        if 'enabled' in data:
            dependency.enabled = data['enabled']
        
        db.session.commit()
        
        response = jsonify({
            'message': '의존성이 수정되었습니다',
            'dependency': dependency.to_dict()
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"의존성 수정 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@dependencies_bp.route('/dependencies/<int:id>', methods=['DELETE', 'OPTIONS'])
@user_required
def delete_dependency(id):
    """의존성 삭제"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        dependency = TestDependency.query.get_or_404(id)
        
        db.session.delete(dependency)
        db.session.commit()
        
        response = jsonify({'message': '의존성이 삭제되었습니다'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"의존성 삭제 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@dependencies_bp.route('/dependencies/graph', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_dependency_graph():
    """의존성 그래프 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        test_case_ids = request.args.getlist('test_case_ids', type=int)
        if not test_case_ids:
            test_case_ids = None
        
        graph = dependency_service.get_dependency_graph(test_case_ids)
        
        response = jsonify(graph)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"의존성 그래프 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@dependencies_bp.route('/dependencies/execution-order', methods=['POST', 'OPTIONS'])
@guest_allowed
def get_execution_order():
    """테스트 케이스 실행 순서 계산"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('test_case_ids'):
            response = jsonify({'error': 'test_case_ids는 필수입니다'})
            return add_cors_headers(response), 400
        
        test_case_ids = data['test_case_ids']
        
        execution_order = dependency_service.get_execution_order(test_case_ids)
        
        # 테스트 케이스 정보 포함
        test_cases = TestCase.query.filter(TestCase.id.in_(execution_order)).all()
        test_case_map = {tc.id: tc.to_dict() for tc in test_cases}
        
        ordered_test_cases = [
            test_case_map.get(test_id, {'id': test_id, 'name': 'Unknown'})
            for test_id in execution_order
        ]
        
        response = jsonify({
            'execution_order': execution_order,
            'test_cases': ordered_test_cases
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"실행 순서 계산 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@dependencies_bp.route('/dependencies/testcases/<int:test_case_id>/check', methods=['GET', 'OPTIONS'])
@guest_allowed
def check_dependency_conditions(test_case_id):
    """테스트 케이스의 의존성 조건 확인"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        conditions = dependency_service.check_dependency_conditions(test_case_id)
        
        response = jsonify(conditions)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"의존성 조건 확인 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@dependencies_bp.route('/dependencies/testcases/<int:test_case_id>/dependencies', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_test_case_dependencies(test_case_id):
    """테스트 케이스가 의존하는 테스트 케이스 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        dependencies = dependency_service.get_dependencies(test_case_id)
        
        response = jsonify(dependencies)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"의존성 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@dependencies_bp.route('/dependencies/testcases/<int:test_case_id>/dependent', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_dependent_tests(test_case_id):
    """특정 테스트 케이스에 의존하는 테스트 케이스 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        dependent_tests = dependency_service.get_dependent_tests(test_case_id)
        
        response = jsonify(dependent_tests)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"의존 테스트 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

