from flask import Blueprint, request, jsonify, send_from_directory
from models import db, AutomationTest, TestResult
from utils.cors import add_cors_headers
from utils.auth_decorators import guest_allowed, user_required, admin_required
from utils.timezone_utils import get_kst_now
from datetime import datetime
import time
import os
import glob
from pathlib import Path
from urllib.parse import unquote
import json

# Blueprint 생성
automation_bp = Blueprint('automation', __name__)

# 스크린샷 관련 설정
SCREENSHOT_BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'test-scripts')

# 자동화 테스트 API
@automation_bp.route('/automation-tests', methods=['GET'])
@guest_allowed
def get_automation_tests():
    """모든 자동화 테스트 조회"""
    try:
        tests = AutomationTest.query.all()
        
        response_data = [{
            'id': test.id,
            'name': test.name,
            'description': test.description,
            'test_type': test.test_type,
            'script_path': test.script_path,
            'environment': test.environment,
            'parameters': test.parameters,
            'created_at': test.created_at.isoformat() if test.created_at else None,
            'updated_at': test.updated_at.isoformat() if test.updated_at else None
        } for test in tests]
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/automation-tests', methods=['POST'])
@user_required
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
@guest_allowed
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
            'created_at': test.created_at.isoformat() if test.created_at else None,
            'updated_at': test.updated_at.isoformat() if test.updated_at else None
        })
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/automation-tests/<int:id>', methods=['PUT'])
@user_required
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
        test.updated_at = get_kst_now()
        
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
@admin_required
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
@user_required
def execute_automation_test(id):
    """자동화 테스트 실행"""
    try:
        test = AutomationTest.query.get_or_404(id)
        
        # 실행 시작 시간
        execution_start = get_kst_now()
        
        # 실제로는 여기서 자동화 테스트를 실행
        # 현재는 시뮬레이션
        time.sleep(2)  # 실행 시간 시뮬레이션
        
        # 실행 종료 시간
        execution_end = get_kst_now()
        execution_duration = (execution_end - execution_start).total_seconds()
        
        # 시뮬레이션된 결과 (실제로는 테스트 실행 결과)
        status = 'Pass'  # 또는 'Fail', 'Skip', 'Error'
        output = f"테스트 '{test.name}' 실행 완료"
        error_message = None
        
        # TestResult 모델을 사용하여 결과 저장
        result = TestResult(
            automation_test_id=test.id,
            result=status,
            execution_time=execution_duration,
            environment=test.environment,
            executed_by='system',  # 또는 실제 사용자 ID
            executed_at=execution_end,
            notes=output
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
        # TestResult 모델에서 자동화 테스트 결과 조회
        results = TestResult.query.filter_by(
            automation_test_id=id
        ).order_by(TestResult.executed_at.desc()).all()
        
        result_list = []
        for result in results:
            result_data = {
                'id': result.id,
                'automation_test_id': result.automation_test_id,
                'result': result.result,
                'execution_time': result.execution_time,
                'environment': result.environment,
                'executed_by': result.executed_by,
                'executed_at': result.executed_at.isoformat() if result.executed_at else None,
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
        # TestResult 모델에서 특정 결과 조회
        result = TestResult.query.filter_by(
            automation_test_id=id,
            id=result_id
        ).first_or_404()
        
        result_data = {
            'id': result.id,
            'automation_test_id': result.automation_test_id,
            'result': result.result,
            'execution_time': result.execution_time,
            'environment': result.environment,
            'executed_by': result.executed_by,
            'executed_at': result.executed_at.isoformat() if result.executed_at else None,
            'notes': result.notes
        }
        
        response = jsonify(result_data)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/screenshots', methods=['GET'])
def get_screenshots():
    """사용 가능한 스크린샷 목록 조회"""
    try:
        screenshots = []
        
        # test-scripts 폴더 내의 모든 PNG 파일 검색
        for root, dirs, files in os.walk(SCREENSHOT_BASE_PATH):
            for file in files:
                if file.lower().endswith('.png'):
                    # 상대 경로 계산
                    rel_path = os.path.relpath(os.path.join(root, file), SCREENSHOT_BASE_PATH)
                    screenshots.append({
                        'filename': file,
                        'path': rel_path,
                        'full_path': os.path.join(root, file),
                        'timestamp': os.path.getmtime(os.path.join(root, file)),
                        'size': os.path.getsize(os.path.join(root, file))
                    })
        
        # 타임스탬프 기준으로 정렬 (최신순)
        screenshots.sort(key=lambda x: x['timestamp'], reverse=True)
        
        response = jsonify(screenshots)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/screenshots/<path:filename>', methods=['GET'])
def get_screenshot(filename):
    """특정 스크린샷 파일 제공"""
    try:
        # 보안을 위해 경로 검증
        safe_path = os.path.normpath(unquote(filename))
        if safe_path.startswith('..') or safe_path.startswith('/'):
            response = jsonify({'error': 'Invalid path'})
            return add_cors_headers(response), 400
        
        file_path = os.path.join(SCREENSHOT_BASE_PATH, safe_path)
        
        if not os.path.exists(file_path):
            response = jsonify({'error': 'Screenshot not found'})
            return add_cors_headers(response), 404
        
        # 파일의 디렉토리와 파일명 분리
        directory = os.path.dirname(safe_path)
        filename_only = os.path.basename(safe_path)
        
        if directory:
            return send_from_directory(os.path.join(SCREENSHOT_BASE_PATH, directory), filename_only)
        else:
            return send_from_directory(SCREENSHOT_BASE_PATH, filename_only)
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/screenshots/by-test/<int:test_id>', methods=['GET'])
def get_screenshots_by_test(test_id):
    """특정 테스트와 관련된 스크린샷 조회"""
    try:
        # 테스트 정보 조회
        test = AutomationTest.query.get_or_404(test_id)
        
        # 스크립트 경로에서 스크린샷 폴더 추정
        script_path = test.script_path
        screenshots = []
        
        # 스크립트 경로 기반으로 관련 스크린샷 검색
        if script_path:
            # 스크립트 파일명에서 폴더명 추출
            script_name = os.path.basename(script_path)
            script_dir = os.path.dirname(script_path)
            
            # 관련 스크린샷 폴더 검색
            for root, dirs, files in os.walk(SCREENSHOT_BASE_PATH):
                for file in files:
                    if file.lower().endswith('.png'):
                        # 스크립트와 관련된 스크린샷인지 확인
                        rel_path = os.path.relpath(os.path.join(root, file), SCREENSHOT_BASE_PATH)
                        
                        # 스크립트 경로와 관련된 스크린샷 필터링
                        if script_name.lower().replace('.js', '') in rel_path.lower() or \
                           any(part in rel_path.lower() for part in script_dir.lower().split('/') if part):
                            screenshots.append({
                                'filename': file,
                                'path': rel_path,
                                'full_path': os.path.join(root, file),
                                'timestamp': os.path.getmtime(os.path.join(root, file)),
                                'size': os.path.getsize(os.path.join(root, file))
                            })
        
        # 타임스탬프 기준으로 정렬 (최신순)
        screenshots.sort(key=lambda x: x['timestamp'], reverse=True)
        
        response = jsonify(screenshots)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@automation_bp.route('/screenshots/recent', methods=['GET'])
def get_recent_screenshots():
    """최근 스크린샷 조회"""
    try:
        limit = request.args.get('limit', 10, type=int)
        screenshots = []
        
        # test-scripts 폴더 내의 모든 PNG 파일 검색
        for root, dirs, files in os.walk(SCREENSHOT_BASE_PATH):
            for file in files:
                if file.lower().endswith('.png'):
                    rel_path = os.path.relpath(os.path.join(root, file), SCREENSHOT_BASE_PATH)
                    screenshots.append({
                        'filename': file,
                        'path': rel_path,
                        'full_path': os.path.join(root, file),
                        'timestamp': os.path.getmtime(os.path.join(root, file)),
                        'size': os.path.getsize(os.path.join(root, file))
                    })
        
        # 타임스탬프 기준으로 정렬하고 최근 것만 반환
        screenshots.sort(key=lambda x: x['timestamp'], reverse=True)
        screenshots = screenshots[:limit]
        
        response = jsonify(screenshots)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500 