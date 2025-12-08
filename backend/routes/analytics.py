"""
고급 분석 및 트렌드 API
트렌드 분석, Flaky 테스트 감지, 회귀 테스트 감지 등
"""
from flask import Blueprint, request, jsonify
from models import db, TestCase, TestResult, TestExecution
from utils.cors import add_cors_headers
from utils.auth_decorators import guest_allowed, user_required
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, case
from sqlalchemy.sql import label
import json

logger = get_logger(__name__)

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/trends', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_test_trends():
    """시간대별 테스트 트렌드 분석"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 파라미터
        days = request.args.get('days', 30, type=int)  # 기본 30일
        environment = request.args.get('environment')  # 선택적 필터
        test_case_id = request.args.get('test_case_id', type=int)  # 선택적 필터
        
        # 시작 날짜 계산
        start_date = get_kst_now() - timedelta(days=days)
        
        # 기본 쿼리
        query = db.session.query(
            func.date(TestResult.executed_at).label('date'),
            TestResult.result,
            func.count(TestResult.id).label('count')
        ).filter(
            TestResult.executed_at >= start_date
        )
        
        # 필터 적용
        if environment:
            query = query.filter(TestResult.environment == environment)
        if test_case_id:
            query = query.filter(TestResult.test_case_id == test_case_id)
        
        # 그룹화 및 정렬
        results = query.group_by(
            func.date(TestResult.executed_at),
            TestResult.result
        ).order_by(
            func.date(TestResult.executed_at).desc()
        ).all()
        
        # 날짜별로 데이터 구성
        trends_by_date = {}
        for row in results:
            date_str = row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date)
            if date_str not in trends_by_date:
                trends_by_date[date_str] = {
                    'date': date_str,
                    'passed': 0,
                    'failed': 0,
                    'total': 0
                }
            trends_by_date[date_str][row.result.lower() if row.result else 'unknown'] = row.count
            trends_by_date[date_str]['total'] += row.count
        
        # 리스트로 변환 및 정렬
        trends = sorted(trends_by_date.values(), key=lambda x: x['date'])
        
        # 통계 계산
        total_passed = sum(t.get('passed', 0) for t in trends)
        total_failed = sum(t.get('failed', 0) for t in trends)
        total_tests = sum(t['total'] for t in trends)
        
        # 실패율 추이 계산
        for trend in trends:
            trend['failure_rate'] = round((trend.get('failed', 0) / trend['total'] * 100) if trend['total'] > 0 else 0, 2)
            trend['pass_rate'] = round((trend.get('passed', 0) / trend['total'] * 100) if trend['total'] > 0 else 0, 2)
        
        response_data = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': get_kst_now().isoformat(),
                'days': days
            },
            'trends': trends,
            'summary': {
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'overall_pass_rate': round((total_passed / total_tests * 100) if total_tests > 0 else 0, 2),
                'overall_failure_rate': round((total_failed / total_tests * 100) if total_tests > 0 else 0, 2)
            },
            'filters': {
                'environment': environment,
                'test_case_id': test_case_id
            }
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"트렌드 분석 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@analytics_bp.route('/analytics/flaky-tests', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_flaky_tests():
    """불안정한(Flaky) 테스트 감지"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 파라미터
        min_executions = request.args.get('min_executions', 5, type=int)  # 최소 실행 횟수
        days = request.args.get('days', 30, type=int)  # 분석 기간
        flakiness_threshold = request.args.get('flakiness_threshold', 0.1, type=float)  # 불안정성 임계값 (10%)
        
        start_date = get_kst_now() - timedelta(days=days)
        
        # 각 테스트 케이스별 실행 결과 통계
        test_stats = db.session.query(
            TestResult.test_case_id,
            TestCase.name.label('test_case_name'),
            func.count(TestResult.id).label('total_executions'),
            func.sum(case([(TestResult.result == 'Pass', 1)], else_=0)).label('passed'),
            func.sum(case([(TestResult.result == 'Fail', 1)], else_=0)).label('failed'),
            func.min(TestResult.executed_at).label('first_execution'),
            func.max(TestResult.executed_at).label('last_execution')
        ).join(
            TestCase, TestResult.test_case_id == TestCase.id
        ).filter(
            TestResult.executed_at >= start_date
        ).group_by(
            TestResult.test_case_id,
            TestCase.name
        ).having(
            func.count(TestResult.id) >= min_executions
        ).all()
        
        flaky_tests = []
        for stat in test_stats:
            total = stat.total_executions
            passed = stat.passed or 0
            failed = stat.failed or 0
            
            # 불안정성 점수 계산: Pass와 Fail이 모두 있는 경우
            if passed > 0 and failed > 0:
                # 불안정성 = min(pass_rate, failure_rate) - 둘 다 있으면 불안정
                pass_rate = passed / total
                failure_rate = failed / total
                flakiness_score = min(pass_rate, failure_rate)
                
                # 불안정성 점수가 임계값을 넘으면 Flaky로 판단
                if flakiness_score >= flakiness_threshold:
                    # 최근 실행 결과 패턴 분석
                    recent_results = db.session.query(
                        TestResult.result,
                        TestResult.executed_at
                    ).filter(
                        TestResult.test_case_id == stat.test_case_id,
                        TestResult.executed_at >= start_date
                    ).order_by(
                        TestResult.executed_at.desc()
                    ).limit(10).all()
                    
                    # 결과 패턴 분석 (Pass/Fail이 번갈아 나타나는지)
                    pattern_changes = 0
                    prev_result = None
                    for res in reversed(recent_results):
                        if prev_result and res.result != prev_result:
                            pattern_changes += 1
                        prev_result = res.result
                    
                    flaky_tests.append({
                        'test_case_id': stat.test_case_id,
                        'test_case_name': stat.test_case_name,
                        'total_executions': total,
                        'passed': passed,
                        'failed': failed,
                        'pass_rate': round(pass_rate * 100, 2),
                        'failure_rate': round(failure_rate * 100, 2),
                        'flakiness_score': round(flakiness_score * 100, 2),
                        'pattern_changes': pattern_changes,
                        'first_execution': stat.first_execution.isoformat() if stat.first_execution else None,
                        'last_execution': stat.last_execution.isoformat() if stat.last_execution else None,
                        'recent_results': [r.result for r in recent_results]
                    })
        
        # 불안정성 점수로 정렬
        flaky_tests.sort(key=lambda x: x['flakiness_score'], reverse=True)
        
        response_data = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': get_kst_now().isoformat(),
                'days': days
            },
            'criteria': {
                'min_executions': min_executions,
                'flakiness_threshold': flakiness_threshold
            },
            'flaky_tests': flaky_tests,
            'total_flaky_tests': len(flaky_tests)
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"Flaky 테스트 감지 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@analytics_bp.route('/analytics/regression-detection', methods=['GET', 'OPTIONS'])
@guest_allowed
def detect_regressions():
    """회귀 테스트 자동 감지 (최근에 실패하기 시작한 테스트)"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 파라미터
        days = request.args.get('days', 7, type=int)  # 최근 N일
        min_previous_passes = request.args.get('min_previous_passes', 3, type=int)  # 이전 최소 성공 횟수
        
        start_date = get_kst_now() - timedelta(days=days)
        previous_start_date = get_kst_now() - timedelta(days=days * 2)
        
        # 최근 기간에 실패한 테스트
        recent_failures = db.session.query(
            TestResult.test_case_id,
            func.count(TestResult.id).label('failure_count')
        ).filter(
            TestResult.executed_at >= start_date,
            TestResult.result == 'Fail'
        ).group_by(
            TestResult.test_case_id
        ).subquery()
        
        # 이전 기간에 성공한 테스트
        previous_passes = db.session.query(
            TestResult.test_case_id,
            func.count(TestResult.id).label('pass_count')
        ).filter(
            and_(
                TestResult.executed_at >= previous_start_date,
                TestResult.executed_at < start_date,
                TestResult.result == 'Pass'
            )
        ).group_by(
            TestResult.test_case_id
        ).having(
            func.count(TestResult.id) >= min_previous_passes
        ).subquery()
        
        # 회귀 테스트 찾기: 이전에 성공했지만 최근에 실패한 테스트
        regressions = db.session.query(
            TestCase.id,
            TestCase.name,
            TestCase.environment,
            recent_failures.c.failure_count,
            previous_passes.c.pass_count
        ).join(
            recent_failures, TestCase.id == recent_failures.c.test_case_id
        ).join(
            previous_passes, TestCase.id == previous_passes.c.test_case_id
        ).all()
        
        regression_list = []
        for reg in regressions:
            # 최근 실패 상세 정보
            recent_failure_details = db.session.query(
                TestResult.executed_at,
                TestResult.error_message,
                TestResult.notes
            ).filter(
                TestResult.test_case_id == reg.id,
                TestResult.executed_at >= start_date,
                TestResult.result == 'Fail'
            ).order_by(
                TestResult.executed_at.desc()
            ).limit(5).all()
            
            regression_list.append({
                'test_case_id': reg.id,
                'test_case_name': reg.name,
                'environment': reg.environment,
                'recent_failures': reg.failure_count,
                'previous_passes': reg.pass_count,
                'first_failure_date': recent_failure_details[0].executed_at.isoformat() if recent_failure_details else None,
                'failure_details': [{
                    'executed_at': fd.executed_at.isoformat() if fd.executed_at else None,
                    'error_message': fd.error_message,
                    'notes': fd.notes[:200] if fd.notes else None
                } for fd in recent_failure_details]
            })
        
        response_data = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': get_kst_now().isoformat(),
                'days': days
            },
            'criteria': {
                'min_previous_passes': min_previous_passes
            },
            'regressions': regression_list,
            'total_regressions': len(regression_list)
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"회귀 테스트 감지 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@analytics_bp.route('/analytics/execution-time', methods=['GET', 'OPTIONS'])
@guest_allowed
def analyze_execution_time():
    """실행 시간 분석 및 최적화 제안"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 파라미터
        days = request.args.get('days', 30, type=int)
        test_case_id = request.args.get('test_case_id', type=int)
        environment = request.args.get('environment')
        
        start_date = get_kst_now() - timedelta(days=days)
        
        query = db.session.query(
            TestResult.test_case_id,
            TestCase.name.label('test_case_name'),
            func.avg(TestResult.execution_time).label('avg_time'),
            func.min(TestResult.execution_time).label('min_time'),
            func.max(TestResult.execution_time).label('max_time'),
            func.stddev(TestResult.execution_time).label('stddev_time'),
            func.count(TestResult.id).label('execution_count')
        ).join(
            TestCase, TestResult.test_case_id == TestCase.id
        ).filter(
            TestResult.executed_at >= start_date,
            TestResult.execution_time.isnot(None)
        )
        
        if test_case_id:
            query = query.filter(TestResult.test_case_id == test_case_id)
        if environment:
            query = query.filter(TestResult.environment == environment)
        
        results = query.group_by(
            TestResult.test_case_id,
            TestCase.name
        ).having(
            func.count(TestResult.id) >= 3  # 최소 3회 실행
        ).all()
        
        analysis = []
        for result in results:
            avg_time = float(result.avg_time) if result.avg_time else 0
            min_time = float(result.min_time) if result.min_time else 0
            max_time = float(result.max_time) if result.max_time else 0
            stddev_time = float(result.stddev_time) if result.stddev_time else 0
            execution_count = result.execution_count
            
            # 변동성 계산 (표준편차 / 평균)
            variability = (stddev_time / avg_time * 100) if avg_time > 0 else 0
            
            # 최적화 제안
            suggestions = []
            if variability > 50:
                suggestions.append('실행 시간 변동성이 높습니다. 환경 설정이나 테스트 데이터를 확인하세요.')
            if max_time > avg_time * 2:
                suggestions.append('최대 실행 시간이 평균의 2배를 넘습니다. 타임아웃이나 리소스 문제를 확인하세요.')
            if avg_time > 300:  # 5분 이상
                suggestions.append('평균 실행 시간이 5분을 넘습니다. 테스트 최적화를 고려하세요.')
            
            analysis.append({
                'test_case_id': result.test_case_id,
                'test_case_name': result.test_case_name,
                'execution_count': execution_count,
                'avg_time': round(avg_time, 2),
                'min_time': round(min_time, 2),
                'max_time': round(max_time, 2),
                'stddev_time': round(stddev_time, 2),
                'variability_percent': round(variability, 2),
                'suggestions': suggestions
            })
        
        # 실행 시간으로 정렬
        analysis.sort(key=lambda x: x['avg_time'], reverse=True)
        
        response_data = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': get_kst_now().isoformat(),
                'days': days
            },
            'analysis': analysis,
            'total_tests': len(analysis),
            'filters': {
                'test_case_id': test_case_id,
                'environment': environment
            }
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"실행 시간 분석 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@analytics_bp.route('/analytics/coverage', methods=['GET', 'OPTIONS'])
@guest_allowed
def analyze_test_coverage():
    """테스트 커버리지 분석"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 파라미터
        environment = request.args.get('environment')
        folder_id = request.args.get('folder_id', type=int)
        
        # 기본 쿼리
        query = db.session.query(
            TestCase.id,
            TestCase.name,
            TestCase.environment,
            TestCase.folder_id,
            TestCase.main_category,
            TestCase.result_status,
            func.count(TestResult.id).label('execution_count'),
            func.max(TestResult.executed_at).label('last_execution')
        ).outerjoin(
            TestResult, TestCase.id == TestResult.test_case_id
        )
        
        # 필터 적용
        if environment:
            query = query.filter(TestCase.environment == environment)
        if folder_id:
            query = query.filter(TestCase.folder_id == folder_id)
        
        results = query.group_by(
            TestCase.id,
            TestCase.name,
            TestCase.environment,
            TestCase.folder_id,
            TestCase.main_category,
            TestCase.result_status
        ).all()
        
        # 커버리지 분석
        total_tests = len(results)
        executed_tests = sum(1 for r in results if r.execution_count > 0)
        never_executed = sum(1 for r in results if r.execution_count == 0)
        
        # 카테고리별 커버리지
        category_coverage = {}
        for result in results:
            category = result.main_category or 'Uncategorized'
            if category not in category_coverage:
                category_coverage[category] = {
                    'total': 0,
                    'executed': 0,
                    'never_executed': 0
                }
            category_coverage[category]['total'] += 1
            if result.execution_count > 0:
                category_coverage[category]['executed'] += 1
            else:
                category_coverage[category]['never_executed'] += 1
        
        # 커버리지 비율 계산
        for category, stats in category_coverage.items():
            stats['coverage_rate'] = round((stats['executed'] / stats['total'] * 100) if stats['total'] > 0 else 0, 2)
        
        # 오래 실행되지 않은 테스트 (30일 이상)
        thirty_days_ago = get_kst_now() - timedelta(days=30)
        stale_tests = [
            {
                'test_case_id': r.id,
                'test_case_name': r.name,
                'last_execution': r.last_execution.isoformat() if r.last_execution else None,
                'days_since_execution': (get_kst_now() - r.last_execution).days if r.last_execution else None
            }
            for r in results
            if r.last_execution is None or r.last_execution < thirty_days_ago
        ]
        
        response_data = {
            'overall': {
                'total_tests': total_tests,
                'executed_tests': executed_tests,
                'never_executed': never_executed,
                'coverage_rate': round((executed_tests / total_tests * 100) if total_tests > 0 else 0, 2)
            },
            'category_coverage': category_coverage,
            'stale_tests': stale_tests[:50],  # 최대 50개
            'filters': {
                'environment': environment,
                'folder_id': folder_id
            }
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"커버리지 분석 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@analytics_bp.route('/analytics/failure-patterns', methods=['GET', 'OPTIONS'])
@guest_allowed
def analyze_failure_patterns():
    """실패 패턴 분석"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 파라미터
        days = request.args.get('days', 30, type=int)
        environment = request.args.get('environment')
        
        start_date = get_kst_now() - timedelta(days=days)
        
        # 실패한 테스트 결과
        failures = db.session.query(
            TestResult.test_case_id,
            TestCase.name,
            TestCase.environment,
            TestCase.main_category,
            TestResult.error_message,
            TestResult.executed_at
        ).join(
            TestCase, TestResult.test_case_id == TestCase.id
        ).filter(
            TestResult.executed_at >= start_date,
            TestResult.result == 'Fail'
        )
        
        if environment:
            failures = failures.filter(TestCase.environment == environment)
        
        failures = failures.all()
        
        # 환경별 실패 통계
        env_failures = {}
        # 카테고리별 실패 통계
        category_failures = {}
        # 시간대별 실패 통계
        hourly_failures = {}
        # 에러 메시지 패턴 분석
        error_patterns = {}
        
        for failure in failures:
            # 환경별
            env = failure.environment or 'Unknown'
            env_failures[env] = env_failures.get(env, 0) + 1
            
            # 카테고리별
            category = failure.main_category or 'Uncategorized'
            category_failures[category] = category_failures.get(category, 0) + 1
            
            # 시간대별
            if failure.executed_at:
                hour = failure.executed_at.hour
                hourly_failures[hour] = hourly_failures.get(hour, 0) + 1
            
            # 에러 메시지 패턴 (간단한 키워드 추출)
            if failure.error_message:
                error_msg = failure.error_message.lower()
                # 일반적인 에러 키워드
                keywords = ['timeout', 'connection', 'not found', 'permission', 'invalid', 'error']
                for keyword in keywords:
                    if keyword in error_msg:
                        error_patterns[keyword] = error_patterns.get(keyword, 0) + 1
                        break
        
        response_data = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': get_kst_now().isoformat(),
                'days': days
            },
            'total_failures': len(failures),
            'environment_failures': env_failures,
            'category_failures': category_failures,
            'hourly_failures': hourly_failures,
            'error_patterns': error_patterns,
            'filters': {
                'environment': environment
            }
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"실패 패턴 분석 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@analytics_bp.route('/analytics/test-health', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_test_health():
    """테스트 건강도 종합 분석"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        # 파라미터
        days = request.args.get('days', 30, type=int)
        environment = request.args.get('environment')
        
        start_date = get_kst_now() - timedelta(days=days)
        
        # 전체 통계
        total_stats = db.session.query(
            func.count(TestCase.id).label('total_tests'),
            func.count(TestResult.id).label('total_executions'),
            func.sum(case([(TestResult.result == 'Pass', 1)], else_=0)).label('passed'),
            func.sum(case([(TestResult.result == 'Fail', 1)], else_=0)).label('failed')
        ).outerjoin(
            TestResult, and_(
                TestCase.id == TestResult.test_case_id,
                TestResult.executed_at >= start_date
            )
        )
        
        if environment:
            total_stats = total_stats.filter(TestCase.environment == environment)
        
        stats = total_stats.first()
        
        total_tests = stats.total_tests or 0
        total_executions = stats.total_executions or 0
        passed = stats.passed or 0
        failed = stats.failed or 0
        
        # 건강도 점수 계산 (0-100)
        health_score = 0
        
        # 실행률 (30%)
        execution_rate = (total_executions / (total_tests * days) * 100) if total_tests > 0 and days > 0 else 0
        execution_rate = min(execution_rate, 100)  # 최대 100%
        health_score += execution_rate * 0.3
        
        # 통과율 (50%)
        pass_rate = (passed / total_executions * 100) if total_executions > 0 else 0
        health_score += pass_rate * 0.5
        
        # 안정성 (20%) - Flaky 테스트가 적을수록 높음
        # 간단한 안정성 계산: 최근 10회 실행 중 일관성
        stability_score = 100  # 기본값
        if total_executions > 0:
            # Flaky 테스트 비율 계산 (간단 버전)
            flaky_count = 0
            test_cases_with_results = db.session.query(
                TestResult.test_case_id,
                func.count(TestResult.id).label('count'),
                func.sum(case([(TestResult.result == 'Pass', 1)], else_=0)).label('passed'),
                func.sum(case([(TestResult.result == 'Fail', 1)], else_=0)).label('failed')
            ).filter(
                TestResult.executed_at >= start_date
            ).group_by(
                TestResult.test_case_id
            ).having(
                func.count(TestResult.id) >= 5
            ).all()
            
            for tc in test_cases_with_results:
                if tc.passed > 0 and tc.failed > 0:
                    flaky_count += 1
            
            if len(test_cases_with_results) > 0:
                flaky_rate = (flaky_count / len(test_cases_with_results)) * 100
                stability_score = 100 - flaky_rate
        
        health_score += stability_score * 0.2
        health_score = round(min(health_score, 100), 2)
        
        # 건강도 등급
        if health_score >= 80:
            health_grade = 'Excellent'
        elif health_score >= 60:
            health_grade = 'Good'
        elif health_score >= 40:
            health_grade = 'Fair'
        else:
            health_grade = 'Poor'
        
        response_data = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': get_kst_now().isoformat(),
                'days': days
            },
            'health_score': health_score,
            'health_grade': health_grade,
            'metrics': {
                'total_tests': total_tests,
                'total_executions': total_executions,
                'passed': passed,
                'failed': failed,
                'pass_rate': round(pass_rate, 2),
                'execution_rate': round(execution_rate, 2),
                'stability_score': round(stability_score, 2)
            },
            'filters': {
                'environment': environment
            }
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"테스트 건강도 분석 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

