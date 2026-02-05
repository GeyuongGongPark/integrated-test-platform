from flask import Blueprint, request, jsonify, send_file
from models import db, TestCase, TestResult, Screenshot, Project, Folder, User, TestCaseTemplate, TestPlan, TestPlanTestCase, SystemConfig
from utils.cors import add_cors_headers
from utils.auth_decorators import admin_required, user_required, guest_allowed
from utils.serializers import serialize_testcase, serialize_project, serialize_folder
from services.testcase_service import TestCaseService
from services.report_service import ReportService
from utils.history_tracker import get_test_case_history, track_test_case_creation, track_test_case_change, track_test_case_deletion
from datetime import datetime, timedelta
from utils.timezone_utils import get_kst_now, get_kst_isoformat, format_kst_datetime
import pandas as pd
from io import BytesIO
import os
import subprocess
import time
import json
import requests
from utils.logger import get_logger

logger = get_logger(__name__)

# Blueprint 생성
testcases_bp = Blueprint('testcases', __name__)

# OPTIONS 핸들러는 app.py의 공통 함수 사용

# 기존 TCM API 엔드포인트들
@testcases_bp.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    data = [serialize_project(p) for p in projects]
    response = jsonify(data)
    return add_cors_headers(response), 200

@testcases_bp.route('/projects', methods=['POST'])
@admin_required
def create_project():
    data = request.get_json()
    project = Project(
        name=data.get('name'),
        description=data.get('description')
    )
    db.session.add(project)
    db.session.commit()
    response = jsonify({'message': '프로젝트 생성 완료', 'id': project.id})
    return add_cors_headers(response), 201


@testcases_bp.route('/projects/<int:project_id>', methods=['PUT'])
@admin_required
def update_project(project_id):
    """프로젝트 수정"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json() or {}

        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)

        db.session.commit()
        response = jsonify({
            'message': '프로젝트 수정 완료',
            'project': serialize_project(project)
        })
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"프로젝트 수정 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500


@testcases_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@admin_required
def delete_project(project_id):
    """프로젝트 삭제"""
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()

        response = jsonify({'message': '프로젝트 삭제 완료'})
        return add_cors_headers(response), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"프로젝트 삭제 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_testcases():
    if request.method == 'OPTIONS':
        from utils.common_helpers import handle_options_request
        return handle_options_request()
    
    try:
        page = request.args.get('page', None, type=int)
        per_page = request.args.get('per_page', None, type=int)
        
        data, pagination = TestCaseService.get_testcases(page, per_page, include_relations=True)
        
        if pagination:
            response_data = {
                'items': data,
                'pagination': pagination
            }
        else:
            response_data = data
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"테스트 케이스 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases/<int:id>', methods=['GET'])
@guest_allowed
def get_testcase(id):
    from sqlalchemy.orm import joinedload
    # N+1 쿼리 문제 해결: joinedload를 사용하여 관련 데이터를 한 번에 로드
    tc = TestCase.query.options(
        joinedload(TestCase.creator),
        joinedload(TestCase.assignee)
    ).get_or_404(id)
    
    # alpha DB 스키마에 맞춤: Screenshot은 test_result_id를 통해 연결됨
    # 최적화: test_result_id 목록을 한 번에 가져와서 IN 쿼리로 스크린샷 조회
    test_results = TestResult.query.filter_by(test_case_id=id).all()
    if test_results:
        result_ids = [result.id for result in test_results]
        screenshots = Screenshot.query.filter(Screenshot.test_result_id.in_(result_ids)).all()
    else:
        screenshots = []
    
    screenshot_data = [{'id': ss.id, 'screenshot_path': ss.file_path, 'timestamp': ss.created_at} for ss in screenshots]
    data = {
        'id': tc.id,
        'name': tc.name,
        'project_id': tc.project_id,
        'main_category': tc.main_category,
        'sub_category': tc.sub_category,
        'detail_category': tc.detail_category,
        'pre_condition': tc.pre_condition,
        'expected_result': tc.expected_result,
        'result_status': tc.result_status,
        'remark': tc.remark,
        'test_steps': tc.test_steps,
        'automation_code_path': tc.automation_code_path,
        'automation_code_type': tc.automation_code_type,
        'folder_id': tc.folder_id,
        'creator_id': tc.creator_id,
        'assignee_id': tc.assignee_id,
        'creator_name': tc.creator.username if tc.creator else None,
        'assignee_name': tc.assignee.username if tc.assignee else None,
        'screenshots': screenshot_data,
        'created_at': tc.created_at,
        'updated_at': tc.updated_at
    }
    response = jsonify(data)
    return add_cors_headers(response), 200


@testcases_bp.route('/testcases/ai/generate', methods=['POST', 'OPTIONS'])
@user_required
def generate_testcases_ai():
    """OpenAI로 테스트 케이스 초안 생성"""
    if request.method == 'OPTIONS':
        from utils.common_helpers import handle_options_request
        return handle_options_request()

    prompt = (request.get_json() or {}).get('prompt', '').strip()
    if not prompt:
        response = jsonify({'error': 'prompt가 필요합니다.'})
        return add_cors_headers(response), 400

    # 설정에 저장된 기본 프롬프트가 있으면 앞에 붙임
    default_row = SystemConfig.query.filter_by(key='tc_default_prompt').first()
    if default_row and (default_row.value or '').strip():
        full_prompt = (default_row.value or '').strip() + "\n\n--- 사용자 입력 ---\n\n" + prompt
    else:
        full_prompt = prompt

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        response = jsonify({'error': 'OPENAI_API_KEY가 설정되지 않았습니다.'})
        return add_cors_headers(response), 500

    model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    try:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a QA test case designer. Generate concise test cases in Korean. "
                        "Return only JSON with key 'test_cases' containing an array of objects. "
                        "Each object fields: name, main_category, sub_category, detail_category, "
                        "pre_condition, expected_result, remark. Keep values short."
                    ),
                },
                {"role": "user", "content": full_prompt},
            ],
            "temperature": 0.25,
            "max_tokens": 800,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        if not r.ok:
            response = jsonify({'error': f'OpenAI 호출 실패: {r.status_code} {r.text}'})
            return add_cors_headers(response), 502

        result = r.json()
        content = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        parsed = {}
        try:
            parsed = json.loads(content) if content else {}
        except json.JSONDecodeError:
            parsed = {}

        items = []
        raw_items = parsed.get("test_cases") if isinstance(parsed, dict) else None
        if raw_items is None and isinstance(parsed, list):
            raw_items = parsed

        if isinstance(raw_items, list):
            for idx, item in enumerate(raw_items):
                if not isinstance(item, dict):
                    continue
                items.append({
                    "name": item.get("name") or f"AI 테스트 케이스 {idx+1}",
                    "main_category": item.get("main_category", ""),
                    "sub_category": item.get("sub_category", ""),
                    "detail_category": item.get("detail_category", ""),
                    "pre_condition": item.get("pre_condition", ""),
                    "expected_result": item.get("expected_result", ""),
                    "remark": item.get("remark", ""),
                })

        response = jsonify({
            "items": items,
            "raw": content,
            "model": model,
            "usage": result.get("usage", {}),
        })
        return add_cors_headers(response), 200

    except requests.exceptions.Timeout:
        response = jsonify({'error': 'OpenAI 응답 대기 시간 초과'})
        return add_cors_headers(response), 504
    except Exception as e:
        logger.error(f"AI 테스트 케이스 생성 오류: {str(e)}")
        response = jsonify({'error': 'AI 생성 중 오류가 발생했습니다.'})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases/<int:id>/history', methods=['GET'])
@guest_allowed
def get_test_case_history_api(id):
    """테스트 케이스 변경 히스토리 조회"""
    try:
        history = get_test_case_history(id)
        
        data = [{
            'id': h.id,
            'field_name': h.field_name,
            'old_value': h.old_value,
            'new_value': h.new_value,
            'change_type': h.change_type,
            'changed_by': h.changed_by,
            'changed_at': h.changed_at.isoformat() if h.changed_at else None,
            'user_name': h.user.username if h.user else 'Unknown'
        } for h in history]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"테스트 케이스 히스토리 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases', methods=['POST'])
@user_required
def create_testcase():
    from utils.common_helpers import get_or_create_default_project, get_or_create_default_folder, validate_required_fields, create_error_response
    from utils.logger import get_logger
    logger = get_logger(__name__)
    
    data = request.get_json()
    logger.debug(f"테스트 케이스 생성 요청 데이터: {data}")
    logger.debug(f"자동화 코드 경로: {data.get('automation_code_path')}")
    logger.debug(f"자동화 코드 타입: {data.get('automation_code_type')}")
    
    # name 필드 검증
    validation_error = validate_required_fields(data, ['name'])
    if validation_error:
        return validation_error
    
    # project_id가 없으면 기본 프로젝트 사용 또는 생성
    project_id = data.get('project_id')
    if not project_id:
        default_project = get_or_create_default_project()
        project_id = default_project.id
    
    # folder_id가 없으면 기본 폴더 사용
    folder_id = data.get('folder_id')
    if not folder_id:
        default_folder = get_or_create_default_folder()
        if default_folder:
            folder_id = default_folder.id
    
    # 폴더의 환경 정보를 자동으로 가져오기
    folder_environment = 'dev'  # 기본값
    if folder_id:
        folder = Folder.query.get(folder_id)
        if folder:
            folder_environment = folder.environment
            logger.debug(f"폴더 '{folder.folder_name}'의 환경: {folder_environment}")
    
    tc = TestCase(
        name=data.get('name'),
        project_id=project_id,
        main_category=data.get('main_category', ''),
        sub_category=data.get('sub_category', ''),
        detail_category=data.get('detail_category', ''),
        pre_condition=data.get('pre_condition', ''),
        expected_result=data.get('expected_result', ''),
        result_status=data.get('result_status', 'N/T'),
        remark=data.get('remark', ''),
        test_steps=data.get('test_steps') or None,
        environment=folder_environment,  # 폴더의 환경 정보 사용
        folder_id=folder_id,
        automation_code_path=data.get('automation_code_path', ''),
        automation_code_type=data.get('automation_code_type', 'playwright'),
        creator_id=request.user.id, # 현재 로그인한 사용자의 ID
        assignee_id=data.get('assignee_id')  # assignee_id가 없으면 None (담당자 미지정)
    )

    try:
        db.session.add(tc)
        db.session.commit()
        
        # 담당자 지정 시 알림 전송
        if tc.assignee_id:
            try:
                from services.notification_service import notification_service
                logger.info(f"🔔 담당자 지정 알림 생성 시도: TestCase {tc.id}, Assignee {tc.assignee_id}, Creator {request.user.id}")
                
                # 테스트 케이스 이름 생성 (main_category, sub_category, detail_category 조합 또는 name)
                if tc.name:
                    test_case_name = tc.name
                elif tc.main_category or tc.sub_category or tc.detail_category:
                    categories = [tc.main_category, tc.sub_category, tc.detail_category]
                    test_case_name = ' > '.join([c for c in categories if c]) or f"테스트 케이스 #{tc.id}"
                else:
                    test_case_name = f"테스트 케이스 #{tc.id}"
                
                logger.info(f"🔔 알림 생성 파라미터: user_id={tc.assignee_id}, title='테스트 케이스 담당자 지정', message='{test_case_name}'")
                
                notification = notification_service.create_notification(
                    user_id=tc.assignee_id,
                    notification_type='assignment',
                    title='테스트 케이스 담당자 지정',
                    message=f"'{test_case_name}' 테스트 케이스의 담당자로 지정되었습니다.",
                    related_test_case_id=tc.id,
                    priority='medium'
                )
                logger.info(f"✅ 담당자 지정 알림 생성 성공: Notification ID {notification.id if notification else 'None'}")
            except Exception as e:
                logger.error(f"❌ 담당자 지정 알림 전송 실패: {str(e)}", exc_info=True)
        
        # 캐시 무효화
        from services.cache_service import cache_service
        cache_service.invalidate_entity('testcase', tc.id)
        cache_service.delete_pattern('testcases:list:*')
        
        # 히스토리 추적
        try:
            track_test_case_creation(tc.id, data, request.user.id)
        except Exception as e:
            logger.warning(f"히스토리 추적 실패: {str(e)}")
        
        response = jsonify({'message': '테스트 케이스 생성 완료', 'id': tc.id})
        return add_cors_headers(response), 201
    except Exception as e:
        print("Error saving to database:", e)
        db.session.rollback()
        response = jsonify({'error': f'데이터베이스 오류: {str(e)}'})
        return add_cors_headers(response), 500

def update_dashboard_summary_for_environment(environment):
    """특정 환경의 대시보드 요약 데이터 업데이트"""
    try:
        from sqlalchemy import text
        from datetime import datetime
        
        # 해당 환경의 테스트 케이스 통계 조회
        query = text("""
            SELECT 
                result_status,
                COUNT(*) as count
            FROM TestCases
            WHERE environment = :env
            GROUP BY result_status
        """)
        
        result = db.session.execute(query, {'env': environment})
        stats = result.fetchall()
        
        # 통계 계산
        status_counts = {row.result_status: row.count for row in stats}
        total_tests = sum(status_counts.values())
        passed_tests = status_counts.get('Pass', 0)
        failed_tests = status_counts.get('Fail', 0)
        skipped_tests = status_counts.get('N/T', 0) + status_counts.get('N/A', 0)
        
        # 통과율 계산
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # DashboardSummary 모델 import
        from models import DashboardSummary
        
        # 기존 요약 데이터 확인 및 업데이트
        existing_summary = DashboardSummary.query.filter_by(environment=environment).first()
        
        if existing_summary:
            existing_summary.total_tests = total_tests
            existing_summary.passed_tests = passed_tests
            existing_summary.failed_tests = failed_tests
            existing_summary.skipped_tests = skipped_tests
            existing_summary.pass_rate = round(pass_rate, 2)
            existing_summary.last_updated = get_kst_now()
        else:
            # 새 요약 데이터 생성
            new_summary = DashboardSummary(
                environment=environment,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
                pass_rate=round(pass_rate, 2),
                last_updated=get_kst_now()
            )
            db.session.add(new_summary)
        
        print(f"🔄 대시보드 요약 데이터 업데이트 완료: {environment}")
        return True
        
    except Exception as e:
        print(f"❌ 대시보드 요약 데이터 업데이트 실패: {str(e)}")
        return False

@testcases_bp.route('/testcases/<int:id>/status', methods=['PUT'])
@user_required
def update_testcase_status(id):
    try:
        tc = TestCase.query.get_or_404(id)
        data = request.get_json()
        
        old_status = tc.result_status
        new_status = data.get('status', tc.result_status)
        
        # 상태가 변경되지 않으면 알림 발송하지 않음
        if old_status == new_status:
            response = jsonify({
                'message': '테스트 케이스 상태가 변경되지 않았습니다.',
                'old_status': old_status,
                'new_status': new_status,
                'environment': tc.environment
            })
            return add_cors_headers(response), 200
        
        print(f"🔄 테스트 케이스 상태 변경: {tc.name} ({old_status} → {new_status})")
        
        # 현재 사용자 ID 가져오기
        current_user_id = None
        if hasattr(request, 'user') and request.user:
            current_user_id = request.user.id
        
        # 상태 업데이트
        tc.result_status = new_status
        db.session.commit()
        
        # 알림 생성 (상태 변경 시 작성자와 담당자에게 발송)
        try:
            from services.notification_service import notification_service
            
            # 상태 변경 알림 발송 (작성자와 담당자에게)
            notification_service.notify_test_status_changed(
                test_case_id=id,
                old_status=old_status,
                new_status=new_status,
                changed_by_user_id=current_user_id
            )
            
            # 실패 알림은 테스트 결과가 있을 때만 추가로 생성
            if new_status == 'Fail':
                latest_result = TestResult.query.filter_by(test_case_id=id).order_by(TestResult.executed_at.desc()).first()
                if latest_result:
                    notification_service.notify_test_failed(id, latest_result.id)
        except Exception as notify_error:
            logger.warning(f"알림 생성 실패: {str(notify_error)}")
        
        # 대시보드 요약 데이터 자동 업데이트
        if update_dashboard_summary_for_environment(tc.environment):
            print(f"✅ 대시보드 요약 데이터 업데이트 성공: {tc.environment}")
        else:
            print(f"⚠️ 대시보드 요약 데이터 업데이트 실패: {tc.environment}")
        
        response = jsonify({
            'message': '테스트 케이스 상태 업데이트 완료',
            'old_status': old_status,
            'new_status': new_status,
            'environment': tc.environment
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        print(f"❌ 테스트 케이스 상태 업데이트 실패: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': f'상태 업데이트 중 오류가 발생했습니다: {str(e)}'})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases/<int:id>', methods=['PUT'])
@user_required
def update_testcase(id):
    try:
        tc = TestCase.query.get_or_404(id)
        data = request.get_json()
        
        # 폴더 ID가 변경되었는지 확인
        new_folder_id = data.get('folder_id', tc.folder_id)
        if new_folder_id != tc.folder_id:
            # 새 폴더의 환경 정보로 자동 업데이트
            new_folder = Folder.query.get(new_folder_id)
            if new_folder:
                tc.environment = new_folder.environment
                print(f"🔄 폴더 변경으로 인한 환경 정보 업데이트: {tc.environment} → {new_folder.environment}")
        
        # 테스트 케이스 정보 업데이트
        tc.main_category = data.get('main_category', tc.main_category)
        tc.sub_category = data.get('sub_category', tc.sub_category)
        tc.detail_category = data.get('detail_category', tc.detail_category)
        tc.pre_condition = data.get('pre_condition', tc.pre_condition)
        tc.expected_result = data.get('expected_result', tc.expected_result)
        tc.result_status = data.get('result_status', tc.result_status)
        tc.remark = data.get('remark', tc.remark)
        if 'test_steps' in data:
            tc.test_steps = data.get('test_steps') or None
        tc.folder_id = new_folder_id
        tc.automation_code_path = data.get('automation_code_path', tc.automation_code_path)
        tc.automation_code_type = data.get('automation_code_type', tc.automation_code_type)
        
        # 담당자 정보 업데이트
        old_assignee_id = tc.assignee_id  # 기존 담당자 (None일 수 있음)
        if 'assignee_id' in data:
            new_assignee_id = data.get('assignee_id')
            tc.assignee_id = new_assignee_id
            
            # 알림 전송 조건:
            # 1. 새로운 담당자가 지정되었고 (new_assignee_id가 None이 아님)
            # 2. 기존 담당자와 다르고 (담당자가 없던 경우도 포함: None -> 사용자ID)
            # 본인인 경우에도 알림 전송
            if new_assignee_id and new_assignee_id != old_assignee_id:
                try:
                    from services.notification_service import notification_service
                    logger.info(f"🔔 담당자 변경 알림 생성 시도: TestCase {tc.id}, Old Assignee {old_assignee_id}, New Assignee {new_assignee_id}, Creator {request.user.id}")
                    
                    # 테스트 케이스 이름 생성
                    if tc.name:
                        test_case_name = tc.name
                    elif tc.main_category or tc.sub_category or tc.detail_category:
                        categories = [tc.main_category, tc.sub_category, tc.detail_category]
                        test_case_name = ' > '.join([c for c in categories if c]) or f"테스트 케이스 #{tc.id}"
                    else:
                        test_case_name = f"테스트 케이스 #{tc.id}"
                    
                    logger.info(f"🔔 알림 생성 파라미터: user_id={new_assignee_id}, title='테스트 케이스 담당자 지정', message='{test_case_name}'")
                    
                    notification = notification_service.create_notification(
                        user_id=new_assignee_id,
                        notification_type='assignment',
                        title='테스트 케이스 담당자 지정',
                        message=f"'{test_case_name}' 테스트 케이스의 담당자로 지정되었습니다.",
                        related_test_case_id=tc.id,
                        priority='medium'
                    )
                    logger.info(f"✅ 담당자 변경 알림 생성 성공: Notification ID {notification.id if notification else 'None'}")
                except Exception as e:
                    logger.error(f"❌ 담당자 변경 알림 전송 실패: {str(e)}", exc_info=True)
        
        db.session.commit()
        
        # 대시보드 요약 데이터 자동 업데이트
        if update_dashboard_summary_for_environment(tc.environment):
            print(f"✅ 대시보드 요약 데이터 업데이트 성공: {tc.environment}")
        else:
            print(f"⚠️ 대시보드 요약 데이터 업데이트 실패: {tc.environment}")
        
        response = jsonify({'message': '테스트 케이스 업데이트 완료'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        print(f"❌ 테스트 케이스 업데이트 실패: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': f'업데이트 중 오류가 발생했습니다: {str(e)}'})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases/<int:id>', methods=['DELETE'])
@admin_required
def delete_testcase(id):
    try:
        tc = TestCase.query.get_or_404(id)
        environment = tc.environment
        testcase_name = tc.name
        
        print(f"🗑️ 테스트 케이스 삭제: {testcase_name} ({environment})")
        
        # 연관된 데이터 먼저 삭제
        # 1. 테스트 결과 삭제
        test_results = TestResult.query.filter_by(test_case_id=id).all()
        for result in test_results:
            # 테스트 결과에 연결된 스크린샷 삭제
            screenshots = Screenshot.query.filter_by(test_result_id=result.id).all()
            for screenshot in screenshots:
                db.session.delete(screenshot)
            # 테스트 결과 삭제
            db.session.delete(result)
        
        # 2. 테스트 계획에서의 연결 삭제
        test_plan_testcases = TestPlanTestCase.query.filter_by(test_case_id=id).all()
        for ptc in test_plan_testcases:
            db.session.delete(ptc)
        
        # 3. 마지막으로 테스트 케이스 삭제
        db.session.delete(tc)
        db.session.commit()
        
        # 대시보드 요약 데이터 자동 업데이트
        if update_dashboard_summary_for_environment(environment):
            print(f"✅ 대시보드 요약 데이터 업데이트 성공: {environment}")
        else:
            print(f"⚠️ 대시보드 요약 데이터 업데이트 실패: {environment}")
        
        response = jsonify({'message': '테스트 케이스 삭제 완료'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        print(f"❌ 테스트 케이스 삭제 실패: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': f'삭제 중 오류가 발생했습니다: {str(e)}'})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases/bulk-delete', methods=['POST'])
@admin_required
def bulk_delete_testcases():
    """다중 테스트 케이스 삭제"""
    try:
        data = request.get_json()
        testcase_ids = data.get('testcase_ids', [])
        
        if not testcase_ids:
            response = jsonify({'error': '삭제할 테스트 케이스 ID 목록이 필요합니다'})
            return add_cors_headers(response), 400
        
        if not isinstance(testcase_ids, list):
            response = jsonify({'error': 'testcase_ids는 배열이어야 합니다'})
            return add_cors_headers(response), 400
        
        print(f"🗑️ 다중 테스트 케이스 삭제 시도: {len(testcase_ids)}개")
        
        # 최적화: 한 번에 모든 테스트 케이스 조회
        testcases_to_delete = TestCase.query.filter(TestCase.id.in_(testcase_ids)).all()
        valid_ids = {tc.id for tc in testcases_to_delete}
        invalid_ids = set(testcase_ids) - valid_ids
        
        # 환경 정보 수집 (대시보드 업데이트용)
        environments_to_update = {tc.environment for tc in testcases_to_delete}
        
        if invalid_ids:
            failed_deletions = [{
                'id': testcase_id,
                'error': '테스트 케이스를 찾을 수 없습니다'
            } for testcase_id in invalid_ids]
        else:
            failed_deletions = []
        
        if testcases_to_delete:
            # 연관된 데이터를 bulk delete로 최적화
            testcase_ids_list = [tc.id for tc in testcases_to_delete]
            
            # 1. 스크린샷 삭제 (test_result_id를 통해)
            test_result_ids = db.session.query(TestResult.id).filter(
                TestResult.test_case_id.in_(testcase_ids_list)
            ).subquery()
            Screenshot.query.filter(Screenshot.test_result_id.in_(test_result_ids)).delete(synchronize_session=False)
            
            # 2. 테스트 결과 삭제
            TestResult.query.filter(TestResult.test_case_id.in_(testcase_ids_list)).delete(synchronize_session=False)
            
            # 3. 테스트 계획에서의 연결 삭제
            TestPlanTestCase.query.filter(TestPlanTestCase.test_case_id.in_(testcase_ids_list)).delete(synchronize_session=False)
            
            # 4. 테스트 케이스 삭제
            deleted_count = TestCase.query.filter(TestCase.id.in_(testcase_ids_list)).delete(synchronize_session=False)
        else:
            deleted_count = 0
        
        # 모든 삭제 작업을 한 번에 커밋
        db.session.commit()
        
        # 대시보드 요약 데이터 자동 업데이트 (환경별로)
        for environment in environments_to_update:
            if update_dashboard_summary_for_environment(environment):
                print(f"✅ 대시보드 요약 데이터 업데이트 성공: {environment}")
            else:
                print(f"⚠️ 대시보드 요약 데이터 업데이트 실패: {environment}")
        
        response_data = {
            'message': f'{deleted_count}개의 테스트 케이스가 성공적으로 삭제되었습니다',
            'deleted_count': deleted_count,
            'total_requested': len(testcase_ids),
            'failed_deletions': failed_deletions
        }
        
        if failed_deletions:
            response_data['warning'] = f'{len(failed_deletions)}개의 테스트 케이스 삭제에 실패했습니다'
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        print(f"❌ 다중 테스트 케이스 삭제 실패: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': f'다중 삭제 중 오류가 발생했습니다: {str(e)}'})
        return add_cors_headers(response), 500

@testcases_bp.route('/testresults/<int:test_case_id>', methods=['GET'])
def get_test_results(test_case_id):
    """특정 테스트 케이스의 실행 결과 조회"""
    try:
        results = TestResult.query.filter_by(test_case_id=test_case_id).order_by(TestResult.executed_at.desc()).all()
        
        result_list = []
        for result in results:
            result_data = {
                'id': result.id,
                'test_case_id': result.test_case_id,
                'result': result.result,
                'executed_at': result.executed_at.isoformat() if result.executed_at else None,
                'notes': result.notes,
                'screenshot': getattr(result, 'screenshot', None),  # 실제 DB에 없을 수 있음
                'environment': result.environment,
                'execution_duration': getattr(result, 'execution_duration', None),  # 실제 DB에 없을 수 있음
                'error_message': getattr(result, 'error_message', None)  # 실제 DB에 없을 수 있음
            }
            result_list.append(result_data)
        
        response = jsonify(result_list)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases/<int:id>/screenshots', methods=['GET'])
def get_testcase_screenshots(id):
    """테스트 케이스의 스크린샷 목록 조회 (최적화: N+1 쿼리 문제 해결)"""
    try:
        test_case = TestCase.query.get_or_404(id)
        # alpha DB 스키마에 맞춤: Screenshot은 test_result_id를 통해 연결됨
        # 최적화: test_result_id 목록을 한 번에 가져와서 IN 쿼리로 스크린샷 조회
        test_results = TestResult.query.filter_by(test_case_id=id).all()
        if test_results:
            result_ids = [result.id for result in test_results]
            screenshots = Screenshot.query.filter(Screenshot.test_result_id.in_(result_ids)).all()
        else:
            screenshots = []
        
        screenshot_list = [{
            'id': screenshot.id,
            'screenshot_path': screenshot.file_path,  # alpha DB는 file_path 사용
            'timestamp': screenshot.created_at.isoformat() if screenshot.created_at else None  # alpha DB는 created_at 사용
        } for screenshot in screenshots]
        
        response = jsonify(screenshot_list)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/screenshots/<path:filename>', methods=['GET'])
def get_screenshot(filename):
    """스크린샷 파일 조회"""
    try:
        import os
        screenshot_path = os.path.join('screenshots', filename)
        if os.path.exists(screenshot_path):
            return send_file(screenshot_path, mimetype='image/png')
        else:
            response = jsonify({'error': '스크린샷 파일을 찾을 수 없습니다'})
            return add_cors_headers(response), 404
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/testresults', methods=['POST'])
@user_required
def create_test_result():
    data = request.get_json()
    result = TestResult(
        test_case_id=data.get('test_case_id'),
        result=data.get('result'),
        notes=data.get('notes')
    )
    db.session.add(result)
    db.session.commit()
    response = jsonify({'message': '테스트 결과 생성 완료', 'id': result.id})
    return add_cors_headers(response), 201

# 엑셀 업로드 API
@testcases_bp.route('/testcases/upload', methods=['POST'])
@user_required
def upload_testcases_excel():
    """엑셀 파일에서 테스트 케이스 업로드"""
    try:
        print("=== 파일 업로드 디버깅 ===")
        print(f"Content-Type: {request.headers.get('Content-Type')}")
        print(f"Files: {list(request.files.keys())}")
        print(f"Form data: {list(request.form.keys())}")
        
        if 'file' not in request.files:
            print("❌ 'file' 키가 request.files에 없음")
            print(f"사용 가능한 키들: {list(request.files.keys())}")
            response = jsonify({'error': '파일이 없습니다'})
            return add_cors_headers(response), 400
        
        file = request.files['file']
        print(f"파일명: {file.filename}")
        print(f"파일 크기: {len(file.read()) if file else 'N/A'}")
        file.seek(0)  # 파일 포인터를 다시 처음으로
        
        if file.filename == '':
            print("❌ 파일명이 비어있음")
            response = jsonify({'error': '파일이 선택되지 않았습니다'})
            return add_cors_headers(response), 400
        
        if not file.filename.endswith('.xlsx'):
            print(f"❌ 지원하지 않는 파일 형식: {file.filename}")
            response = jsonify({'error': '엑셀 파일(.xlsx)만 업로드 가능합니다'})
            return add_cors_headers(response), 400
        
        print("✅ 파일 검증 통과")
        
        # 엑셀 파일 읽기
        df = pd.read_excel(file)
        print(f"✅ 엑셀 파일 읽기 성공, 행 수: {len(df)}")
        print(f"📊 컬럼명: {list(df.columns)}")
        print(f"📋 첫 번째 행 데이터: {df.iloc[0].to_dict()}")
        
        created_count = 0
        for index, row in df.iterrows():
            print(f"🔍 처리 중인 행 {index + 1}: {row.to_dict()}")
            
            test_case = TestCase(
                project_id=row.get('project_id', 1),
                main_category=row.get('main_category', ''),
                sub_category=row.get('sub_category', ''),
                detail_category=row.get('detail_category', ''),
                pre_condition=row.get('pre_condition', ''),
                expected_result=row.get('expected_result', ''),
                result_status=row.get('result_status', 'N/T'),
                remark=row.get('remark', ''),
                environment=row.get('environment', 'dev'),
                automation_code_path=row.get('automation_code_path', ''),
                automation_code_type=row.get('automation_code_type', '')
            )
            
            print(f"📝 생성된 테스트 케이스: main_category='{test_case.main_category}', expected_result='{test_case.expected_result}'")
            
            db.session.add(test_case)
            created_count += 1
        
        try:
            db.session.commit()
            print(f"✅ {created_count}개의 테스트 케이스 생성 완료")
        except Exception as commit_error:
            print(f"❌ 데이터베이스 커밋 오류: {str(commit_error)}")
            db.session.rollback()
            raise commit_error
        
        response = jsonify({
            'message': f'{created_count}개의 테스트 케이스가 업로드되었습니다',
            'created_count': created_count
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        print(f"❌ 파일 업로드 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# 엑셀 다운로드 API
@testcases_bp.route('/testcases/download', methods=['GET'])
def download_testcases_excel():
    """테스트 케이스를 엑셀 파일로 다운로드 (필터 적용 가능)"""
    try:
        from sqlalchemy import or_
        
        # 필터 파라미터 받기
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '')
        environment = request.args.get('environment', '')
        category = request.args.get('category', '')
        creator = request.args.get('creator', '')
        assignee = request.args.get('assignee', '')
        folder_id = request.args.get('folder_id', type=int)
        
        # 기본 쿼리
        query = TestCase.query
        
        # 검색어 필터
        if search:
            search_lower = search.lower()
            query = query.filter(
                or_(
                    TestCase.main_category.ilike(f'%{search}%'),
                    TestCase.sub_category.ilike(f'%{search}%'),
                    TestCase.detail_category.ilike(f'%{search}%'),
                    TestCase.expected_result.ilike(f'%{search}%'),
                    TestCase.remark.ilike(f'%{search}%')
                )
            )
        
        # 상태 필터
        if status and status != 'all':
            query = query.filter(TestCase.result_status == status)
        
        # 환경 필터
        if environment and environment != 'all':
            query = query.filter(TestCase.environment == environment)
        
        # 카테고리 필터 (main > sub > detail 형식)
        if category and category != 'all':
            category_parts = category.split(' > ')
            if len(category_parts) >= 1:
                query = query.filter(TestCase.main_category == category_parts[0])
            if len(category_parts) >= 2:
                query = query.filter(TestCase.sub_category == category_parts[1])
            if len(category_parts) >= 3:
                query = query.filter(TestCase.detail_category == category_parts[2])
        
        # 폴더 필터
        if folder_id:
            folder = Folder.query.get(folder_id)
            if folder:
                # 폴더 타입에 따라 필터링
                if folder.folder_type == 'environment':
                    # 환경 폴더인 경우, 해당 환경의 모든 하위 폴더 포함
                    from sqlalchemy.orm import aliased
                    env_folders = Folder.query.filter(
                        Folder.parent_folder_id == folder_id
                    ).all()
                    folder_ids = [folder_id] + [f.id for f in env_folders]
                    # 하위 폴더의 하위 폴더도 포함
                    for env_folder in env_folders:
                        sub_folders = Folder.query.filter(
                            Folder.parent_folder_id == env_folder.id
                        ).all()
                        folder_ids.extend([f.id for f in sub_folders])
                    query = query.filter(TestCase.folder_id.in_(folder_ids))
                elif folder.folder_type == 'deployment_date':
                    # 배포일자 폴더인 경우, 해당 배포일자의 모든 하위 폴더 포함
                    dep_folders = Folder.query.filter(
                        Folder.parent_folder_id == folder_id
                    ).all()
                    folder_ids = [folder_id] + [f.id for f in dep_folders]
                    query = query.filter(TestCase.folder_id.in_(folder_ids))
                else:
                    # 기능명 폴더인 경우, 해당 폴더만
                    query = query.filter(TestCase.folder_id == folder_id)
        
        # 작성자 필터 (User 테이블과 조인 필요)
        if creator and creator != 'all':
            from sqlalchemy.orm import aliased
            CreatorUser = aliased(User)
            query = query.join(CreatorUser, TestCase.creator_id == CreatorUser.id).filter(
                CreatorUser.username == creator
            )
        
        # 담당자 필터 (User 테이블과 조인 필요)
        if assignee and assignee != 'all':
            from sqlalchemy.orm import aliased
            AssigneeUser = aliased(User)
            # creator 조인 여부 확인
            if creator and creator != 'all':
                # 이미 creator로 조인되어 있으므로 별칭 사용
                query = query.join(AssigneeUser, TestCase.assignee_id == AssigneeUser.id).filter(
                    AssigneeUser.username == assignee
                )
            else:
                # creator 조인이 없으므로 일반 조인
                query = query.join(AssigneeUser, TestCase.assignee_id == AssigneeUser.id).filter(
                    AssigneeUser.username == assignee
                )
        
        # 필터링된 테스트 케이스 조회
        test_cases = query.all()
        
        logger.info(f"다운로드 필터 적용: 검색={search}, 상태={status}, 환경={environment}, 카테고리={category}, 폴더={folder_id}, 결과={len(test_cases)}개")
        
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
                'expected_result': tc.expected_result,
                'result_status': tc.result_status,
                'remark': tc.remark,
                'test_steps': getattr(tc, 'test_steps', None),
                'environment': tc.environment,
                'automation_code_path': tc.automation_code_path,
                'automation_code_type': tc.automation_code_type,
                'created_at': tc.created_at.isoformat() if tc.created_at else None
            })
        
        df = pd.DataFrame(data)
        
        # 엑셀 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='TestCases')
        
        output.seek(0)
        
        # 파일명 생성
        try:
            filename = f'testcases_{format_kst_datetime(get_kst_now(), "%Y%m%d_%H%M%S")}.xlsx'
        except Exception as e:
            logger.warning(f"파일명 생성 오류: {str(e)}, 기본 파일명 사용")
            filename = f'testcases_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        # Flask 2.3.3에서는 download_name 사용
        file_response = send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
        # CORS 헤더 추가
        return add_cors_headers(file_response), 200
        
    except Exception as e:
        logger.error(f"다운로드 에러: {str(e)}", exc_info=True)
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"에러 상세: {error_trace}")
        response = jsonify({'error': f'파일 다운로드 중 오류가 발생했습니다: {str(e)}'})
        return add_cors_headers(response), 500

# 자동화 코드 실행 API
@testcases_bp.route('/testcases/<int:id>/execute', methods=['POST'])
def execute_automation_code(id):
    """테스트 케이스의 자동화 코드 실행 (스크립트 경로 또는 test_steps JSON 지원)"""
    try:
        test_case = TestCase.query.get_or_404(id)
        body = request.get_json() or {}
        base_url = body.get('baseUrl') or body.get('base_url') or os.environ.get('PLAYWRIGHT_BASE_URL', 'http://localhost:3000')

        # 테스트 단계(JSON)만 있고 자동화 코드 경로가 없는 경우 → 단계 실행기로 실행
        if not test_case.automation_code_path and test_case.test_steps:
            try:
                steps_data = json.loads(test_case.test_steps)
            except (json.JSONDecodeError, TypeError):
                response = jsonify({'error': '테스트 단계(test_steps) JSON 형식이 올바르지 않습니다'})
                return add_cors_headers(response), 400
            if not isinstance(steps_data, list) or len(steps_data) == 0:
                response = jsonify({'error': '테스트 단계는 비어 있지 않은 배열이어야 합니다'})
                return add_cors_headers(response), 400

            start_time = time.time()
            from utils.playwright_steps_runner import run_playwright_steps
            run_result = run_playwright_steps(steps_data, base_url=base_url)
            execution_duration = time.time() - start_time

            test_result = TestResult(
                test_case_id=id,
                result=run_result['status'],
                environment=test_case.environment,
                execution_duration=execution_duration,
                error_message=run_result.get('error')
            )
            db.session.add(test_result)
            db.session.commit()

            response = jsonify({
                'message': '테스트 단계 실행 완료',
                'result': run_result['status'],
                'output': run_result.get('output', ''),
                'error': run_result.get('error', ''),
                'execution_duration': execution_duration
            })
            return add_cors_headers(response), 200

        if not test_case.automation_code_path:
            response = jsonify({'error': '자동화 코드 경로 또는 테스트 단계(test_steps)를 설정해 주세요'})
            return add_cors_headers(response), 400

        # 자동화 코드 실행
        script_path = test_case.automation_code_path
        script_type = test_case.automation_code_type or 'playwright'
        
        # 디버깅을 위한 로그 추가
        print(f"🔍 테스트 케이스 ID: {id}")
        print(f"🔍 자동화 코드 경로: {script_path}")
        print(f"🔍 자동화 코드 타입: {script_type}")
        
        # 스크립트 경로가 디렉토리인지 파일인지 확인
        if not script_path:
            response = jsonify({'error': '자동화 코드 경로가 설정되지 않았습니다'})
            return add_cors_headers(response), 400
        
        import time
        start_time = time.time()
        
        if script_type == 'k6':
            # k6 성능 테스트 실행
            from engines.k6_engine import k6_engine
            result = k6_engine.execute_test(script_path, {})
            execution_duration = time.time() - start_time
            
            # 실행 결과 저장
            test_result = TestResult(
                test_case_id=id,
                result=result['status'],
                environment=test_case.environment,
                execution_duration=execution_duration,
                error_message=result.get('error')
            )
            db.session.add(test_result)
            db.session.commit()
            
            response = jsonify({
                'message': '자동화 코드 실행 완료',
                'result': result['status'],
                'output': result.get('output', ''),
                'error': result.get('error', ''),
                'execution_duration': execution_duration
            })
            return add_cors_headers(response), 200
            
        elif script_type in ['selenium', 'playwright', 'k6']:
            # UI 테스트 실행
            if script_type == 'k6':
                # k6 실행
                import os
                # 스크립트 경로를 절대 경로로 변환
                if not os.path.isabs(script_path):
                    # 백엔드 디렉토리에서 상위 디렉토리로 이동
                    backend_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(backend_dir)
                    script_path = os.path.join(project_root, script_path)
                
                print(f"🔍 k6 실행 경로: {script_path}")
                print(f"📁 파일 존재 여부: {os.path.exists(script_path)}")
                print(f"📁 프로젝트 루트: {project_root}")
                print(f"📁 현재 작업 디렉토리: {os.getcwd()}")
                
                # 경로가 디렉토리인지 파일인지 확인
                if os.path.isdir(script_path):
                    # 디렉토리인 경우 해당 디렉토리에서 .js 파일 찾기
                    js_files = [f for f in os.listdir(script_path) if f.endswith('.js')]
                    if js_files:
                        script_path = os.path.join(script_path, js_files[0])
                        print(f"🔍 디렉토리에서 찾은 스크립트: {script_path}")
                    else:
                        response = jsonify({'error': f'디렉토리 {script_path}에서 .js 파일을 찾을 수 없습니다'})
                        return add_cors_headers(response), 400
                
                # 절대 경로 사용
                absolute_script_path = os.path.abspath(script_path)
                print(f"🔍 절대 경로: {absolute_script_path}")
                print(f"📁 절대 경로 파일 존재 여부: {os.path.exists(absolute_script_path)}")
                
                if not os.path.exists(absolute_script_path):
                    response = jsonify({'error': f'스크립트 파일을 찾을 수 없습니다: {absolute_script_path}'})
                    return add_cors_headers(response), 400
                
                # 환경 변수 설정
                env = os.environ.copy()
                env['K6_BROWSER_ENABLED'] = 'true'
                env['K6_BROWSER_HEADLESS'] = 'true'
                
                result = subprocess.run(
                    ['k6', 'run', absolute_script_path],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5분 타임아웃
                    cwd=project_root,  # 프로젝트 루트에서 실행
                    env=env
                )
            elif script_type == 'playwright':
                # Playwright 실행
                import os
                # 스크립트 경로를 절대 경로로 변환
                if not os.path.isabs(script_path):
                    backend_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(backend_dir)
                    script_path = os.path.join(project_root, script_path)
                
                # 경로가 디렉토리인지 파일인지 확인
                if os.path.isdir(script_path):
                    # 디렉토리인 경우 해당 디렉토리에서 .spec.js 파일 찾기
                    spec_files = [f for f in os.listdir(script_path) if f.endswith('.spec.js')]
                    if spec_files:
                        script_path = os.path.join(script_path, spec_files[0])
                        print(f"🔍 디렉토리에서 찾은 Playwright 스크립트: {script_path}")
                    else:
                        response = jsonify({'error': f'디렉토리 {script_path}에서 .spec.js 파일을 찾을 수 없습니다'})
                        return add_cors_headers(response), 400
                
                absolute_script_path = os.path.abspath(script_path)
                if not os.path.exists(absolute_script_path):
                    response = jsonify({'error': f'Playwright 스크립트 파일을 찾을 수 없습니다: {absolute_script_path}'})
                    return add_cors_headers(response), 400
                
                result = subprocess.run(
                    ['npx', 'playwright', 'test', absolute_script_path, '--reporter=json'],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5분 타임아웃
                    cwd=os.path.dirname(absolute_script_path) if os.path.dirname(absolute_script_path) else None
                )
            else:
                # Selenium 실행
                import os
                # 스크립트 경로를 절대 경로로 변환
                if not os.path.isabs(script_path):
                    backend_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(backend_dir)
                    script_path = os.path.join(project_root, script_path)
                
                # 경로가 디렉토리인지 파일인지 확인
                if os.path.isdir(script_path):
                    # 디렉토리인 경우 해당 디렉토리에서 .py 파일 찾기
                    py_files = [f for f in os.listdir(script_path) if f.endswith('.py')]
                    if py_files:
                        script_path = os.path.join(script_path, py_files[0])
                        print(f"🔍 디렉토리에서 찾은 Selenium 스크립트: {script_path}")
                    else:
                        response = jsonify({'error': f'디렉토리 {script_path}에서 .py 파일을 찾을 수 없습니다'})
                        return add_cors_headers(response), 400
                
                absolute_script_path = os.path.abspath(script_path)
                if not os.path.exists(absolute_script_path):
                    response = jsonify({'error': f'Selenium 스크립트 파일을 찾을 수 없습니다: {absolute_script_path}'})
                    return add_cors_headers(response), 400
                
                result = subprocess.run(
                    ['python', absolute_script_path],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5분 타임아웃
                    cwd=os.path.dirname(absolute_script_path) if os.path.dirname(absolute_script_path) else None
                )
            
            execution_duration = time.time() - start_time
            
            # 스크린샷 경로 생성 (Playwright의 경우)
            screenshot_path = None
            if script_type == 'playwright' and result.returncode == 0:
                # Playwright 테스트 결과에서 스크린샷 경로 추출
                try:
                    import json
                    import os
                    from datetime import datetime
                    
                    # 테스트 결과 디렉토리 생성
                    screenshot_dir = os.path.join('screenshots', f'testcase_{id}')
                    os.makedirs(screenshot_dir, exist_ok=True)
                    
                    # 스크린샷 파일명 생성
                    timestamp = format_kst_datetime(get_kst_now(), '%Y%m%d_%H%M%S')
                    screenshot_path = os.path.join(screenshot_dir, f'screenshot_{timestamp}.png')
                    
                    # Playwright 실행 결과에서 스크린샷 복사 (실제 구현에서는 더 복잡)
                    if os.path.exists('test-results'):
                        import shutil
                        for root, dirs, files in os.walk('test-results'):
                            for file in files:
                                if file.endswith('.png'):
                                    shutil.copy2(os.path.join(root, file), screenshot_path)
                                    break
                except Exception as e:
                    print(f"스크린샷 처리 중 오류: {e}")
            
            # 실행 결과 저장
            test_result = TestResult(
                test_case_id=id,
                result='Pass' if result.returncode == 0 else 'Fail',
                environment=test_case.environment,
                execution_duration=execution_duration,
                error_message=result.stderr if result.returncode != 0 else None,
                screenshot=screenshot_path
            )
            db.session.add(test_result)
            db.session.commit()
            
            response = jsonify({
                'message': '자동화 코드 실행 완료',
                'result': 'Pass' if result.returncode == 0 else 'Fail',
                'output': result.stdout,
                'error': result.stderr,
                'execution_duration': execution_duration,
                'screenshot_path': screenshot_path
            })
            return add_cors_headers(response), 200
        else:
            response = jsonify({'error': '지원하지 않는 자동화 코드 타입입니다'})
            return add_cors_headers(response), 400
        
    except subprocess.TimeoutExpired:
        response = jsonify({'error': '자동화 코드 실행 시간이 초과되었습니다'})
        return add_cors_headers(response), 408
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500 

# 테스트 케이스 템플릿 API
@testcases_bp.route('/templates', methods=['GET'])
@guest_allowed
def get_templates():
    """템플릿 목록 조회"""
    try:
        # 검색 및 필터링 파라미터
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        tags = request.args.get('tags', '')
        is_public = request.args.get('public', '')
        
        query = TestCaseTemplate.query
        
        # 검색어 필터링
        if search:
            query = query.filter(
                db.or_(
                    TestCaseTemplate.name.contains(search),
                    TestCaseTemplate.description.contains(search),
                    TestCaseTemplate.main_category.contains(search),
                    TestCaseTemplate.sub_category.contains(search)
                )
            )
        
        # 카테고리 필터링
        if category:
            query = query.filter(TestCaseTemplate.main_category == category)
        
        # 태그 필터링
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                query = query.filter(TestCaseTemplate.tags.contains(tag))
        
        # 공개 여부 필터링
        if is_public == 'true':
            query = query.filter(TestCaseTemplate.is_public == True)
        
        # 사용 횟수순으로 정렬
        templates = query.order_by(TestCaseTemplate.usage_count.desc()).all()
        
        data = [{
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'main_category': t.main_category,
            'sub_category': t.sub_category,
            'detail_category': t.detail_category,
            'pre_condition': t.pre_condition,
            'expected_result': t.expected_result,
            'test_steps': t.test_steps,
            'automation_code_path': t.automation_code_path,
            'automation_code_type': t.automation_code_type,
            'tags': json.loads(t.tags) if t.tags else [],
            'created_by': t.created_by,
            'created_at': t.created_at.isoformat() if t.created_at else None,
            'updated_at': t.updated_at.isoformat() if t.updated_at else None,
            'is_public': t.is_public,
            'usage_count': t.usage_count,
            'creator_name': t.creator.username if t.creator else 'Unknown'
        } for t in templates]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"템플릿 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/templates', methods=['POST'])
@user_required
def create_template():
    """템플릿 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name'):
            response = jsonify({'error': '템플릿명은 필수입니다'})
            return add_cors_headers(response), 400
        
        template = TestCaseTemplate(
            name=data['name'],
            description=data.get('description', ''),
            main_category=data.get('main_category', ''),
            sub_category=data.get('sub_category', ''),
            detail_category=data.get('detail_category', ''),
            pre_condition=data.get('pre_condition', ''),
            expected_result=data.get('expected_result', ''),
            test_steps=data.get('test_steps', ''),
            automation_code_path=data.get('automation_code_path', ''),
            automation_code_type=data.get('automation_code_type', 'playwright'),
            tags=json.dumps(data.get('tags', [])),
            created_by=request.user.id,
            is_public=data.get('is_public', False)
        )
        
        db.session.add(template)
        db.session.commit()
        
        response = jsonify({
            'message': '템플릿이 성공적으로 생성되었습니다.',
            'id': template.id
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        logger.error(f"템플릿 생성 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/templates/<int:id>/apply', methods=['POST'])
@user_required
def apply_template(id):
    """템플릿을 테스트 케이스로 적용"""
    try:
        template = TestCaseTemplate.query.get_or_404(id)
        data = request.get_json()
        
        # 폴더 ID 필수
        if not data.get('folder_id'):
            response = jsonify({'error': '폴더 ID는 필수입니다'})
            return add_cors_headers(response), 400
        
        # 템플릿을 기반으로 테스트 케이스 생성
        test_case = TestCase(
            name=template.name,
            description=template.description,
            main_category=template.main_category,
            sub_category=template.sub_category,
            detail_category=template.detail_category,
            pre_condition=template.pre_condition,
            expected_result=template.expected_result,
            remark=template.test_steps,
            folder_id=data['folder_id'],
            automation_code_path=template.automation_code_path,
            automation_code_type=template.automation_code_type,
            environment='dev',  # 기본값
            creator_id=request.user.id
        )
        
        db.session.add(test_case)
        
        # 템플릿 사용 횟수 증가
        template.usage_count += 1
        
        db.session.commit()
        
        response = jsonify({
            'message': '템플릿이 성공적으로 적용되었습니다.',
            'test_case_id': test_case.id
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        logger.error(f"템플릿 적용 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500 

# 자동화 연동 API
@testcases_bp.route('/testcases/<int:id>/automation', methods=['GET'])
@guest_allowed
def get_test_case_automation(id):
    """테스트 케이스 자동화 정보 조회"""
    try:
        test_case = TestCase.query.get_or_404(id)
        
        # 자동화 스크립트 정보
        automation_info = {
            'has_automation': bool(test_case.automation_code_path),
            'script_path': test_case.automation_code_path,
            'script_type': test_case.automation_code_type,
            'last_execution': None,
            'execution_count': 0,
            'success_rate': 0
        }
        
        # 실행 이력 조회
        if test_case.automation_code_path:
            executions = TestResult.query.filter_by(
                automation_test_id=id
            ).order_by(TestResult.executed_at.desc()).limit(10).all()
            
            if executions:
                automation_info['last_execution'] = executions[0].executed_at.isoformat()
                automation_info['execution_count'] = len(executions)
                
                # 성공률 계산
                success_count = sum(1 for e in executions if e.result == 'Pass')
                automation_info['success_rate'] = (success_count / len(executions)) * 100
        
        response = jsonify(automation_info)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"자동화 정보 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases/<int:id>/automation', methods=['POST'])
@user_required
def link_automation_script(id):
    """테스트 케이스에 자동화 스크립트 연결"""
    try:
        test_case = TestCase.query.get_or_404(id)
        data = request.get_json()
        
        # 스크립트 경로 검증
        script_path = data.get('script_path')
        if not script_path:
            response = jsonify({'error': '스크립트 경로는 필수입니다'})
            return add_cors_headers(response), 400
        
        # 파일 존재 여부 확인 (선택사항)
        import os
        full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), script_path)
        if not os.path.exists(full_path):
            logger.warning(f"자동화 스크립트 파일이 존재하지 않습니다: {full_path}")
        
        # 테스트 케이스 업데이트
        test_case.automation_code_path = script_path
        test_case.automation_code_type = data.get('script_type', 'playwright')
        
        db.session.commit()
        
        # 히스토리 추적
        try:
            track_test_case_change(id, 'automation_code_path', None, script_path, request.user.id)
        except Exception as e:
            logger.warning(f"자동화 연결 히스토리 추적 실패: {str(e)}")
        
        response = jsonify({
            'message': '자동화 스크립트가 성공적으로 연결되었습니다.',
            'script_path': script_path
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"자동화 스크립트 연결 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/automation/suggest', methods=['GET'])
@guest_allowed
def suggest_automation_scripts():
    """자동화 스크립트 추천"""
    try:
        # 미연결된 테스트 케이스들
        unlinked_test_cases = TestCase.query.filter(
            db.or_(
                TestCase.automation_code_path.is_(None),
                TestCase.automation_code_path == ''
            )
        ).all()
        
        suggestions = []
        
        for tc in unlinked_test_cases:
            # 카테고리 기반 추천
            if tc.main_category:
                # 유사한 카테고리의 자동화 스크립트 찾기
                similar_scripts = TestCase.query.filter(
                    TestCase.main_category == tc.main_category,
                    TestCase.automation_code_path.isnot(None),
                    TestCase.automation_code_path != ''
                ).limit(3).all()
                
                if similar_scripts:
                    suggestions.append({
                        'test_case_id': tc.id,
                        'test_case_name': tc.name,
                        'category': tc.main_category,
                        'suggested_scripts': [
                            {
                                'script_path': script.automation_code_path,
                                'script_type': script.automation_code_type,
                                'similarity': 'category_match'
                            } for script in similar_scripts
                        ]
                    })
        
        response = jsonify(suggestions)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"자동화 스크립트 추천 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500 

# 테스트 계획 API
@testcases_bp.route('/test-plans', methods=['GET'])
@guest_allowed
def get_test_plans():
    """테스트 계획 목록 조회"""
    try:
        plans = TestPlan.query.order_by(TestPlan.created_at.desc()).all()
        
        data = [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'version': p.version,
            'environment': p.environment,
            'start_date': p.start_date.isoformat() if p.start_date else None,
            'end_date': p.end_date.isoformat() if p.end_date else None,
            'status': p.status,
            'priority': p.priority,
            'created_by': p.created_by,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None,
            'creator_name': p.creator.username if p.creator else 'Unknown',
            'test_case_count': len(p.test_cases)
        } for p in plans]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"테스트 계획 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/test-plans', methods=['POST'])
@user_required
def create_test_plan():
    """테스트 계획 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name'):
            response = jsonify({'error': '계획명은 필수입니다'})
            return add_cors_headers(response), 400
        
        plan = TestPlan(
            name=data['name'],
            description=data.get('description', ''),
            version=data.get('version', '1.0'),
            environment=data.get('environment', 'dev'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            status=data.get('status', 'draft'),
            priority=data.get('priority', 'medium'),
            created_by=request.user.id
        )
        
        db.session.add(plan)
        db.session.commit()
        
        response = jsonify({
            'message': '테스트 계획이 성공적으로 생성되었습니다.',
            'id': plan.id
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        logger.error(f"테스트 계획 생성 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/test-plans/<int:id>/test-cases', methods=['POST'])
@user_required
def add_test_cases_to_plan(id):
    """테스트 계획에 테스트 케이스 추가"""
    try:
        plan = TestPlan.query.get_or_404(id)
        data = request.get_json()
        
        test_case_ids = data.get('test_case_ids', [])
        if not test_case_ids:
            response = jsonify({'error': '테스트 케이스 ID 목록이 필요합니다'})
            return add_cors_headers(response), 400
        
        added_count = 0
        for test_case_id in test_case_ids:
            # 이미 추가된 테스트 케이스인지 확인
            existing = TestPlanTestCase.query.filter_by(
                test_plan_id=id,
                test_case_id=test_case_id
            ).first()
            
            if not existing:
                plan_test_case = TestPlanTestCase(
                    test_plan_id=id,
                    test_case_id=test_case_id,
                    execution_order=len(plan.test_cases) + 1,
                    estimated_duration=data.get('estimated_duration', 30),
                    assigned_to=data.get('assigned_to'),
                    notes=data.get('notes', '')
                )
                db.session.add(plan_test_case)
                added_count += 1
        
        db.session.commit()
        
        response = jsonify({
            'message': f'{added_count}개 테스트 케이스가 계획에 추가되었습니다.',
            'added_count': added_count
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"테스트 케이스 추가 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/test-plans/<int:id>', methods=['GET'])
@guest_allowed
def get_test_plan_detail(id):
    """테스트 계획 상세 조회"""
    try:
        plan = TestPlan.query.get_or_404(id)
        
        # 계획에 포함된 테스트 케이스들
        test_cases = []
        for ptc in plan.test_cases:
            tc = ptc.test_case
            test_cases.append({
                'id': tc.id,
                'name': tc.name,
                'main_category': tc.main_category,
                'sub_category': tc.sub_category,
                'detail_category': tc.detail_category,
                'environment': tc.environment,
                'result_status': tc.result_status,
                'execution_order': ptc.execution_order,
                'estimated_duration': ptc.estimated_duration,
                'assigned_to': ptc.assigned_to,
                'assignee_name': ptc.assignee.username if ptc.assignee else None,
                'notes': ptc.notes
            })
        
        # 실행 순서대로 정렬
        test_cases.sort(key=lambda x: x['execution_order'])
        
        data = {
            'id': plan.id,
            'name': plan.name,
            'description': plan.description,
            'version': plan.version,
            'environment': plan.environment,
            'start_date': plan.start_date.isoformat() if plan.start_date else None,
            'end_date': plan.end_date.isoformat() if plan.end_date else None,
            'status': plan.status,
            'priority': plan.priority,
            'created_by': plan.created_by,
            'created_at': plan.created_at.isoformat() if plan.created_at else None,
            'updated_at': plan.updated_at.isoformat() if plan.updated_at else None,
            'creator_name': plan.creator.username if plan.creator else 'Unknown',
            'test_cases': test_cases,
            'total_estimated_duration': sum(tc['estimated_duration'] for tc in test_cases if tc['estimated_duration'])
        }
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"테스트 계획 상세 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500 

# 리포팅 API
@testcases_bp.route('/reports/summary', methods=['GET'])
@guest_allowed
def get_test_summary_report():
    """테스트 결과 요약 리포트"""
    try:
        # 환경별 통계
        environment_stats = db.session.query(
            TestCase.environment,
            db.func.count(TestCase.id).label('total'),
            db.func.sum(db.case([(TestCase.result_status == 'Pass', 1)], else_=0)).label('passed'),
            db.func.sum(db.case([(TestCase.result_status == 'Fail', 1)], else_=0)).label('failed'),
            db.func.sum(db.case([(TestCase.result_status == 'N/T', 1)], else_=0)).label('not_tested'),
            db.func.sum(db.case([(TestCase.result_status == 'N/A', 1)], else_=0)).label('not_applicable'),
            db.func.sum(db.case([(TestCase.result_status == 'Block', 1)], else_=0)).label('blocked')
        ).group_by(TestCase.environment).all()
        
        # 카테고리별 통계
        category_stats = db.session.query(
            TestCase.main_category,
            db.func.count(TestCase.id).label('total'),
            db.func.sum(db.case([(TestCase.result_status == 'Pass', 1)], else_=0)).label('passed'),
            db.func.sum(db.case([(TestCase.result_status == 'Fail', 1)], else_=0)).label('failed')
        ).group_by(TestCase.main_category).all()
        
        # 자동화 통계
        automation_stats = db.session.query(
            db.func.count(TestCase.id).label('total'),
            db.func.sum(db.case([(TestCase.automation_code_path.isnot(None), 1)], else_=0)).label('automated'),
            db.func.sum(db.case([(TestCase.automation_code_path.is_(None), 1)], else_=0)).label('manual')
        ).first()
        
        # 최근 실행 결과
        recent_results = db.session.query(
            TestResult.result,
            db.func.count(TestResult.id).label('count')
        ).filter(
            TestResult.executed_at >= datetime.utcnow() - timedelta(days=30)
        ).group_by(TestResult.result).all()
        
        data = {
            'environment_stats': [{
                'environment': stat.environment or 'Unknown',
                'total': stat.total,
                'passed': stat.passed or 0,
                'failed': stat.failed or 0,
                'not_tested': stat.not_tested or 0,
                'not_applicable': stat.not_applicable or 0,
                'blocked': stat.blocked or 0,
                'pass_rate': round((stat.passed or 0) / stat.total * 100, 1) if stat.total > 0 else 0
            } for stat in environment_stats],
            
            'category_stats': [{
                'category': stat.main_category or 'Unknown',
                'total': stat.total,
                'passed': stat.passed or 0,
                'failed': stat.failed or 0,
                'pass_rate': round((stat.passed or 0) / stat.total * 100, 1) if stat.total > 0 else 0
            } for stat in category_stats],
            
            'automation_stats': {
                'total': automation_stats.total,
                'automated': automation_stats.automated or 0,
                'manual': automation_stats.manual or 0,
                'automation_rate': round((automation_stats.automated or 0) / automation_stats.total * 100, 1) if automation_stats.total > 0 else 0
            },
            
            'recent_results': [{
                'result': stat.result or 'Unknown',
                'count': stat.count
            } for stat in recent_results],
            
            'generated_at': datetime.utcnow().isoformat()
        }
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"요약 리포트 생성 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/reports/export', methods=['POST'])
@user_required
def export_test_report():
    """테스트 리포트 엑셀 내보내기"""
    try:
        data = request.get_json()
        report_type = data.get('type', 'summary')
        
        if report_type == 'summary':
            output, filename = ReportService.generate_test_summary_report('excel')
            
            response = send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
            return add_cors_headers(response), 200
            
        else:
            response = jsonify({'error': '지원하지 않는 리포트 타입입니다'})
            return add_cors_headers(response), 400
        
    except Exception as e:
        logger.error(f"리포트 내보내기 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# get_test_summary_report_data 함수는 ReportService로 이동됨 