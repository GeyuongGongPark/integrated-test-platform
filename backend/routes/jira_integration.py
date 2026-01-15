"""
JIRA 연동 API 엔드포인트
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
from utils.jira_client import JiraClient, JiraIntegrationService
from utils.auth_decorators import user_required
from models import db, JiraIssue, JiraComment, TestCase, AutomationTest, PerformanceTest

jira_bp = Blueprint('jira', __name__, url_prefix='/api/jira')

# JIRA 클라이언트 초기화
jira_client = JiraClient()
jira_service = JiraIntegrationService(jira_client)

@jira_bp.route('/health', methods=['GET'])
def health_check():
    """JIRA 서버 상태 확인"""
    try:
        health_status = jira_client.health_check()
        return jsonify({
            'success': True,
            'data': health_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/projects', methods=['GET'])
@user_required
def get_projects():
    """JIRA 프로젝트 목록 조회"""
    try:
        projects = jira_client.get_projects()
        return jsonify({
            'success': True,
            'data': projects
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/issues', methods=['POST'])
# @user_required  # 개발 단계에서 임시로 비활성화
def create_issue():
    """이슈 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['summary']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        summary = data['summary']
        description = data.get('description', '')
        issue_type = data.get('issue_type', 'Task')
        priority = data.get('priority', 'Medium')
        assignee = data.get('assignee')
        labels = data.get('labels', [])
        
        # 이슈 생성
        issue = jira_client.create_issue(
            summary=summary,
            description=description,
            issue_type=issue_type,
            priority=priority,
            assignee=assignee,
            labels=labels
        )
        
        # 데이터베이스에 연동 정보 저장
        jira_integration = JiraIntegration(
            jira_issue_key=issue['key'],
            jira_issue_id=issue['id'],
            jira_project_key=issue['fields']['project']['key'],
            issue_type=issue_type,
            status=issue['fields']['status']['name'],
            priority=priority,
            summary=summary,
            description=description,
            assignee_account_id=assignee,
            labels=json.dumps(labels) if labels else None,
            last_sync_at=datetime.utcnow()
        )
        
        db.session.add(jira_integration)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'issue': issue,
                'integration_id': jira_integration.id
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/sync-issue', methods=['POST'])
# @user_required  # 개발 단계에서 임시로 비활성화
def sync_issue():
    """이슈를 데이터베이스에 동기화"""
    try:
        data = request.get_json()
        issue_key = data.get('issue_key')
        
        if not issue_key:
            return jsonify({
                'success': False,
                'error': 'issue_key가 필요합니다.'
            }), 400
        
        # JIRA에서 이슈 정보 가져오기
        issue_data = jira_client.get_issue(issue_key)
        
        if not issue_data:
            return jsonify({
                'success': False,
                'error': '이슈를 찾을 수 없습니다.'
            }), 404
        
        # 데이터베이스에 저장 또는 업데이트
        jira_integration = JiraIntegration.query.filter_by(jira_issue_key=issue_key).first()
        
        if not jira_integration:
            jira_integration = JiraIntegration()
            jira_integration.jira_issue_key = issue_key
            jira_integration.created_at = datetime.utcnow()
        
        # 이슈 정보 업데이트
        fields = issue_data.get('fields', {})
        jira_integration.summary = fields.get('summary', '')
        jira_integration.description = fields.get('description', '')
        jira_integration.status = fields.get('status', {}).get('name', '')
        jira_integration.priority = fields.get('priority', {}).get('name', '')
        jira_integration.issue_type = fields.get('issuetype', {}).get('name', '')
        jira_integration.assignee_account_id = fields.get('assignee', {}).get('accountId') if fields.get('assignee') else None
        jira_integration.labels = json.dumps(fields.get('labels', [])) if fields.get('labels') else None
        jira_integration.updated_at = datetime.utcnow()
        jira_integration.last_sync_at = datetime.utcnow()
        
        if not jira_integration.id:
            db.session.add(jira_integration)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '이슈가 성공적으로 동기화되었습니다.',
            'data': {
                'id': jira_integration.id,
                'jira_issue_key': jira_integration.jira_issue_key,
                'summary': jira_integration.summary
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/issues', methods=['GET'])
# @user_required  # 개발 단계에서 임시로 비활성화
def get_issues():
    """이슈 목록 조회 (페이지네이션 지원)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 데이터베이스에서 이슈 목록 조회
        pagination = JiraIntegration.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        issues = []
        for jira_integration in pagination.items:
            issues.append({
                'id': jira_integration.id,
                'jira_issue_key': jira_integration.jira_issue_key,
                'summary': jira_integration.summary,
                'description': jira_integration.description,
                'status': jira_integration.status,
                'priority': jira_integration.priority,
                'issue_type': jira_integration.issue_type,
                'assignee': jira_integration.assignee_account_id,
                'labels': jira_integration.labels,
                'created_at': jira_integration.created_at.isoformat() if jira_integration.created_at else None,
                'updated_at': jira_integration.updated_at.isoformat() if jira_integration.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'issues': issues,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/issues/<issue_key>', methods=['GET'])
@user_required
def get_issue(issue_key):
    """이슈 조회"""
    try:
        issue = jira_client.get_issue(issue_key)
        return jsonify({
            'success': True,
            'data': issue
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/issues/<issue_key>', methods=['PUT'])
@user_required
def update_issue(issue_key):
    """이슈 업데이트"""
    try:
        data = request.get_json()
        
        # 이슈 업데이트
        issue = jira_client.update_issue(issue_key, **data)
        
        # 데이터베이스 연동 정보 업데이트
        jira_integration = JiraIntegration.query.filter_by(jira_issue_key=issue_key).first()
        if jira_integration:
            if 'summary' in data:
                jira_integration.summary = data['summary']
            if 'description' in data:
                jira_integration.description = data['description']
            if 'status' in data:
                jira_integration.status = data['status']
            if 'assignee' in data:
                jira_integration.assignee_account_id = data['assignee']
            if 'priority' in data:
                jira_integration.priority = data['priority']
            if 'labels' in data:
                jira_integration.labels = json.dumps(data['labels']) if data['labels'] else None
            
            jira_integration.updated_at = datetime.utcnow()
            jira_integration.last_sync_at = datetime.utcnow()
            
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': issue
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/issues/<issue_key>/comment', methods=['POST'])
@user_required
def add_comment(issue_key):
    """이슈에 댓글 추가"""
    try:
        data = request.get_json()
        comment = data.get('comment', '')
        
        if not comment:
            return jsonify({
                'success': False,
                'error': '댓글 내용이 필요합니다.'
            }), 400
        
        # 먼저 데이터베이스에서 이슈 정보 조회
        jira_integration = JiraIntegration.query.filter_by(jira_issue_key=issue_key).first()
        
        if not jira_integration:
            return jsonify({
                'success': False,
                'error': '이슈를 찾을 수 없습니다.',
                'error_type': 'ISSUE_NOT_FOUND'
            }), 404
        
        # 데이터베이스에 댓글 저장
        new_comment = JiraComment(
            jira_integration_id=jira_integration.id,
            body=comment,
            author_display_name='System User',
            author_account_id='system'
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        # Mock JIRA 서버에도 댓글 추가 시도 (동기화용)
        try:
            mock_result = jira_client.add_comment(issue_key, comment)
            # Mock 서버에서 받은 댓글 ID가 있으면 DB에 저장
            if 'id' in mock_result:
                new_comment.jira_comment_id = str(mock_result['id'])
                db.session.commit()
        except Exception as mock_error:
            print(f"Mock JIRA 서버에서 댓글 추가 실패: {mock_error}")
        
        return jsonify({
            'success': True,
            'data': new_comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/search', methods=['GET'])
@user_required
def search_issues():
    """이슈 검색"""
    try:
        jql = request.args.get('jql', '')
        start_at = int(request.args.get('startAt', 0))
        max_results = int(request.args.get('maxResults', 50))
        
        results = jira_client.search_issues(jql, start_at, max_results)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/integrations', methods=['GET'])
# @user_required  # 개발 단계에서 임시로 비활성화
def get_integrations():
    """JIRA 연동 목록 조회"""
    try:
        test_id = request.args.get('test_id')
        test_type = request.args.get('test_type')
        
        query = JiraIntegration.query
        
        if test_id and test_type:
            if test_type == 'testcase':
                query = query.filter_by(test_case_id=test_id)
            elif test_type == 'automation':
                query = query.filter_by(automation_test_id=test_id)
            elif test_type == 'performance':
                query = query.filter_by(performance_test_id=test_id)
        
        integrations = query.all()
        
        return jsonify({
            'success': True,
            'data': [integration.to_dict() for integration in integrations]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/stats', methods=['GET'])
# @user_required  # 개발 단계에서 임시로 비활성화
def get_jira_stats():
    """JIRA 통계 조회"""
    try:
        # 모든 이슈 조회
        all_integrations = JiraIntegration.query.all()
        
        # 통계 계산
        stats = {
            'total_issues': len(all_integrations),
            'issues_by_status': {},
            'issues_by_priority': {},
            'issues_by_type': {},
            'recent_issues': []
        }
        
        # 상태별, 우선순위별, 타입별 통계 계산
        for integration in all_integrations:
            # 상태별 통계
            status = integration.status or 'Unknown'
            stats['issues_by_status'][status] = stats['issues_by_status'].get(status, 0) + 1
            
            # 우선순위별 통계
            priority = integration.priority or 'Unknown'
            stats['issues_by_priority'][priority] = stats['issues_by_priority'].get(priority, 0) + 1
            
            # 타입별 통계
            issue_type = integration.issue_type or 'Unknown'
            stats['issues_by_type'][issue_type] = stats['issues_by_type'].get(issue_type, 0) + 1
        
        # 최근 이슈 (최대 5개, 생성일 기준 내림차순)
        recent_issues = sorted(all_integrations, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]
        stats['recent_issues'] = [issue.to_dict() for issue in recent_issues]
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/integrations/<int:integration_id>', methods=['DELETE'])
@user_required
def delete_integration(integration_id):
    """JIRA 연동 삭제"""
    try:
        integration = JiraIntegration.query.get(integration_id)
        if not integration:
            return jsonify({
                'success': False,
                'error': '연동 정보를 찾을 수 없습니다.'
            }), 404
        
        db.session.delete(integration)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '연동 정보가 삭제되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/sync', methods=['POST'])
@user_required
def sync_issues():
    """이슈 상태 동기화"""
    try:
        data = request.get_json()
        integration_id = data.get('integration_id')
        
        if integration_id:
            # 특정 연동 정보 동기화
            integration = JiraIntegration.query.get(integration_id)
            if not integration:
                return jsonify({
                    'success': False,
                    'error': '연동 정보를 찾을 수 없습니다.'
                }), 404
            
            # JIRA에서 최신 이슈 정보 조회
            issue = jira_client.get_issue(integration.jira_issue_key)
            
            # 상태 업데이트
            integration.status = issue['fields']['status']['name']
            integration.updated_at = datetime.utcnow()
            integration.last_sync_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': integration.to_dict()
            })
        else:
            # 모든 연동 정보 동기화
            integrations = JiraIntegration.query.all()
            synced_count = 0
            
            for integration in integrations:
                try:
                    issue = jira_client.get_issue(integration.jira_issue_key)
                    integration.status = issue['fields']['status']['name']
                    integration.last_sync_at = datetime.utcnow()
                    synced_count += 1
                except Exception as e:
                    print(f"동기화 실패: {integration.jira_issue_key} - {str(e)}")
                    continue
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'{synced_count}개의 이슈가 동기화되었습니다.'
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/auto-create', methods=['POST'])
# @user_required  # 개발 단계에서 임시로 비활성화
def auto_create_issue():
    """테스트 실패 시 자동 이슈 생성"""
    try:
        data = request.get_json()
        
        test_id = data.get('test_id')
        test_type = data.get('test_type')
        test_name = data.get('test_name')
        test_result = data.get('test_result')
        error_message = data.get('error_message')
        
        if not all([test_id, test_type, test_name, test_result]):
            return jsonify({
                'success': False,
                'error': '필수 필드가 누락되었습니다.'
            }), 400
        
        # 테스트 실패 시에만 이슈 생성
        if test_result not in ['Fail', 'Error']:
            return jsonify({
                'success': True,
                'message': '테스트가 성공했으므로 이슈를 생성하지 않습니다.',
                'data': None
            })
        
        # 자동 이슈 생성
        issue = jira_service.create_issue_from_test_result(
            test_id=test_id,
            test_type=test_type,
            test_name=test_name,
            test_result=test_result,
            error_message=error_message
        )
        
        if issue:
            # 데이터베이스에 연동 정보 저장
            jira_integration = JiraIntegration(
                test_case_id=test_id if test_type == 'testcase' else None,
                automation_test_id=test_id if test_type == 'automation' else None,
                performance_test_id=test_id if test_type == 'performance' else None,
                jira_issue_key=issue['key'],
                jira_issue_id=issue['id'],
                jira_project_key=issue['fields']['project']['key'],
                issue_type='Bug',
                status=issue['fields']['status']['name'],
                priority='High' if test_result == 'Error' else 'Medium',
                summary=issue['fields']['summary'],
                description=issue['fields']['description'],
                last_sync_at=datetime.utcnow()
            )
            
            db.session.add(jira_integration)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'issue': issue,
                    'integration_id': jira_integration.id
                }
            }), 201
        else:
            return jsonify({
                'success': True,
                'message': '이슈 생성 조건을 만족하지 않습니다.',
                'data': None
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_bp.route('/issues/<issue_key>/comments', methods=['GET'])
# @user_required  # 개발 단계에서 임시로 비활성화
def get_issue_comments(issue_key):
    """이슈 댓글 목록 조회"""
    try:
        # 먼저 데이터베이스에서 이슈 정보 조회
        jira_integration = JiraIntegration.query.filter_by(jira_issue_key=issue_key).first()
        
        if not jira_integration:
            return jsonify({
                'success': False,
                'error': '이슈를 찾을 수 없습니다.',
                'error_type': 'ISSUE_NOT_FOUND'
            }), 404
        
        # 데이터베이스에서 댓글 조회
        db_comments = JiraComment.query.filter_by(jira_integration_id=jira_integration.id).order_by(JiraComment.created_at.asc()).all()
        
        # Mock JIRA 서버에서 댓글 조회 시도 (동기화용)
        mock_comments = []
        try:
            mock_comments = jira_client.get_comments(issue_key)
        except Exception as mock_error:
            print(f"Mock JIRA 서버에서 댓글 조회 실패: {mock_error}")
        
        # DB 댓글을 JIRA 형식으로 변환
        comments = [comment.to_dict() for comment in db_comments]
        
        return jsonify({
            'success': True,
            'data': {
                'comments': comments,
                'issue_info': {
                    'key': jira_integration.jira_issue_key,
                    'summary': jira_integration.summary,
                    'status': jira_integration.status,
                    'priority': jira_integration.priority
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
