"""
Celery 태스크 정의
테스트 실행을 비동기로 처리하는 태스크들
"""
from celery_app import celery_app
from flask import Flask
from models import db, TestCase, TestResult, AutomationTest, PerformanceTest, TestExecution
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
import subprocess
import os
import time
import json
from datetime import datetime

logger = get_logger(__name__)

def create_app():
    """Flask 앱 생성 (Celery 태스크에서 사용)"""
    from app import app
    return app

@celery_app.task(bind=True, name='tasks.execute_test_case')
def execute_test_case(self, test_case_id, environment='dev', execution_parameters=None):
    """
    테스트 케이스 실행 태스크
    
    Args:
        test_case_id: 테스트 케이스 ID
        environment: 실행 환경
        execution_parameters: 실행 파라미터 (dict)
    
    Returns:
        dict: 실행 결과
    """
    app = create_app()
    with app.app_context():
        try:
            test_case = TestCase.query.get(test_case_id)
            if not test_case:
                raise ValueError(f"테스트 케이스를 찾을 수 없습니다: {test_case_id}")

            # 테스트 단계(JSON)만 있고 자동화 코드 경로가 없는 경우 → 단계 실행기로 실행
            if not test_case.automation_code_path and getattr(test_case, 'test_steps', None):
                try:
                    import json
                    steps_data = json.loads(test_case.test_steps)
                except (TypeError, ValueError):
                    steps_data = None
                if isinstance(steps_data, list) and len(steps_data) > 0:
                    base_url = (execution_parameters or {}).get('baseUrl') or (execution_parameters or {}).get('base_url')
                    from utils.playwright_steps_runner import run_playwright_steps
                    _start = time.time()
                    run_result = run_playwright_steps(steps_data, base_url=base_url)
                    execution_duration = time.time() - _start
                    test_result = TestResult(
                        test_case_id=test_case_id,
                        result=run_result['status'],
                        environment=test_case.environment or environment,
                        execution_duration=execution_duration,
                        error_message=run_result.get('error')
                    )
                    db.session.add(test_result)
                    db.session.commit()
                    return {
                        'status': run_result['status'],
                        'output': run_result.get('output', ''),
                        'error': run_result.get('error'),
                        'execution_duration': execution_duration
                    }
                # test_steps 비어 있음 → 아래에서 에러
                # test_steps가 비어 있거나 잘못된 경우 아래에서 에러 처리
            
            if not test_case.automation_code_path:
                raise ValueError("자동화 코드 경로 또는 테스트 단계(test_steps)를 설정해 주세요")
            
            # 테스트 데이터 가져오기 (매핑된 데이터 세트가 있는 경우)
            test_data = None
            try:
                from services.test_data_service import test_data_service
                test_data = test_data_service.get_data_for_test_case(test_case_id, environment)
                if test_data:
                    # execution_parameters에 테스트 데이터 병합
                    if execution_parameters is None:
                        execution_parameters = {}
                    execution_parameters.update(test_data)
                    logger.info(f"테스트 데이터 적용: {test_case.name}")
            except Exception as data_error:
                logger.warning(f"테스트 데이터 로드 실패: {str(data_error)}")
            
            script_path = test_case.automation_code_path
            script_type = test_case.automation_code_type or 'playwright'
            
            logger.info(f"테스트 케이스 실행 시작: {test_case.name} (ID: {test_case_id})")
            
            start_time = time.time()
            result_status = 'Fail'
            error_message = None
            output = ''
            
            try:
                # 스크립트 경로를 절대 경로로 변환
                if not os.path.isabs(script_path):
                    backend_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(backend_dir)
                    script_path = os.path.join(project_root, script_path)
                
                absolute_script_path = os.path.abspath(script_path)
                
                if not os.path.exists(absolute_script_path):
                    raise FileNotFoundError(f"스크립트 파일을 찾을 수 없습니다: {absolute_script_path}")
                
                # 스크립트 타입에 따라 실행
                if script_type == 'k6':
                    from engines.k6_engine import k6_engine
                    result = k6_engine.execute_test(absolute_script_path, execution_parameters or {})
                    result_status = result.get('status', 'Fail')
                    output = result.get('output', '')
                    error_message = result.get('error')
                    
                elif script_type == 'playwright':
                    result = subprocess.run(
                        ['npx', 'playwright', 'test', absolute_script_path, '--reporter=json'],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=os.path.dirname(absolute_script_path) if os.path.dirname(absolute_script_path) else None
                    )
                    result_status = 'Pass' if result.returncode == 0 else 'Fail'
                    output = result.stdout
                    error_message = result.stderr if result.returncode != 0 else None
                    
                elif script_type == 'selenium':
                    result = subprocess.run(
                        ['python', absolute_script_path],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=os.path.dirname(absolute_script_path) if os.path.dirname(absolute_script_path) else None
                    )
                    result_status = 'Pass' if result.returncode == 0 else 'Fail'
                    output = result.stdout
                    error_message = result.stderr if result.returncode != 0 else None
                else:
                    raise ValueError(f"지원하지 않는 스크립트 타입: {script_type}")
                
            except subprocess.TimeoutExpired:
                result_status = 'Fail'
                error_message = '테스트 실행 시간이 초과되었습니다'
            except Exception as e:
                result_status = 'Fail'
                error_message = str(e)
                logger.error(f"테스트 실행 중 오류: {str(e)}")
            
            execution_duration = time.time() - start_time
            
            # 결과 저장
            test_result = TestResult(
                test_case_id=test_case_id,
                result=result_status,
                environment=environment,
                execution_duration=execution_duration,
                executed_at=get_kst_now(),
                executed_by='system',
                error_message=error_message,
                notes=output[:1000] if output else None  # 최대 1000자
            )
            
            db.session.add(test_result)
            db.session.commit()
            
            # 알림 생성
            try:
                from services.notification_service import notification_service
                if result_status == 'Fail':
                    notification_service.notify_test_failed(test_case_id, test_result.id)
                else:
                    notification_service.notify_test_completed(test_case_id, test_result.id, result_status)
            except Exception as notify_error:
                logger.error(f"알림 생성 오류: {str(notify_error)}")
            
            # WebSocket을 통해 실시간 업데이트
            try:
                from socketio_handlers import emit_test_result
                emit_test_result(test_result.id)
            except Exception as socket_error:
                logger.error(f"WebSocket 업데이트 오류: {str(socket_error)}")
            
            logger.info(f"테스트 케이스 실행 완료: {test_case.name} - {result_status}")
            
            return {
                'status': 'success',
                'test_case_id': test_case_id,
                'result': result_status,
                'execution_duration': execution_duration,
                'result_id': test_result.id,
                'error': error_message
            }
            
        except Exception as e:
            logger.error(f"태스크 실행 오류: {str(e)}")
            raise

@celery_app.task(bind=True, name='tasks.execute_test_case_batch')
def execute_test_case_batch(self, test_case_ids, environment='dev', max_workers=5):
    """
    여러 테스트 케이스를 병렬로 실행하는 태스크
    
    Args:
        test_case_ids: 테스트 케이스 ID 리스트
        environment: 실행 환경
        max_workers: 최대 동시 실행 수
    
    Returns:
        dict: 실행 결과 요약
    """
    app = create_app()
    with app.app_context():
        try:
            from celery import group
            
            # 태스크 그룹 생성 (병렬 실행)
            job = group(
                execute_test_case.s(test_id, environment) 
                for test_id in test_case_ids
            )
            
            # 결과 수집
            result = job.apply_async()
            results = result.get()  # 모든 태스크 완료 대기
            
            # 결과 요약
            total = len(test_case_ids)
            passed = sum(1 for r in results if r.get('result') == 'Pass')
            failed = total - passed
            
            # CI/CD 실행 기록 업데이트 (있는 경우)
            try:
                # 실행 컨텍스트에서 execution_id 가져오기 (있는 경우)
                execution_id = self.request.get('execution_id') if hasattr(self, 'request') else None
                if execution_id:
                    from services.cicd_service import cicd_service
                    cicd_service.update_execution_with_results(execution_id, results)
            except Exception as cicd_error:
                logger.error(f"CI/CD 실행 기록 업데이트 오류: {str(cicd_error)}")
            
            return {
                'status': 'success',
                'total': total,
                'passed': passed,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"배치 실행 오류: {str(e)}")
            raise

@celery_app.task(bind=True, name='tasks.execute_automation_test')
def execute_automation_test(self, automation_test_id, environment='dev'):
    """
    자동화 테스트 실행 태스크
    
    Args:
        automation_test_id: 자동화 테스트 ID
        environment: 실행 환경
    
    Returns:
        dict: 실행 결과
    """
    app = create_app()
    with app.app_context():
        try:
            test = AutomationTest.query.get(automation_test_id)
            if not test:
                raise ValueError(f"자동화 테스트를 찾을 수 없습니다: {automation_test_id}")
            
            execution_start = get_kst_now()
            time.sleep(2)  # 시뮬레이션 (실제로는 테스트 실행)
            execution_end = get_kst_now()
            execution_duration = (execution_end - execution_start).total_seconds()
            
            status = 'Pass'
            result = TestResult(
                automation_test_id=automation_test_id,
                result=status,
                execution_time=execution_duration,
                environment=environment,
                executed_by='system',
                executed_at=execution_end
            )
            
            db.session.add(result)
            db.session.commit()
            
            return {
                'status': 'success',
                'automation_test_id': automation_test_id,
                'result': status,
                'execution_duration': execution_duration,
                'result_id': result.id
            }
            
        except Exception as e:
            logger.error(f"자동화 테스트 실행 오류: {str(e)}")
            raise

@celery_app.task(bind=True, name='tasks.execute_performance_test')
def execute_performance_test(self, performance_test_id, environment_vars=None):
    """
    성능 테스트 실행 태스크
    
    Args:
        performance_test_id: 성능 테스트 ID
        environment_vars: 환경 변수 (dict)
    
    Returns:
        dict: 실행 결과
    """
    app = create_app()
    with app.app_context():
        try:
            from engines.k6_engine import k6_engine
            
            pt = PerformanceTest.query.get(performance_test_id)
            if not pt:
                raise ValueError(f"성능 테스트를 찾을 수 없습니다: {performance_test_id}")
            
            env_vars = environment_vars or {}
            if pt.parameters:
                try:
                    base_params = json.loads(pt.parameters)
                    if isinstance(base_params, dict):
                        env_vars.update(base_params)
                except:
                    pass
            
            result = k6_engine.execute_test(pt.script_path, env_vars)
            
            execution = TestExecution(
                performance_test_id=pt.id,
                test_type='performance',
                status=result.get('status', 'Error'),
                result_summary=json.dumps(result)
            )
            
            db.session.add(execution)
            db.session.commit()
            
            return {
                'status': 'success',
                'performance_test_id': performance_test_id,
                'result': result.get('status'),
                'execution_id': execution.id
            }
            
        except Exception as e:
            logger.error(f"성능 테스트 실행 오류: {str(e)}")
            raise

