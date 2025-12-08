"""
이슈 관리 API (DB 기반)
Mock JIRA 서버 대신 데이터베이스에 직접 저장
"""

from flask import Blueprint, request, jsonify
from models import db, JiraIssue, JiraComment, TestCase
from datetime import datetime
import json
import uuid

jira_issues_bp = Blueprint('jira_issues', __name__, url_prefix='/api/jira')

@jira_issues_bp.route('/stats', methods=['GET'])
def get_jira_stats():
    """JIRA 통계 정보 조회"""
    try:
        # 전체 이슈 수
        total_issues = JiraIssue.query.count()
        
        # 상태별 이슈 수
        issues_by_status = {}
        status_counts = db.session.query(
            JiraIssue.status, 
            db.func.count(JiraIssue.id)
        ).group_by(JiraIssue.status).all()
        
        for status, count in status_counts:
            issues_by_status[status] = count
        
        # 우선순위별 이슈 수
        issues_by_priority = {}
        priority_counts = db.session.query(
            JiraIssue.priority, 
            db.func.count(JiraIssue.id)
        ).group_by(JiraIssue.priority).all()
        
        for priority, count in priority_counts:
            issues_by_priority[priority] = count
        
        # 타입별 이슈 수
        issues_by_type = {}
        type_counts = db.session.query(
            JiraIssue.issue_type, 
            db.func.count(JiraIssue.id)
        ).group_by(JiraIssue.issue_type).all()
        
        for issue_type, count in type_counts:
            issues_by_type[issue_type] = count
        
        # 최근 이슈 (최근 5개)
        recent_issues = JiraIssue.query.order_by(
            JiraIssue.created_at.desc()
        ).limit(5).all()
        
        recent_issues_data = []
        for issue in recent_issues:
            recent_issues_data.append({
                'issue_key': issue.issue_key,
                'summary': issue.summary,
                'status': issue.status,
                'priority': issue.priority,
                'created_at': issue.created_at.isoformat() if issue.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total_issues': total_issues,
                'issues_by_status': issues_by_status,
                'issues_by_priority': issues_by_priority,
                'issues_by_type': issues_by_type,
                'recent_issues': recent_issues_data
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'통계 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@jira_issues_bp.route('/issues', methods=['GET'])
def get_issues():
    """이슈 목록 조회 (페이지네이션 지원)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 검색 및 필터링
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        priority_filter = request.args.get('priority', '')
        
        query = JiraIssue.query
        
        # 검색 조건
        if search:
            query = query.filter(
                JiraIssue.summary.contains(search) |
                JiraIssue.issue_key.contains(search) |
                JiraIssue.description.contains(search)
            )
        
        if status_filter:
            query = query.filter(JiraIssue.status == status_filter)
            
        if priority_filter:
            query = query.filter(JiraIssue.priority == priority_filter)
        
        # 페이지네이션
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        issues = []
        for issue in pagination.items:
            issues.append(issue.to_dict())
        
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

@jira_issues_bp.route('/issues/testcase/<int:test_case_id>', methods=['GET'])
def get_issues_by_testcase(test_case_id):
    """특정 테스트 케이스와 연결된 이슈 목록 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 검색 및 필터링
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        priority_filter = request.args.get('priority', '')
        
        # 테스트 케이스와 연결된 이슈만 조회
        query = JiraIssue.query.filter(JiraIssue.test_case_id == test_case_id)
        
        # 검색 조건
        if search:
            query = query.filter(
                JiraIssue.summary.contains(search) |
                JiraIssue.issue_key.contains(search) |
                JiraIssue.description.contains(search)
            )
        
        if status_filter:
            query = query.filter(JiraIssue.status == status_filter)
            
        if priority_filter:
            query = query.filter(JiraIssue.priority == priority_filter)
        
        # 페이지네이션
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        issues = []
        for issue in pagination.items:
            issues.append(issue.to_dict())
        
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

@jira_issues_bp.route('/issues', methods=['POST'])
def create_issue():
    """새 이슈 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['summary', 'issue_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field}은 필수입니다.'
                }), 400
        
        # 이슈 키 생성 (TEST-1, TEST-2, ...)
        last_issue = JiraIssue.query.filter_by(project_key='TEST').order_by(JiraIssue.id.desc()).first()
        if last_issue:
            last_number = int(last_issue.issue_key.split('-')[1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        issue_key = f"TEST-{new_number}"
        
        # 새 이슈 생성
        issue = JiraIssue(
            issue_key=issue_key,
            project_key=data.get('project_key', 'TEST'),
            issue_type=data.get('issue_type'),
            status=data.get('status', 'To Do'),
            priority=data.get('priority', 'Medium'),
            summary=data.get('summary'),
            description=data.get('description', ''),
            assignee_email=data.get('assignee_email'),
            labels=json.dumps(data.get('labels', [])) if data.get('labels') else None,
            reporter_email=data.get('reporter_email', 'admin@example.com'),
            test_case_id=data.get('test_case_id'),
            automation_test_id=data.get('automation_test_id'),
            performance_test_id=data.get('performance_test_id')
        )
        
        db.session.add(issue)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '이슈가 성공적으로 생성되었습니다.',
            'data': issue.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_issues_bp.route('/issues/<issue_key>', methods=['GET'])
def get_issue(issue_key):
    """특정 이슈 조회"""
    try:
        issue = JiraIssue.query.filter_by(issue_key=issue_key).first()
        
        if not issue:
            return jsonify({
                'success': False,
                'error': '이슈를 찾을 수 없습니다.'
            }), 404
        
        return jsonify({
            'success': True,
            'data': issue.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_issues_bp.route('/issues/<issue_key>', methods=['PUT'])
def update_issue(issue_key):
    """이슈 업데이트"""
    try:
        issue = JiraIssue.query.filter_by(issue_key=issue_key).first()
        
        if not issue:
            return jsonify({
                'success': False,
                'error': '이슈를 찾을 수 없습니다.'
            }), 404
        
        data = request.get_json()
        
        # 업데이트할 필드들
        if 'summary' in data:
            issue.summary = data['summary']
        if 'description' in data:
            issue.description = data['description']
        if 'status' in data:
            issue.status = data['status']
        if 'priority' in data:
            issue.priority = data['priority']
        if 'issue_type' in data:
            issue.issue_type = data['issue_type']
        if 'assignee_email' in data:
            issue.assignee_email = data['assignee_email']
        if 'labels' in data:
            issue.labels = json.dumps(data['labels']) if data['labels'] else None
        if 'test_case_id' in data:
            issue.test_case_id = data['test_case_id']
        if 'automation_test_id' in data:
            issue.automation_test_id = data['automation_test_id']
        if 'performance_test_id' in data:
            issue.performance_test_id = data['performance_test_id']
        
        issue.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '이슈가 성공적으로 업데이트되었습니다.',
            'data': issue.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_issues_bp.route('/issues/<issue_key>', methods=['DELETE'])
def delete_issue(issue_key):
    """이슈 삭제"""
    try:
        issue = JiraIssue.query.filter_by(issue_key=issue_key).first()
        
        if not issue:
            return jsonify({
                'success': False,
                'error': '이슈를 찾을 수 없습니다.'
            }), 404
        
        # 관련 댓글도 삭제
        JiraComment.query.filter_by(jira_issue_id=issue.id).delete()
        
        db.session.delete(issue)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '이슈가 성공적으로 삭제되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_issues_bp.route('/issues/<issue_key>/comments', methods=['GET'])
def get_comments(issue_key):
    """이슈 댓글 조회"""
    try:
        issue = JiraIssue.query.filter_by(issue_key=issue_key).first()
        
        if not issue:
            return jsonify({
                'success': False,
                'error': '이슈를 찾을 수 없습니다.'
            }), 404
        
        comments = JiraComment.query.filter_by(jira_issue_id=issue.id).order_by(JiraComment.created_at.asc()).all()
        
        return jsonify({
            'success': True,
            'data': [comment.to_dict() for comment in comments]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_issues_bp.route('/issues/<issue_key>/comments', methods=['POST'])
def add_comment(issue_key):
    """이슈에 댓글 추가"""
    try:
        issue = JiraIssue.query.filter_by(issue_key=issue_key).first()
        
        if not issue:
            return jsonify({
                'success': False,
                'error': '이슈를 찾을 수 없습니다.'
            }), 404
        
        data = request.get_json()
        
        if not data.get('body'):
            return jsonify({
                'success': False,
                'error': '댓글 내용은 필수입니다.'
            }), 400
        
        comment = JiraComment(
            jira_issue_id=issue.id,
            body=data['body'],
            author_email=data.get('author_email', 'admin@example.com')
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '댓글이 성공적으로 추가되었습니다.',
            'data': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_issues_bp.route('/stats', methods=['GET'])
def get_stats():
    """JIRA 통계 조회"""
    try:
        total_issues = JiraIssue.query.count()
        
        # 상태별 통계
        status_stats = db.session.query(
            JiraIssue.status, 
            db.func.count(JiraIssue.id)
        ).group_by(JiraIssue.status).all()
        
        # 우선순위별 통계
        priority_stats = db.session.query(
            JiraIssue.priority, 
            db.func.count(JiraIssue.id)
        ).group_by(JiraIssue.priority).all()
        
        # 타입별 통계
        type_stats = db.session.query(
            JiraIssue.issue_type, 
            db.func.count(JiraIssue.id)
        ).group_by(JiraIssue.issue_type).all()
        
        return jsonify({
            'success': True,
            'data': {
                'totalIssues': total_issues,
                'issuesByStatus': dict(status_stats),
                'issuesByPriority': dict(priority_stats),
                'issuesByType': dict(type_stats)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@jira_issues_bp.route('/stats/environment', methods=['GET'])
def get_jira_stats_by_environment():
    """환경별 JIRA 통계 조회"""
    try:
        from sqlalchemy import func
        
        # TestCase를 통해 환경별 이슈 통계 계산
        environment_stats = {}
        
        # 각 환경별로 이슈 수 집계
        # TestCase의 environment를 기준으로 연결된 JiraIssue를 조회
        environments = ['dev', 'alpha', 'staging', 'production', 'prod']
        
        for env in environments:
            # 해당 환경의 테스트 케이스에 연결된 이슈 수
            issue_count = db.session.query(func.count(JiraIssue.id)).join(
                TestCase, JiraIssue.test_case_id == TestCase.id
            ).filter(TestCase.environment == env).scalar() or 0
            
            # 상태별 통계
            status_counts = db.session.query(
                JiraIssue.status,
                func.count(JiraIssue.id)
            ).join(
                TestCase, JiraIssue.test_case_id == TestCase.id
            ).filter(TestCase.environment == env).group_by(JiraIssue.status).all()
            
            environment_stats[env] = {
                'totalIssues': issue_count,
                'issuesByStatus': dict(status_counts) if status_counts else {}
            }
        
        return jsonify({
            'success': True,
            'data': environment_stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

