"""
CI/CD 통합 API
GitHub Actions, Jenkins 등과의 통합 처리
"""
from flask import Blueprint, request, jsonify
from models import db, CICDIntegration, CICDExecution
from utils.cors import add_cors_headers
from utils.auth_decorators import user_required, admin_required, guest_allowed
from utils.logger import get_logger
from services.cicd_service import cicd_service
import json

logger = get_logger(__name__)

cicd_bp = Blueprint('cicd', __name__)

@cicd_bp.route('/cicd/integrations', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_integrations():
    """CI/CD 통합 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        integrations = CICDIntegration.query.order_by(CICDIntegration.created_at.desc()).all()
        data = [integration.to_dict() for integration in integrations]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"통합 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@cicd_bp.route('/cicd/integrations/<int:id>', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_integration(id):
    """CI/CD 통합 상세 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        integration = CICDIntegration.query.get_or_404(id)
        data = integration.to_dict()
        
        # 보안상 webhook_secret은 제외
        if 'webhook_secret' in data:
            del data['webhook_secret']
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"통합 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@cicd_bp.route('/cicd/integrations', methods=['POST', 'OPTIONS'])
@user_required
def create_integration():
    """CI/CD 통합 생성"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name'):
            response = jsonify({'error': 'name은 필수입니다'})
            return add_cors_headers(response), 400
        
        if not data.get('integration_type'):
            response = jsonify({'error': 'integration_type은 필수입니다'})
            return add_cors_headers(response), 400
        
        integration = CICDIntegration(
            name=data['name'],
            integration_type=data['integration_type'],
            webhook_url=data.get('webhook_url'),
            webhook_secret=data.get('webhook_secret'),
            config=json.dumps(data.get('config', {})),
            enabled=data.get('enabled', True),
            active=data.get('active', True),
            trigger_on_push=data.get('trigger_on_push', True),
            trigger_on_pr=data.get('trigger_on_pr', True),
            trigger_on_tag=data.get('trigger_on_tag', False),
            test_case_filter=json.dumps(data.get('test_case_filter', {})),
            created_by=request.user.id
        )
        
        db.session.add(integration)
        db.session.commit()
        
        response = jsonify({
            'message': 'CI/CD 통합이 생성되었습니다',
            'id': integration.id,
            'integration': integration.to_dict()
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        logger.error(f"통합 생성 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@cicd_bp.route('/cicd/integrations/<int:id>', methods=['PUT', 'OPTIONS'])
@user_required
def update_integration(id):
    """CI/CD 통합 수정"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        integration = CICDIntegration.query.get_or_404(id)
        data = request.get_json()
        
        # 수정 가능한 필드 업데이트
        if 'name' in data:
            integration.name = data['name']
        if 'webhook_url' in data:
            integration.webhook_url = data['webhook_url']
        if 'webhook_secret' in data:
            integration.webhook_secret = data['webhook_secret']
        if 'config' in data:
            integration.config = json.dumps(data['config'])
        if 'enabled' in data:
            integration.enabled = data['enabled']
        if 'active' in data:
            integration.active = data['active']
        if 'trigger_on_push' in data:
            integration.trigger_on_push = data['trigger_on_push']
        if 'trigger_on_pr' in data:
            integration.trigger_on_pr = data['trigger_on_pr']
        if 'trigger_on_tag' in data:
            integration.trigger_on_tag = data['trigger_on_tag']
        if 'test_case_filter' in data:
            integration.test_case_filter = json.dumps(data['test_case_filter'])
        
        db.session.commit()
        
        response = jsonify({
            'message': 'CI/CD 통합이 수정되었습니다',
            'integration': integration.to_dict()
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"통합 수정 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@cicd_bp.route('/cicd/integrations/<int:id>', methods=['DELETE', 'OPTIONS'])
@user_required
def delete_integration(id):
    """CI/CD 통합 삭제"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        integration = CICDIntegration.query.get_or_404(id)
        
        db.session.delete(integration)
        db.session.commit()
        
        response = jsonify({'message': 'CI/CD 통합이 삭제되었습니다'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"통합 삭제 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@cicd_bp.route('/cicd/webhook/github', methods=['POST', 'OPTIONS'])
def github_webhook():
    """GitHub 웹훅 수신"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # GitHub 이벤트 타입 확인
        event_type = request.headers.get('X-GitHub-Event')
        signature = request.headers.get('X-Hub-Signature-256')
        
        payload = request.get_json()
        
        if not payload:
            response = jsonify({'error': '페이로드가 없습니다'})
            return add_cors_headers(response), 400
        
        # 활성화된 GitHub 통합 찾기
        integrations = CICDIntegration.query.filter_by(
            integration_type='github',
            enabled=True,
            active=True
        ).all()
        
        if not integrations:
            logger.info("활성화된 GitHub 통합이 없습니다")
            response = jsonify({'message': '활성화된 통합이 없습니다'})
            return add_cors_headers(response), 200
        
        # 각 통합에 대해 처리
        results = []
        for integration in integrations:
            try:
                execution = cicd_service.handle_github_webhook(
                    payload,
                    signature,
                    integration
                )
                if execution:
                    results.append({
                        'integration_id': integration.id,
                        'execution_id': execution.id,
                        'status': 'triggered'
                    })
            except Exception as e:
                logger.error(f"통합 {integration.id} 처리 오류: {str(e)}")
                results.append({
                    'integration_id': integration.id,
                    'status': 'error',
                    'error': str(e)
                })
        
        response = jsonify({
            'message': '웹훅이 처리되었습니다',
            'event_type': event_type,
            'results': results
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"GitHub 웹훅 처리 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@cicd_bp.route('/cicd/webhook/jenkins', methods=['POST', 'OPTIONS'])
def jenkins_webhook():
    """Jenkins 웹훅 수신"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        payload = request.get_json()
        
        if not payload:
            response = jsonify({'error': '페이로드가 없습니다'})
            return add_cors_headers(response), 400
        
        # 활성화된 Jenkins 통합 찾기
        integrations = CICDIntegration.query.filter_by(
            integration_type='jenkins',
            enabled=True,
            active=True
        ).all()
        
        if not integrations:
            logger.info("활성화된 Jenkins 통합이 없습니다")
            response = jsonify({'message': '활성화된 통합이 없습니다'})
            return add_cors_headers(response), 200
        
        # 각 통합에 대해 처리
        results = []
        for integration in integrations:
            try:
                execution = cicd_service.handle_jenkins_webhook(
                    payload,
                    integration
                )
                if execution:
                    results.append({
                        'integration_id': integration.id,
                        'execution_id': execution.id,
                        'status': 'triggered'
                    })
            except Exception as e:
                logger.error(f"통합 {integration.id} 처리 오류: {str(e)}")
                results.append({
                    'integration_id': integration.id,
                    'status': 'error',
                    'error': str(e)
                })
        
        response = jsonify({
            'message': '웹훅이 처리되었습니다',
            'results': results
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"Jenkins 웹훅 처리 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@cicd_bp.route('/cicd/executions', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_executions():
    """CI/CD 실행 기록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 필터링 파라미터
        integration_id = request.args.get('integration_id', type=int)
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        
        query = CICDExecution.query
        
        if integration_id:
            query = query.filter(CICDExecution.integration_id == integration_id)
        if status:
            query = query.filter(CICDExecution.status == status)
        
        executions = query.order_by(CICDExecution.started_at.desc()).limit(limit).all()
        
        data = [execution.to_dict() for execution in executions]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"실행 기록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@cicd_bp.route('/cicd/executions/<int:id>', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_execution(id):
    """CI/CD 실행 기록 상세 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        execution = CICDExecution.query.get_or_404(id)
        data = execution.to_dict()
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"실행 기록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@cicd_bp.route('/cicd/executions/<int:id>/update-results', methods=['POST', 'OPTIONS'])
@user_required
def update_execution_results(id):
    """실행 결과 업데이트 (Celery 태스크에서 호출)"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        test_results = data.get('test_results', [])
        
        if cicd_service.update_execution_with_results(id, test_results):
            response = jsonify({'message': '실행 결과가 업데이트되었습니다'})
            return add_cors_headers(response), 200
        else:
            response = jsonify({'error': '실행 기록을 찾을 수 없습니다'})
            return add_cors_headers(response), 404
        
    except Exception as e:
        logger.error(f"실행 결과 업데이트 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@cicd_bp.route('/cicd/integrations/<int:id>/test', methods=['POST', 'OPTIONS'])
@user_required
def test_integration(id):
    """CI/CD 통합 테스트 (수동 트리거)"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        integration = CICDIntegration.query.get_or_404(id)
        
        # 테스트 실행 기록 생성
        execution = CICDExecution(
            integration_id=integration.id,
            trigger_type='manual',
            trigger_source=integration.integration_type,
            status='running'
        )
        db.session.add(execution)
        db.session.commit()
        
        # 테스트 케이스 필터 적용
        test_case_ids = cicd_service._get_test_case_ids_from_filter(integration.test_case_filter)
        
        if test_case_ids:
            from tasks import execute_test_case_batch
            task = execute_test_case_batch.delay(
                test_case_ids,
                environment='dev',
                max_workers=5
            )
            
            response = jsonify({
                'message': '테스트가 실행되었습니다',
                'execution_id': execution.id,
                'task_id': task.id,
                'test_case_count': len(test_case_ids)
            })
            return add_cors_headers(response), 200
        else:
            execution.status = 'completed'
            execution.error_message = '실행할 테스트 케이스가 없습니다'
            db.session.commit()
            
            response = jsonify({'error': '실행할 테스트 케이스가 없습니다'})
            return add_cors_headers(response), 400
        
    except Exception as e:
        logger.error(f"통합 테스트 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

