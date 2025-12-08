"""
테스트 실행 큐 관리 API
병렬 실행 및 큐 상태 관리
"""
from flask import Blueprint, request, jsonify
from models import db, TestCase
from utils.cors import add_cors_headers
from utils.auth_decorators import user_required, admin_required, guest_allowed
from utils.logger import get_logger
from celery_app import celery_app
from tasks import execute_test_case, execute_test_case_batch, execute_automation_test, execute_performance_test
import json

logger = get_logger(__name__)

queue_bp = Blueprint('queue', __name__)

@queue_bp.route('/queue/testcases/<int:id>/execute', methods=['POST', 'OPTIONS'])
@user_required
def queue_test_case_execution(id):
    """테스트 케이스를 큐에 추가하여 비동기 실행"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        test_case = TestCase.query.get_or_404(id)
        data = request.get_json() or {}
        
        environment = data.get('environment', 'dev')
        execution_parameters = data.get('execution_parameters')
        
        # Celery 태스크에 추가
        task = execute_test_case.delay(id, environment, execution_parameters)
        
        response = jsonify({
            'message': '테스트 케이스가 실행 큐에 추가되었습니다',
            'task_id': task.id,
            'test_case_id': id,
            'test_case_name': test_case.name,
            'status': 'queued'
        })
        return add_cors_headers(response), 202  # Accepted
        
    except Exception as e:
        logger.error(f"큐 추가 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@queue_bp.route('/queue/testcases/batch-execute', methods=['POST', 'OPTIONS'])
@user_required
def queue_batch_execution():
    """여러 테스트 케이스를 병렬로 실행"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        test_case_ids = data.get('test_case_ids', [])
        
        if not test_case_ids or not isinstance(test_case_ids, list):
            response = jsonify({'error': 'test_case_ids는 배열이어야 합니다'})
            return add_cors_headers(response), 400
        
        if len(test_case_ids) == 0:
            response = jsonify({'error': '실행할 테스트 케이스가 없습니다'})
            return add_cors_headers(response), 400
        
        environment = data.get('environment', 'dev')
        max_workers = data.get('max_workers', 5)
        
        # 배치 실행 태스크 추가
        task = execute_test_case_batch.delay(test_case_ids, environment, max_workers)
        
        response = jsonify({
            'message': f'{len(test_case_ids)}개의 테스트 케이스가 병렬 실행 큐에 추가되었습니다',
            'task_id': task.id,
            'test_case_ids': test_case_ids,
            'max_workers': max_workers,
            'status': 'queued'
        })
        return add_cors_headers(response), 202
        
    except Exception as e:
        logger.error(f"배치 실행 큐 추가 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@queue_bp.route('/queue/tasks/<task_id>', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_task_status(task_id):
    """태스크 상태 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        task = celery_app.AsyncResult(task_id)
        
        response_data = {
            'task_id': task_id,
            'status': task.status,
            'ready': task.ready(),
            'successful': task.successful() if task.ready() else None,
            'failed': task.failed() if task.ready() else None
        }
        
        if task.ready():
            if task.successful():
                response_data['result'] = task.result
            else:
                response_data['error'] = str(task.info) if task.info else 'Unknown error'
        else:
            # 진행 중인 경우
            if hasattr(task, 'info') and task.info:
                if isinstance(task.info, dict):
                    response_data['progress'] = task.info.get('current', 0)
                    response_data['total'] = task.info.get('total', 0)
                else:
                    response_data['info'] = str(task.info)
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"태스크 상태 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@queue_bp.route('/queue/tasks/<task_id>/cancel', methods=['POST', 'OPTIONS'])
@user_required
def cancel_task(task_id):
    """태스크 취소"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        celery_app.control.revoke(task_id, terminate=True)
        
        response = jsonify({
            'message': '태스크가 취소되었습니다',
            'task_id': task_id
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"태스크 취소 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@queue_bp.route('/queue/stats', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_queue_stats():
    """큐 통계 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 활성 워커 정보
        inspect = celery_app.control.inspect()
        
        active_workers = inspect.active()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()
        stats = inspect.stats()
        
        # 큐별 작업 수
        queue_stats = {}
        if active_workers:
            for worker, tasks in active_workers.items():
                for task in tasks:
                    queue_name = task.get('delivery_info', {}).get('routing_key', 'unknown')
                    queue_stats[queue_name] = queue_stats.get(queue_name, 0) + 1
        
        response_data = {
            'active_workers': len(active_workers) if active_workers else 0,
            'active_tasks': sum(len(tasks) for tasks in active_workers.values()) if active_workers else 0,
            'scheduled_tasks': sum(len(tasks) for tasks in scheduled_tasks.values()) if scheduled_tasks else 0,
            'reserved_tasks': sum(len(tasks) for tasks in reserved_tasks.values()) if reserved_tasks else 0,
            'queue_stats': queue_stats,
            'worker_stats': stats if stats else {}
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"큐 통계 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@queue_bp.route('/queue/workers', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_workers():
    """워커 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        stats = inspect.stats()
        
        workers = []
        if active_workers:
            for worker_name in active_workers.keys():
                worker_info = {
                    'name': worker_name,
                    'active_tasks': len(active_workers.get(worker_name, [])),
                    'stats': stats.get(worker_name, {}) if stats else {}
                }
                workers.append(worker_info)
        
        response = jsonify({
            'workers': workers,
            'total': len(workers)
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"워커 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@queue_bp.route('/queue/purge', methods=['POST', 'OPTIONS'])
@admin_required
def purge_queue():
    """큐 비우기 (관리자만)"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json() or {}
        queue_name = data.get('queue_name', 'test_execution')
        
        # 큐 비우기
        celery_app.control.purge()
        
        response = jsonify({
            'message': f'큐가 비워졌습니다: {queue_name}'
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"큐 비우기 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

