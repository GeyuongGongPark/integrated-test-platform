#!/usr/bin/env python3
"""
폴더 ID가 없는 테스트 케이스들을 적절한 폴더에 할당하고 환경 정보를 설정하는 스크립트
"""

from app import app, db
from models import TestCase, Folder
from sqlalchemy import text
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_orphaned_testcases():
    """폴더 ID가 없는 테스트 케이스들을 적절한 폴더에 할당"""
    
    with app.app_context():
        try:
            # 1. 사용 가능한 폴더들 조회
            available_folders = Folder.query.filter_by(folder_type='deployment_date').all()
            logger.info(f"📁 사용 가능한 폴더 수: {len(available_folders)}")
            
            # 환경별로 폴더 그룹화
            folders_by_env = {}
            for folder in available_folders:
                if folder.environment not in folders_by_env:
                    folders_by_env[folder.environment] = []
                folders_by_env[folder.environment].append(folder)
            
            for env, folders in folders_by_env.items():
                logger.info(f"   {env}: {len(folders)}개 폴더")
            
            # 2. 폴더 ID가 없는 테스트 케이스들 조회
            orphaned_testcases = TestCase.query.filter_by(folder_id=None).all()
            logger.info(f"🔍 폴더 ID가 없는 테스트 케이스 수: {len(orphaned_testcases)}")
            
            if not orphaned_testcases:
                logger.info("✅ 모든 테스트 케이스가 폴더에 할당되어 있습니다.")
                return True
            
            # 3. 테스트 케이스들을 환경별로 분류하여 적절한 폴더에 할당
            updated_count = 0
            
            for testcase in orphaned_testcases:
                try:
                    # 테스트 케이스 이름을 기반으로 환경 추정
                    assigned_env = 'dev'  # 기본값
                    
                    # 이름에 특정 키워드가 있으면 해당 환경으로 할당
                    name_lower = testcase.name.lower()
                    if 'alpha' in name_lower or 'staging' in name_lower:
                        assigned_env = 'alpha'
                    elif 'prod' in name_lower or 'production' in name_lower:
                        assigned_env = 'production'
                    elif 'dev' in name_lower:
                        assigned_env = 'dev'
                    
                    # 해당 환경의 폴더가 있는지 확인
                    if assigned_env in folders_by_env and folders_by_env[assigned_env]:
                        # 첫 번째 폴더에 할당 (가장 최근 배포일자)
                        target_folder = folders_by_env[assigned_env][0]
                        
                        old_folder_id = testcase.folder_id
                        old_environment = testcase.environment
                        
                        testcase.folder_id = target_folder.id
                        testcase.environment = target_folder.environment
                        
                        db.session.commit()
                        updated_count += 1
                        
                        logger.info(f"✅ 할당 완료: '{testcase.name}' → {target_folder.folder_name} ({target_folder.environment})")
                        
                    else:
                        # 해당 환경의 폴더가 없으면 dev 환경에 할당
                        if 'dev' in folders_by_env and folders_by_env['dev']:
                            target_folder = folders_by_env['dev'][0]
                            
                            testcase.folder_id = target_folder.id
                            testcase.environment = target_folder.environment
                            
                            db.session.commit()
                            updated_count += 1
                            
                            logger.info(f"✅ 기본 할당: '{testcase.name}' → {target_folder.folder_name} (dev)")
                        else:
                            logger.warning(f"⚠️ 적절한 폴더를 찾을 수 없음: '{testcase.name}'")
                            
                except Exception as e:
                    logger.error(f"❌ 할당 실패: '{testcase.name}' - {str(e)}")
                    db.session.rollback()
            
            logger.info(f"🎉 총 {updated_count}개의 테스트 케이스 폴더 할당 완료")
            
            # 4. 최종 결과 확인
            final_orphaned = TestCase.query.filter_by(folder_id=None).count()
            logger.info(f"📊 폴더 ID가 없는 테스트 케이스: {final_orphaned}개")
            
            if final_orphaned == 0:
                logger.info("✅ 모든 테스트 케이스가 폴더에 할당되었습니다!")
            else:
                logger.warning(f"⚠️ 여전히 {final_orphaned}개의 테스트 케이스가 폴더에 할당되지 않았습니다.")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 스크립트 실행 중 오류 발생: {str(e)}")
            db.session.rollback()
            return False

def verify_testcase_assignments():
    """테스트 케이스 할당 상태 검증"""
    
    with app.app_context():
        try:
            # 환경별 테스트 케이스 수 확인
            query = text("""
                SELECT 
                    tc.environment,
                    COUNT(*) as count
                FROM TestCases tc
                WHERE tc.folder_id IS NOT NULL
                GROUP BY tc.environment
                ORDER BY tc.environment
            """)
            
            result = db.session.execute(query)
            stats = result.fetchall()
            
            logger.info("📈 환경별 테스트 케이스 할당 현황:")
            total = 0
            for stat in stats:
                logger.info(f"   {stat.environment}: {stat.count}개")
                total += stat.count
            
            logger.info(f"   총 할당된 테스트 케이스: {total}개")
            
            # 폴더 ID가 없는 테스트 케이스 수
            orphaned_count = TestCase.query.filter_by(folder_id=None).count()
            logger.info(f"   폴더 ID가 없는 테스트 케이스: {orphaned_count}개")
            
            return orphaned_count == 0
            
        except Exception as e:
            logger.error(f"❌ 검증 중 오류 발생: {str(e)}")
            return False

if __name__ == "__main__":
    logger.info("🚀 고아 테스트 케이스 폴더 할당 시작")
    
    # 1. 폴더 할당
    success = fix_orphaned_testcases()
    
    if success:
        logger.info("✅ 폴더 할당 완료")
        
        # 2. 할당 상태 검증
        logger.info("🔍 할당 상태 검증 중...")
        is_fully_assigned = verify_testcase_assignments()
        
        if is_fully_assigned:
            logger.info("🎉 모든 테스트 케이스가 폴더에 할당되었습니다!")
        else:
            logger.warning("⚠️ 일부 테스트 케이스가 여전히 폴더에 할당되지 않았습니다.")
    else:
        logger.error("❌ 폴더 할당에 실패했습니다.")
