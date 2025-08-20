#!/usr/bin/env python3
"""
테스트 케이스 데이터를 기반으로 대시보드 요약 데이터를 동기화하는 스크립트
"""

from app import app, db
from models import TestCase, DashboardSummary
from sqlalchemy import text
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_dashboard_summary():
    """테스트 케이스 데이터를 기반으로 대시보드 요약 데이터 동기화"""
    
    with app.app_context():
        try:
            # 1. 현재 테스트 케이스 상태별 통계 조회
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
            
            logger.info("📊 테스트 케이스 통계 데이터:")
            logger.info("=" * 60)
            
            # 환경별로 데이터 그룹화
            env_stats = {}
            for row in stats:
                env = row.environment
                if env not in env_stats:
                    env_stats[env] = {}
                env_stats[env][row.result_status] = row.count
            
            # 2. 각 환경별로 대시보드 요약 데이터 생성/업데이트
            for environment, status_counts in env_stats.items():
                logger.info(f"🌍 환경: {environment}")
                
                # 통계 계산
                total_tests = sum(status_counts.values())
                passed_tests = status_counts.get('Pass', 0)
                failed_tests = status_counts.get('Fail', 0)
                skipped_tests = status_counts.get('N/T', 0) + status_counts.get('N/A', 0)
                blocked_tests = status_counts.get('Block', 0)
                
                # 통과율 계산
                pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
                
                logger.info(f"  총 테스트: {total_tests}")
                logger.info(f"  통과: {passed_tests}")
                logger.info(f"  실패: {failed_tests}")
                logger.info(f"  건너뜀: {skipped_tests}")
                logger.info(f"  차단: {blocked_tests}")
                logger.info(f"  통과율: {pass_rate:.1f}%")
                
                # 기존 대시보드 요약 데이터 확인
                existing_summary = DashboardSummary.query.filter_by(environment=environment).first()
                
                if existing_summary:
                    # 기존 데이터 업데이트
                    existing_summary.total_tests = total_tests
                    existing_summary.passed_tests = passed_tests
                    existing_summary.failed_tests = failed_tests
                    existing_summary.skipped_tests = skipped_tests
                    existing_summary.pass_rate = round(pass_rate, 2)
                    existing_summary.last_updated = datetime.utcnow()
                    
                    logger.info(f"  ✅ 기존 요약 데이터 업데이트 완료")
                else:
                    # 새 데이터 생성
                    new_summary = DashboardSummary(
                        environment=environment,
                        total_tests=total_tests,
                        passed_tests=passed_tests,
                        failed_tests=failed_tests,
                        skipped_tests=skipped_tests,
                        pass_rate=round(pass_rate, 2),
                        last_updated=datetime.utcnow()
                    )
                    
                    db.session.add(new_summary)
                    logger.info(f"  ✅ 새 요약 데이터 생성 완료")
                
                logger.info("")
            
            # 3. 데이터베이스 커밋
            db.session.commit()
            logger.info("💾 데이터베이스 커밋 완료")
            
            # 4. 최종 결과 확인
            logger.info("📈 최종 대시보드 요약 데이터:")
            logger.info("=" * 60)
            
            summaries = DashboardSummary.query.all()
            for summary in summaries:
                logger.info(f"환경: {summary.environment}")
                logger.info(f"  총 테스트: {summary.total_tests}")
                logger.info(f"  통과: {summary.passed_tests}")
                logger.info(f"  실패: {summary.failed_tests}")
                logger.info(f"  건너뜀: {summary.skipped_tests}")
                logger.info(f"  통과율: {summary.pass_rate}%")
                logger.info(f"  마지막 업데이트: {summary.last_updated}")
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 스크립트 실행 중 오류 발생: {str(e)}")
            db.session.rollback()
            return False

def verify_sync():
    """동기화 결과 검증"""
    
    with app.app_context():
        try:
            # 테스트 케이스 실제 데이터와 대시보드 요약 데이터 비교
            query = text("""
                SELECT 
                    tc.environment,
                    tc.result_status,
                    COUNT(*) as count
                FROM TestCases tc
                GROUP BY tc.environment, tc.result_status
                ORDER BY tc.environment, tc.result_status
            """)
            
            result = db.session.execute(query)
            testcase_stats = result.fetchall()
            
            logger.info("🔍 동기화 결과 검증:")
            logger.info("=" * 60)
            
            # 환경별로 테스트 케이스 통계
            env_testcase_stats = {}
            for row in testcase_stats:
                env = row.environment
                if env not in env_testcase_stats:
                    env_testcase_stats[env] = {}
                env_testcase_stats[env][row.result_status] = row.count
            
            # 대시보드 요약 데이터와 비교
            summaries = DashboardSummary.query.all()
            summary_dict = {s.environment: s for s in summaries}
            
            for env, status_counts in env_testcase_stats.items():
                logger.info(f"🌍 환경: {env}")
                
                total_tests = sum(status_counts.values())
                passed_tests = status_counts.get('Pass', 0)
                failed_tests = status_counts.get('Fail', 0)
                skipped_tests = status_counts.get('N/T', 0) + status_counts.get('N/A', 0)
                
                if env in summary_dict:
                    summary = summary_dict[env]
                    logger.info(f"  테스트케이스 총계: {total_tests}개")
                    logger.info(f"  대시보드 총계: {summary.total_tests}개")
                    logger.info(f"  일치 여부: {'✅' if total_tests == summary.total_tests else '❌'}")
                else:
                    logger.info(f"  ❌ 대시보드 요약 데이터 없음")
                
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 검증 중 오류 발생: {str(e)}")
            return False

if __name__ == "__main__":
    logger.info("🚀 대시보드 요약 데이터 동기화 시작")
    
    # 1. 동기화 실행
    success = sync_dashboard_summary()
    
    if success:
        logger.info("✅ 동기화 완료")
        
        # 2. 결과 검증
        logger.info("🔍 동기화 결과 검증 중...")
        verify_success = verify_sync()
        
        if verify_success:
            logger.info("🎉 모든 작업이 성공적으로 완료되었습니다!")
        else:
            logger.warning("⚠️ 검증 중 문제가 발생했습니다.")
    else:
        logger.error("❌ 동기화에 실패했습니다.")
