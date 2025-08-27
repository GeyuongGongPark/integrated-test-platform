from flask import Blueprint, request, jsonify
from models import db, TestCase
from utils.cors import add_cors_headers
from datetime import datetime
from sqlalchemy import func, text
from utils.timezone_utils import get_kst_now

# Blueprint 생성
dashboard_extended_bp = Blueprint('dashboard_extended', __name__)

# 대시보드 요약 목록 조회 (프론트엔드에서 사용)
@dashboard_extended_bp.route('/dashboard-summaries', methods=['GET', 'OPTIONS'])
def get_dashboard_summaries():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'preflight_ok'}), 200
    
    try:
        # DashboardSummary 테이블이 있으면 사용, 없으면 실시간 계산
        try:
            from models import DashboardSummary
            summaries = DashboardSummary.query.all()
            data = [{
                'id': s.id,
                'environment': s.environment,
                'total_tests': s.total_tests,
                'passed_tests': s.passed_tests,
                'failed_tests': s.failed_tests,
                'skipped_tests': s.skipped_tests,
                'pass_rate': s.pass_rate,
                'last_updated': s.last_updated.isoformat() if s.last_updated else None
            } for s in summaries]
        except:
            # DashboardSummary 테이블이 없으면 실시간 계산
            data = []
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# 테스트 케이스 전체 요약 (프론트엔드에서 사용) - 실제 DB 값 사용
@dashboard_extended_bp.route('/testcases/summary/all', methods=['GET', 'OPTIONS'])
def get_testcases_summary_all():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'preflight_ok'}), 200
    
    try:
        # 실제 DB에 저장된 값으로 환경별/테스트 결과별 카운트 계산
        query = text("""
            SELECT 
                environment, 
                result_status, 
                COUNT(*) as count 
            FROM TestCases
            GROUP BY environment, result_status
            ORDER BY environment, result_status
        """)
        
        result = db.session.execute(query)
        stats = result.fetchall()
        
        # 환경별로 데이터 그룹화
        env_stats = {}
        for row in stats:
            env = row.environment
            if env not in env_stats:
                env_stats[env] = {}
            env_stats[env][row.result_status] = row.count
        
        # 요약 데이터 생성
        summaries = []
        for environment, status_counts in env_stats.items():
            total = sum(status_counts.values())
            passed = status_counts.get('Pass', 0)
            failed = status_counts.get('Fail', 0)
            nt = status_counts.get('N/T', 0)
            na = status_counts.get('N/A', 0)
            blocked = status_counts.get('Block', 0)
            
            # 통과율 계산
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            summary = {
                'environment': environment,
                'total_testcases': total,
                'passed': passed,
                'failed': failed,
                'nt': nt,
                'na': na,
                'blocked': blocked,
                'pass_rate': round(pass_rate, 2),
                'last_updated': get_kst_now().isoformat()
            }
            summaries.append(summary)
        
        response = jsonify(summaries)
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500
