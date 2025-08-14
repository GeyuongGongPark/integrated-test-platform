from flask import Blueprint, request, jsonify
from models import db, DashboardSummary, TestResult, TestCase
from utils.cors import add_cors_headers
from utils.auth_decorators import guest_allowed
from datetime import datetime

# Blueprint 생성
dashboard_bp = Blueprint('dashboard', __name__)

# 새로운 대시보드 요약 API
@dashboard_bp.route('/dashboard-summaries', methods=['GET'])
@guest_allowed
def get_dashboard_summaries():
    summaries = DashboardSummary.query.all()
    data = [{
        'id': s.id,
        'environment': s.environment,
        'total_tests': s.total_tests,
        'passed_tests': s.passed_tests,
        'failed_tests': s.failed_tests,
        'skipped_tests': s.skipped_tests,
        'pass_rate': s.pass_rate,
        'last_updated': s.last_updated
    } for s in summaries]
    response = jsonify(data)
    return add_cors_headers(response), 200

@dashboard_bp.route('/dashboard-summaries', methods=['POST'])
def create_dashboard_summary():
    data = request.get_json()
    summary = DashboardSummary(
        environment=data.get('environment'),
        total_tests=data.get('total_tests', 0),
        passed_tests=data.get('passed_tests', 0),
        failed_tests=data.get('failed_tests', 0),
        skipped_tests=data.get('skipped_tests', 0),
        pass_rate=data.get('pass_rate', 0.0)
    )
    db.session.add(summary)
    db.session.commit()
    response = jsonify({'message': '대시보드 요약 생성 완료', 'id': summary.id})
    return add_cors_headers(response), 201

@dashboard_bp.route('/dashboard-summaries/<int:id>', methods=['PUT'])
def update_dashboard_summary(id):
    summary = DashboardSummary.query.get_or_404(id)
    data = request.get_json()
    summary.environment = data.get('environment', summary.environment)
    summary.total_tests = data.get('total_tests', summary.total_tests)
    summary.passed_tests = data.get('passed_tests', summary.passed_tests)
    summary.failed_tests = data.get('failed_tests', summary.failed_tests)
    summary.skipped_tests = data.get('skipped_tests', summary.skipped_tests)
    summary.pass_rate = data.get('pass_rate', summary.pass_rate)
    db.session.commit()
    response = jsonify({'message': '대시보드 요약 업데이트 완료'})
    return add_cors_headers(response), 200

@dashboard_bp.route('/dashboard-summaries/<int:id>', methods=['DELETE'])
def delete_dashboard_summary(id):
    summary = DashboardSummary.query.get_or_404(id)
    db.session.delete(summary)
    db.session.commit()
    response = jsonify({'message': '대시보드 요약 삭제 완료'})
    return add_cors_headers(response), 200

# 환경별 테스트 결과 요약 API
@dashboard_bp.route('/test-results/summary/<environment>', methods=['GET'])
@guest_allowed
def get_test_results_summary(environment):
    """특정 환경의 테스트 결과 요약"""
    try:
        # 해당 환경의 모든 테스트 결과 조회
        results = TestResult.query.filter_by(environment=environment).all()
        
        total = len(results)
        passed = len([r for r in results if r.result == 'Pass'])
        failed = len([r for r in results if r.result == 'Fail'])
        skipped = len([r for r in results if r.result == 'Skip'])
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        summary = {
            'environment': environment,
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': failed,
            'skipped_tests': skipped,
            'pass_rate': round(pass_rate, 2),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        response = jsonify(summary)
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@dashboard_bp.route('/testcases/summary/<environment>', methods=['GET'])
@guest_allowed
def get_testcases_summary(environment):
    """특정 환경의 테스트 케이스 상태 요약 (Pass, Fail, N/T, N/A, Block)"""
    try:
        # 해당 환경의 모든 테스트 케이스 조회
        testcases = TestCase.query.filter_by(environment=environment).all()
        
        total = len(testcases)
        passed = len([tc for tc in testcases if tc.result_status == 'Pass'])
        failed = len([tc for tc in testcases if tc.result_status == 'Fail'])
        nt = len([tc for tc in testcases if tc.result_status == 'N/T'])
        na = len([tc for tc in testcases if tc.result_status == 'N/A'])
        blocked = len([tc for tc in testcases if tc.result_status == 'Block'])
        
        # 통과율 계산 (Pass / Total)
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
            'last_updated': datetime.utcnow().isoformat()
        }
        
        response = jsonify(summary)
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@dashboard_bp.route('/testcases/summary/all', methods=['GET'])
def get_all_testcases_summary():
    """모든 환경의 테스트 케이스 상태 요약"""
    try:
        # 모든 환경의 테스트 케이스 조회
        environments = ['dev', 'alpha', 'production']
        summaries = []
        
        for env in environments:
            testcases = TestCase.query.filter_by(environment=env).all()
            
            total = len(testcases)
            passed = len([tc for tc in testcases if tc.result_status == 'Pass'])
            failed = len([tc for tc in testcases if tc.result_status == 'Fail'])
            nt = len([tc for tc in testcases if tc.result_status == 'N/T'])
            na = len([tc for tc in testcases if tc.result_status == 'N/A'])
            blocked = len([tc for tc in testcases if tc.result_status == 'Block'])
            
            # 통과율 계산 (Pass / Total)
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            summary = {
                'environment': env,
                'total_testcases': total,
                'passed': passed,
                'failed': failed,
                'nt': nt,
                'na': na,
                'blocked': blocked,
                'pass_rate': round(pass_rate, 2),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            summaries.append(summary)
        
        response = jsonify(summaries)
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500 