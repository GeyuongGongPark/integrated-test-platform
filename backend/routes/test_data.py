"""
테스트 데이터 관리 API
"""
from flask import Blueprint, request, jsonify
from models import db, TestDataSet, TestCaseDataMapping, TestCase
from utils.cors import add_cors_headers
from utils.auth_decorators import user_required, guest_allowed
from utils.logger import get_logger
from services.test_data_service import test_data_service
import json

logger = get_logger(__name__)

test_data_bp = Blueprint('test_data', __name__)

@test_data_bp.route('/test-data/datasets', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_data_sets():
    """데이터 세트 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 필터링 파라미터
        environment = request.args.get('environment')
        tag = request.args.get('tag')
        search = request.args.get('search', '')
        
        query = TestDataSet.query
        
        if environment:
            query = query.filter(TestDataSet.environment == environment)
        if tag:
            query = query.filter(TestDataSet.tags.contains(tag))
        if search:
            query = query.filter(
                db.or_(
                    TestDataSet.name.contains(search),
                    TestDataSet.description.contains(search)
                )
            )
        
        data_sets = query.order_by(TestDataSet.created_at.desc()).all()
        
        data = [ds.to_dict() for ds in data_sets]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"데이터 세트 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/datasets/<int:id>', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_data_set(id):
    """데이터 세트 상세 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data_set = TestDataSet.query.get_or_404(id)
        
        # 마스킹 여부 확인
        include_masked = request.args.get('masked', 'false').lower() == 'true'
        
        data = data_set.to_dict()
        
        # 마스킹된 데이터 반환 여부
        if include_masked and data_set.masking_enabled:
            data['data'] = data_set.get_masked_data()
        else:
            # 원본 데이터 반환 (권한 확인 필요할 수 있음)
            data['data'] = json.loads(data_set.data) if data_set.data else {}
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"데이터 세트 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/datasets', methods=['POST', 'OPTIONS'])
@user_required
def create_data_set():
    """데이터 세트 생성"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name'):
            response = jsonify({'error': 'name은 필수입니다'})
            return add_cors_headers(response), 400
        
        if not data.get('data'):
            response = jsonify({'error': 'data는 필수입니다'})
            return add_cors_headers(response), 400
        
        data_set = test_data_service.create_data_set(
            name=data['name'],
            data=data['data'],
            environment=data.get('environment', 'dev'),
            description=data.get('description'),
            data_type=data.get('data_type', 'json'),
            masking_enabled=data.get('masking_enabled', False),
            masking_rules=data.get('masking_rules'),
            tags=data.get('tags'),
            created_by=request.user.id
        )
        
        response = jsonify({
            'message': '데이터 세트가 생성되었습니다',
            'id': data_set.id,
            'data_set': data_set.to_dict()
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        logger.error(f"데이터 세트 생성 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/datasets/<int:id>', methods=['PUT', 'OPTIONS'])
@user_required
def update_data_set(id):
    """데이터 세트 수정"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data_set = TestDataSet.query.get_or_404(id)
        data = request.get_json()
        
        # 수정 가능한 필드 업데이트
        if 'name' in data:
            data_set.name = data['name']
        if 'description' in data:
            data_set.description = data['description']
        if 'data' in data:
            if isinstance(data['data'], str):
                data_set.data = data['data']
            else:
                data_set.data = json.dumps(data['data'])
        if 'environment' in data:
            data_set.environment = data['environment']
        if 'masking_enabled' in data:
            data_set.masking_enabled = data['masking_enabled']
        if 'masking_rules' in data:
            data_set.masking_rules = json.dumps(data['masking_rules']) if data['masking_rules'] else None
        if 'tags' in data:
            data_set.tags = json.dumps(data['tags']) if data['tags'] else None
        
        db.session.commit()
        
        response = jsonify({
            'message': '데이터 세트가 수정되었습니다',
            'data_set': data_set.to_dict()
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"데이터 세트 수정 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/datasets/<int:id>', methods=['DELETE', 'OPTIONS'])
@user_required
def delete_data_set(id):
    """데이터 세트 삭제"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data_set = TestDataSet.query.get_or_404(id)
        
        # 매핑된 테스트 케이스가 있는지 확인
        mappings = TestCaseDataMapping.query.filter_by(data_set_id=id).count()
        if mappings > 0:
            response = jsonify({
                'error': f'{mappings}개의 테스트 케이스에 매핑되어 있어 삭제할 수 없습니다',
                'mappings_count': mappings
            })
            return add_cors_headers(response), 400
        
        db.session.delete(data_set)
        db.session.commit()
        
        response = jsonify({'message': '데이터 세트가 삭제되었습니다'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"데이터 세트 삭제 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/datasets/<int:id>/versions', methods=['POST', 'OPTIONS'])
@user_required
def create_data_set_version(id):
    """데이터 세트 버전 생성"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('data'):
            response = jsonify({'error': 'data는 필수입니다'})
            return add_cors_headers(response), 400
        
        new_version = test_data_service.create_data_set_version(
            parent_id=id,
            data=data['data'],
            version=data.get('version'),
            created_by=request.user.id
        )
        
        response = jsonify({
            'message': '데이터 세트 버전이 생성되었습니다',
            'id': new_version.id,
            'data_set': new_version.to_dict()
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        logger.error(f"데이터 세트 버전 생성 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/datasets/<int:id>/versions', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_data_set_versions(id):
    """데이터 세트 버전 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 부모 버전과 모든 자식 버전 조회
        parent = TestDataSet.query.get_or_404(id)
        versions = [parent]
        
        # 자식 버전들
        child_versions = TestDataSet.query.filter_by(parent_version_id=id).order_by(
            TestDataSet.created_at.desc()
        ).all()
        versions.extend(child_versions)
        
        data = [v.to_dict() for v in versions]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"데이터 세트 버전 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/testcases/<int:test_case_id>/data', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_test_case_data(test_case_id):
    """테스트 케이스에 매핑된 데이터 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        environment = request.args.get('environment')
        
        data = test_data_service.get_data_for_test_case(test_case_id, environment)
        
        if data:
            response = jsonify({
                'test_case_id': test_case_id,
                'data': data
            })
        else:
            response = jsonify({
                'test_case_id': test_case_id,
                'data': None,
                'message': '매핑된 데이터 세트가 없습니다'
            })
        
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"테스트 케이스 데이터 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/mappings', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_mappings():
    """테스트 케이스-데이터 세트 매핑 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        test_case_id = request.args.get('test_case_id', type=int)
        data_set_id = request.args.get('data_set_id', type=int)
        
        query = TestCaseDataMapping.query
        
        if test_case_id:
            query = query.filter(TestCaseDataMapping.test_case_id == test_case_id)
        if data_set_id:
            query = query.filter(TestCaseDataMapping.data_set_id == data_set_id)
        
        mappings = query.order_by(TestCaseDataMapping.priority.asc()).all()
        
        data = [m.to_dict() for m in mappings]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"매핑 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/mappings', methods=['POST', 'OPTIONS'])
@user_required
def create_mapping():
    """테스트 케이스-데이터 세트 매핑 생성"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('test_case_id'):
            response = jsonify({'error': 'test_case_id는 필수입니다'})
            return add_cors_headers(response), 400
        
        if not data.get('data_set_id'):
            response = jsonify({'error': 'data_set_id는 필수입니다'})
            return add_cors_headers(response), 400
        
        # 중복 확인
        existing = TestCaseDataMapping.query.filter_by(
            test_case_id=data['test_case_id'],
            data_set_id=data['data_set_id']
        ).first()
        
        if existing:
            response = jsonify({'error': '이미 매핑이 존재합니다'})
            return add_cors_headers(response), 400
        
        mapping = TestCaseDataMapping(
            test_case_id=data['test_case_id'],
            data_set_id=data['data_set_id'],
            field_mapping=json.dumps(data.get('field_mapping', {})) if data.get('field_mapping') else None,
            priority=data.get('priority', 1),
            enabled=data.get('enabled', True)
        )
        
        db.session.add(mapping)
        db.session.commit()
        
        response = jsonify({
            'message': '매핑이 생성되었습니다',
            'id': mapping.id,
            'mapping': mapping.to_dict()
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        logger.error(f"매핑 생성 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/mappings/<int:id>', methods=['PUT', 'OPTIONS'])
@user_required
def update_mapping(id):
    """매핑 수정"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        mapping = TestCaseDataMapping.query.get_or_404(id)
        data = request.get_json()
        
        if 'field_mapping' in data:
            mapping.field_mapping = json.dumps(data['field_mapping']) if data['field_mapping'] else None
        if 'priority' in data:
            mapping.priority = data['priority']
        if 'enabled' in data:
            mapping.enabled = data['enabled']
        
        db.session.commit()
        
        response = jsonify({
            'message': '매핑이 수정되었습니다',
            'mapping': mapping.to_dict()
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"매핑 수정 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/mappings/<int:id>', methods=['DELETE', 'OPTIONS'])
@user_required
def delete_mapping(id):
    """매핑 삭제"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        mapping = TestCaseDataMapping.query.get_or_404(id)
        
        db.session.delete(mapping)
        db.session.commit()
        
        response = jsonify({'message': '매핑이 삭제되었습니다'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"매핑 삭제 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@test_data_bp.route('/test-data/generate', methods=['POST', 'OPTIONS'])
@user_required
def generate_dynamic_data():
    """동적 테스트 데이터 생성"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('schema'):
            response = jsonify({'error': 'schema는 필수입니다'})
            return add_cors_headers(response), 400
        
        schema = data['schema']
        count = data.get('count', 1)
        
        generated_data = test_data_service.generate_dynamic_data(schema, count)
        
        response = jsonify({
            'message': f'{count}개의 데이터가 생성되었습니다',
            'data': generated_data,
            'count': len(generated_data)
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"동적 데이터 생성 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

