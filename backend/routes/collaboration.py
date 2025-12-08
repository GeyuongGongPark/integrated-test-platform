"""
협업 및 워크플로우 API
댓글, 멘션, 워크플로우 관리
"""
from flask import Blueprint, request, jsonify
from models import db, Comment, Mention, Workflow, WorkflowStep, WorkflowState
from utils.cors import add_cors_headers
from utils.auth_decorators import user_required, guest_allowed
from utils.logger import get_logger
from services.collaboration_service import collaboration_service, workflow_service

logger = get_logger(__name__)

collaboration_bp = Blueprint('collaboration', __name__)

# ========== 댓글 API ==========

@collaboration_bp.route('/comments', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_comments():
    """댓글 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id', type=int)
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        if not entity_type or not entity_id:
            response = jsonify({'error': 'entity_type과 entity_id는 필수입니다'})
            return add_cors_headers(response), 400
        
        comments = collaboration_service.get_comments(entity_type, entity_id, include_deleted)
        
        response = jsonify(comments)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"댓글 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@collaboration_bp.route('/comments', methods=['POST', 'OPTIONS'])
@user_required
def create_comment():
    """댓글 생성"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('entity_type') or not data.get('entity_id') or not data.get('content'):
            response = jsonify({'error': 'entity_type, entity_id, content는 필수입니다'})
            return add_cors_headers(response), 400
        
        comment = collaboration_service.create_comment(
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
            content=data['content'],
            author_id=request.user.id,
            parent_comment_id=data.get('parent_comment_id')
        )
        
        response = jsonify({
            'message': '댓글이 생성되었습니다',
            'comment': comment.to_dict()
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        logger.error(f"댓글 생성 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@collaboration_bp.route('/comments/<int:comment_id>', methods=['PUT', 'OPTIONS'])
@user_required
def update_comment(comment_id):
    """댓글 수정"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('content'):
            response = jsonify({'error': 'content는 필수입니다'})
            return add_cors_headers(response), 400
        
        comment = collaboration_service.update_comment(
            comment_id=comment_id,
            content=data['content'],
            user_id=request.user.id
        )
        
        response = jsonify({
            'message': '댓글이 수정되었습니다',
            'comment': comment.to_dict()
        })
        return add_cors_headers(response), 200
        
    except PermissionError as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 403
    except Exception as e:
        logger.error(f"댓글 수정 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@collaboration_bp.route('/comments/<int:comment_id>', methods=['DELETE', 'OPTIONS'])
@user_required
def delete_comment(comment_id):
    """댓글 삭제"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        comment = collaboration_service.delete_comment(
            comment_id=comment_id,
            user_id=request.user.id
        )
        
        response = jsonify({'message': '댓글이 삭제되었습니다'})
        return add_cors_headers(response), 200
        
    except PermissionError as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 403
    except Exception as e:
        logger.error(f"댓글 삭제 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# ========== 멘션 API ==========

@collaboration_bp.route('/mentions', methods=['GET', 'OPTIONS'])
@user_required
def get_mentions():
    """사용자 멘션 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        is_read = request.args.get('is_read')
        if is_read is not None:
            is_read = is_read.lower() == 'true'
        
        mentions = collaboration_service.get_user_mentions(request.user.id, is_read)
        
        response = jsonify(mentions)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"멘션 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@collaboration_bp.route('/mentions/<int:mention_id>/read', methods=['POST', 'OPTIONS'])
@user_required
def mark_mention_as_read(mention_id):
    """멘션 읽음 처리"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        mention = collaboration_service.mark_mention_as_read(mention_id, request.user.id)
        
        response = jsonify({
            'message': '멘션이 읽음 처리되었습니다',
            'mention': mention.to_dict()
        })
        return add_cors_headers(response), 200
        
    except PermissionError as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 403
    except Exception as e:
        logger.error(f"멘션 읽음 처리 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# ========== 워크플로우 API ==========

@collaboration_bp.route('/workflows', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_workflows():
    """워크플로우 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        workflow_type = request.args.get('workflow_type')
        project_id = request.args.get('project_id', type=int)
        is_active = request.args.get('is_active')
        
        query = Workflow.query
        
        if workflow_type:
            query = query.filter(Workflow.workflow_type == workflow_type)
        if project_id:
            query = query.filter(Workflow.project_id == project_id)
        if is_active is not None:
            query = query.filter(Workflow.is_active == (is_active.lower() == 'true'))
        
        workflows = query.order_by(Workflow.created_at.desc()).all()
        
        data = [w.to_dict() for w in workflows]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"워크플로우 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@collaboration_bp.route('/workflows/<int:id>', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_workflow(id):
    """워크플로우 상세 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        workflow = Workflow.query.get_or_404(id)
        
        response = jsonify(workflow.to_dict())
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"워크플로우 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@collaboration_bp.route('/workflows', methods=['POST', 'OPTIONS'])
@user_required
def create_workflow():
    """워크플로우 생성"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('workflow_type') or not data.get('initial_status') or not data.get('steps'):
            response = jsonify({'error': 'name, workflow_type, initial_status, steps는 필수입니다'})
            return add_cors_headers(response), 400
        
        workflow = workflow_service.create_workflow(
            name=data['name'],
            workflow_type=data['workflow_type'],
            initial_status=data['initial_status'],
            steps=data['steps'],
            created_by=request.user.id,
            project_id=data.get('project_id'),
            description=data.get('description')
        )
        
        response = jsonify({
            'message': '워크플로우가 생성되었습니다',
            'workflow': workflow.to_dict()
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        logger.error(f"워크플로우 생성 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@collaboration_bp.route('/workflows/<int:id>', methods=['PUT', 'OPTIONS'])
@user_required
def update_workflow(id):
    """워크플로우 수정"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        workflow = Workflow.query.get_or_404(id)
        data = request.get_json()
        
        if 'name' in data:
            workflow.name = data['name']
        if 'description' in data:
            workflow.description = data['description']
        if 'is_active' in data:
            workflow.is_active = data['is_active']
        
        db.session.commit()
        
        response = jsonify({
            'message': '워크플로우가 수정되었습니다',
            'workflow': workflow.to_dict()
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"워크플로우 수정 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@collaboration_bp.route('/workflows/<int:id>/apply', methods=['POST', 'OPTIONS'])
@user_required
def apply_workflow(id):
    """엔티티에 워크플로우 적용"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('entity_type') or not data.get('entity_id'):
            response = jsonify({'error': 'entity_type과 entity_id는 필수입니다'})
            return add_cors_headers(response), 400
        
        state = workflow_service.apply_workflow_to_entity(
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
            workflow_id=id
        )
        
        response = jsonify({
            'message': '워크플로우가 적용되었습니다',
            'state': state.to_dict()
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"워크플로우 적용 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@collaboration_bp.route('/workflows/transition', methods=['POST', 'OPTIONS'])
@user_required
def transition_workflow():
    """워크플로우 상태 전환"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('entity_type') or not data.get('entity_id') or not data.get('next_status'):
            response = jsonify({'error': 'entity_type, entity_id, next_status는 필수입니다'})
            return add_cors_headers(response), 400
        
        state = workflow_service.transition_workflow_state(
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
            next_status=data['next_status'],
            user_id=request.user.id,
            user_role=getattr(request.user, 'role', None)
        )
        
        response = jsonify({
            'message': '워크플로우 상태가 전환되었습니다',
            'state': state.to_dict()
        })
        return add_cors_headers(response), 200
        
    except PermissionError as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 403
    except Exception as e:
        logger.error(f"워크플로우 상태 전환 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@collaboration_bp.route('/workflows/state', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_workflow_state():
    """엔티티의 워크플로우 상태 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id', type=int)
        
        if not entity_type or not entity_id:
            response = jsonify({'error': 'entity_type과 entity_id는 필수입니다'})
            return add_cors_headers(response), 400
        
        state = workflow_service.get_entity_workflow_state(entity_type, entity_id)
        
        if state:
            response = jsonify(state)
        else:
            response = jsonify({'message': '워크플로우가 적용되지 않았습니다'})
        
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"워크플로우 상태 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

