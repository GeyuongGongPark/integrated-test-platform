"""
CI/CD 통합 서비스
GitHub Actions, Jenkins 등과의 통합 처리
"""
import requests
import hmac
import hashlib
import json
from models import db, CICDIntegration, CICDExecution, TestCase, TestResult
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
from tasks import execute_test_case_batch

logger = get_logger(__name__)

class CICDService:
    """CI/CD 통합 서비스"""
    
    def verify_webhook_signature(self, payload, signature, secret):
        """웹훅 서명 검증"""
        try:
            if not secret:
                return False
            
            # GitHub 서명 검증
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # GitHub는 'sha256=' 접두사 사용
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"웹훅 서명 검증 오류: {str(e)}")
            return False
    
    def handle_github_webhook(self, payload, signature, integration):
        """GitHub 웹훅 처리"""
        try:
            # 서명 검증
            if integration.webhook_secret:
                if not self.verify_webhook_signature(
                    json.dumps(payload),
                    signature,
                    integration.webhook_secret
                ):
                    logger.warning("GitHub 웹훅 서명 검증 실패")
                    return None
            
            event_type = payload.get('action') or payload.get('event')
            event_data = payload
            
            # Push 이벤트
            if 'push' in event_type.lower() or 'push' in payload:
                return self._handle_github_push(event_data, integration)
            
            # Pull Request 이벤트
            elif 'pull_request' in event_type.lower() or 'pull_request' in payload:
                return self._handle_github_pr(event_data, integration)
            
            # Tag 이벤트
            elif 'create' in event_type.lower() and payload.get('ref_type') == 'tag':
                return self._handle_github_tag(event_data, integration)
            
            else:
                logger.info(f"처리하지 않는 GitHub 이벤트: {event_type}")
                return None
                
        except Exception as e:
            logger.error(f"GitHub 웹훅 처리 오류: {str(e)}")
            return None
    
    def _handle_github_push(self, event_data, integration):
        """GitHub Push 이벤트 처리"""
        try:
            if not integration.trigger_on_push:
                return None
            
            # 실행 기록 생성
            execution = CICDExecution(
                integration_id=integration.id,
                trigger_type='push',
                trigger_source='github',
                trigger_event=json.dumps(event_data),
                status='running'
            )
            db.session.add(execution)
            db.session.commit()
            
            # 테스트 케이스 필터 적용
            test_case_ids = self._get_test_case_ids_from_filter(integration.test_case_filter)
            
            if test_case_ids:
                # Celery를 통해 비동기 실행
                from tasks import execute_test_case_batch
                task = execute_test_case_batch.delay(
                    test_case_ids,
                    environment='dev',  # 기본값
                    max_workers=5
                )
                
                execution.status = 'running'
                db.session.commit()
                
                logger.info(f"GitHub Push 이벤트로 테스트 실행 시작: {len(test_case_ids)}개")
                return execution
            else:
                execution.status = 'completed'
                execution.error_message = '실행할 테스트 케이스가 없습니다'
                db.session.commit()
                return execution
                
        except Exception as e:
            logger.error(f"GitHub Push 처리 오류: {str(e)}")
            return None
    
    def _handle_github_pr(self, event_data, integration):
        """GitHub Pull Request 이벤트 처리"""
        try:
            if not integration.trigger_on_pr:
                return None
            
            pr_data = event_data.get('pull_request', {})
            pr_number = pr_data.get('number')
            pr_url = pr_data.get('html_url')
            action = event_data.get('action')  # opened, synchronize, closed 등
            
            # PR이 열리거나 업데이트된 경우만 실행
            if action not in ['opened', 'synchronize', 'reopened']:
                return None
            
            # 실행 기록 생성
            execution = CICDExecution(
                integration_id=integration.id,
                trigger_type='pull_request',
                trigger_source='github',
                trigger_event=json.dumps(event_data),
                status='running',
                pr_number=pr_number,
                pr_url=pr_url
            )
            db.session.add(execution)
            db.session.commit()
            
            # 테스트 케이스 필터 적용
            test_case_ids = self._get_test_case_ids_from_filter(integration.test_case_filter)
            
            if test_case_ids:
                # Celery를 통해 비동기 실행
                from tasks import execute_test_case_batch
                task = execute_test_case_batch.delay(
                    test_case_ids,
                    environment='dev',
                    max_workers=5
                )
                
                execution.status = 'running'
                db.session.commit()
                
                logger.info(f"GitHub PR 이벤트로 테스트 실행 시작: PR #{pr_number}, {len(test_case_ids)}개 테스트")
                return execution
            else:
                execution.status = 'completed'
                execution.error_message = '실행할 테스트 케이스가 없습니다'
                db.session.commit()
                return execution
                
        except Exception as e:
            logger.error(f"GitHub PR 처리 오류: {str(e)}")
            return None
    
    def _handle_github_tag(self, event_data, integration):
        """GitHub Tag 이벤트 처리"""
        try:
            if not integration.trigger_on_tag:
                return None
            
            # Tag 이벤트 처리 (Push와 유사)
            return self._handle_github_push(event_data, integration)
            
        except Exception as e:
            logger.error(f"GitHub Tag 처리 오류: {str(e)}")
            return None
    
    def handle_jenkins_webhook(self, payload, integration):
        """Jenkins 웹훅 처리"""
        try:
            build_status = payload.get('build', {}).get('status')
            build_url = payload.get('build', {}).get('full_url')
            
            # 실행 기록 생성
            execution = CICDExecution(
                integration_id=integration.id,
                trigger_type='jenkins_build',
                trigger_source='jenkins',
                trigger_event=json.dumps(payload),
                status='running'
            )
            db.session.add(execution)
            db.session.commit()
            
            # 빌드 성공 시 테스트 실행
            if build_status == 'SUCCESS':
                test_case_ids = self._get_test_case_ids_from_filter(integration.test_case_filter)
                
                if test_case_ids:
                    from tasks import execute_test_case_batch
                    task = execute_test_case_batch.delay(
                        test_case_ids,
                        environment='dev',
                        max_workers=5
                    )
                    
                    execution.status = 'running'
                    db.session.commit()
                    
                    logger.info(f"Jenkins 빌드 성공으로 테스트 실행 시작: {len(test_case_ids)}개")
                    return execution
            
            execution.status = 'completed'
            execution.error_message = f'Jenkins 빌드 상태: {build_status}'
            db.session.commit()
            return execution
            
        except Exception as e:
            logger.error(f"Jenkins 웹훅 처리 오류: {str(e)}")
            return None
    
    def _get_test_case_ids_from_filter(self, filter_json):
        """필터에서 테스트 케이스 ID 목록 추출"""
        try:
            if not filter_json:
                # 필터가 없으면 모든 활성 테스트 케이스
                test_cases = TestCase.query.filter_by(status='active').all()
                return [tc.id for tc in test_cases]
            
            filter_data = json.loads(filter_json) if isinstance(filter_json, str) else filter_json
            
            query = TestCase.query.filter_by(status='active')
            
            # 폴더 필터
            if 'folder_ids' in filter_data and filter_data['folder_ids']:
                query = query.filter(TestCase.folder_id.in_(filter_data['folder_ids']))
            
            # 환경 필터
            if 'environments' in filter_data and filter_data['environments']:
                query = query.filter(TestCase.environment.in_(filter_data['environments']))
            
            # 카테고리 필터
            if 'categories' in filter_data and filter_data['categories']:
                query = query.filter(TestCase.main_category.in_(filter_data['categories']))
            
            test_cases = query.all()
            return [tc.id for tc in test_cases]
            
        except Exception as e:
            logger.error(f"테스트 케이스 필터 처리 오류: {str(e)}")
            return []
    
    def update_execution_with_results(self, execution_id, test_results):
        """실행 결과로 실행 기록 업데이트"""
        try:
            execution = CICDExecution.query.get(execution_id)
            if not execution:
                return False
            
            execution.status = 'completed'
            execution.completed_at = get_kst_now()
            execution.test_results = json.dumps(test_results)
            
            # 실행된 테스트 케이스 ID 목록
            executed_ids = [r.get('test_case_id') for r in test_results if 'test_case_id' in r]
            execution.executed_test_cases = json.dumps(executed_ids)
            
            db.session.commit()
            
            # PR 코멘트 업데이트 (GitHub의 경우)
            if execution.pr_number and execution.integration:
                self._update_pr_comment(execution, test_results)
            
            return True
            
        except Exception as e:
            logger.error(f"실행 결과 업데이트 오류: {str(e)}")
            return False
    
    def _update_pr_comment(self, execution, test_results):
        """GitHub PR에 테스트 결과 코멘트 추가"""
        try:
            integration = execution.integration
            config = json.loads(integration.config) if integration.config else {}
            
            github_token = config.get('github_token')
            repo = config.get('repository')  # owner/repo 형식
            
            if not github_token or not repo:
                logger.warning("GitHub 토큰 또는 저장소 정보가 없습니다")
                return False
            
            # 테스트 결과 요약
            total = len(test_results)
            passed = sum(1 for r in test_results if r.get('result') == 'Pass')
            failed = total - passed
            
            comment_body = f"""## 🧪 테스트 실행 결과

**실행 시간**: {execution.started_at.isoformat() if execution.started_at else 'N/A'}

### 요약
- ✅ 통과: {passed}
- ❌ 실패: {failed}
- 📊 전체: {total}
- 📈 통과율: {round((passed / total * 100) if total > 0 else 0, 2)}%

### 상세 결과
"""
            
            for result in test_results:
                status_emoji = '✅' if result.get('result') == 'Pass' else '❌'
                comment_body += f"{status_emoji} {result.get('test_case_name', 'Unknown')}: {result.get('result', 'Unknown')}\n"
            
            # GitHub API로 코멘트 추가
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f"https://api.github.com/repos/{repo}/issues/{execution.pr_number}/comments"
            data = {
                'body': comment_body
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                comment_data = response.json()
                execution.pr_comment_id = str(comment_data.get('id'))
                db.session.commit()
                logger.info(f"PR 코멘트 추가 완료: PR #{execution.pr_number}")
                return True
            else:
                logger.error(f"PR 코멘트 추가 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"PR 코멘트 업데이트 오류: {str(e)}")
            return False

# 전역 CI/CD 서비스 인스턴스
cicd_service = CICDService()

