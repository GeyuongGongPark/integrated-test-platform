#!/usr/bin/env python3
"""
테스트 케이스의 환경 정보를 상위 폴더의 환경 정보로 업데이트하는 스크립트
"""

from app import app, db
from models import TestCase, Folder
from sqlalchemy import text
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_testcase_environments():
    """테스트 케이스의 환경 정보를 상위 폴더의 환경 정보로 업데이트"""
    
    with app.app_context():
        try:
            # 1. 현재 테스트 케이스와 폴더 정보 조회
            query = text("""
                SELECT 
                    tc.id as testcase_id,
                    tc.name as testcase_name,
                    tc.environment as current_env,
                    tc.folder_id,
                    f.folder_name,
                    f.environment as folder_env
                FROM TestCases tc
                LEFT JOIN Folders f ON tc.folder_id = f.id
                ORDER BY tc.folder_id, tc.id
            """)
            
            result = db.session.execute(query)
            testcases = result.fetchall()
            
            logger.info(f"📊 총 {len(testcases)}개의 테스트 케이스 발견")
            
            # 2. 환경 정보가 다른 테스트 케이스들 찾기
            mismatched_cases = []
            for row in testcases:
                if row.current_env != row.folder_env:
                    mismatched_cases.append({
                        'id': row.testcase_id,
                        'name': row.testcase_name,
                        'current_env': row.current_env,
                        'folder_env': row.folder_env,
                        'folder_name': row.folder_name
                    })
            
            logger.info(f"🔄 환경 정보가 다른 테스트 케이스: {len(mismatched_cases)}개")
            
            # 3. 환경 정보 업데이트
            updated_count = 0
            for case in mismatched_cases:
                try:
                    # SQLAlchemy ORM을 사용한 업데이트
                    testcase = TestCase.query.get(case['id'])
                    if testcase:
                        old_env = testcase.environment
                        testcase.environment = case['folder_env']
                        db.session.commit()
                        updated_count += 1
                        logger.info(f"✅ 업데이트 완료: {case['name']} ({old_env} → {case['folder_env']})")
                    else:
                        logger.warning(f"⚠️ 테스트 케이스를 찾을 수 없음: ID {case['id']}")
                        
                except Exception as e:
                    logger.error(f"❌ 업데이트 실패: {case['name']} - {str(e)}")
                    db.session.rollback()
            
            logger.info(f"🎉 총 {updated_count}개의 테스트 케이스 환경 정보 업데이트 완료")
            
            # 4. 업데이트 후 결과 확인
            final_query = text("""
                SELECT 
                    tc.environment as testcase_env,
                    f.environment as folder_env,
                    COUNT(*) as count
                FROM TestCases tc
                LEFT JOIN Folders f ON tc.folder_id = f.id
                GROUP BY tc.environment, f.environment
                ORDER BY tc.environment, f.environment
            """)
            
            final_result = db.session.execute(final_query)
            final_stats = final_result.fetchall()
            
            logger.info("📈 최종 통계:")
            for stat in final_stats:
                logger.info(f"   테스트케이스: {stat.testcase_env}, 폴더: {stat.folder_env} → {stat.count}개")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 스크립트 실행 중 오류 발생: {str(e)}")
            db.session.rollback()
            return False

def verify_environment_consistency():
    """환경 정보 일관성 검증"""
    
    with app.app_context():
        try:
            # 환경 정보가 일치하지 않는 테스트 케이스 확인
            query = text("""
                SELECT 
                    COUNT(*) as mismatched_count
                FROM TestCases tc
                LEFT JOIN Folders f ON tc.folder_id = f.id
                WHERE tc.environment != f.environment
            """)
            
            result = db.session.execute(query)
            mismatched_count = result.fetchone().mismatched_count
            
            if mismatched_count == 0:
                logger.info("✅ 모든 테스트 케이스의 환경 정보가 폴더와 일치합니다!")
                return True
            else:
                logger.warning(f"⚠️ {mismatched_count}개의 테스트 케이스가 여전히 환경 정보가 일치하지 않습니다.")
                return False
                
        except Exception as e:
            logger.error(f"❌ 검증 중 오류 발생: {str(e)}")
            return False

if __name__ == "__main__":
    logger.info("🚀 테스트 케이스 환경 정보 업데이트 시작")
    
    # 1. 환경 정보 업데이트
    success = update_testcase_environments()
    
    if success:
        logger.info("✅ 환경 정보 업데이트 완료")
        
        # 2. 일관성 검증
        logger.info("🔍 환경 정보 일관성 검증 중...")
        is_consistent = verify_environment_consistency()
        
        if is_consistent:
            logger.info("🎉 모든 작업이 성공적으로 완료되었습니다!")
        else:
            logger.warning("⚠️ 일부 테스트 케이스의 환경 정보가 여전히 일치하지 않습니다.")
    else:
        logger.error("❌ 환경 정보 업데이트에 실패했습니다.")
