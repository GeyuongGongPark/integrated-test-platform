#!/usr/bin/env python3
"""
PostgreSQL 테스트 케이스 구조 변경 마이그레이션 스크립트
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def get_database_url():
    """데이터베이스 URL을 가져옵니다."""
    return os.environ.get('DATABASE_URL')

def migrate_postgresql_structure():
    """PostgreSQL 테스트 케이스 구조를 마이그레이션합니다."""
    database_url = get_database_url()
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return False
    
    try:
        # 데이터베이스 연결
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # 1. expected_result 컬럼이 있는지 확인
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_name = 'TestCases' 
                AND column_name = 'expected_result'
            """))
            
            has_expected_result = result.fetchone()[0] > 0
            
            if not has_expected_result:
                print("🔄 expected_result 컬럼을 추가합니다...")
                conn.execute(text("""
                    ALTER TABLE "TestCases" 
                    ADD COLUMN expected_result TEXT
                """))
                print("✅ expected_result 컬럼 추가 완료")
            
            # 2. description 컬럼의 데이터를 expected_result로 복사
            print("🔄 description 데이터를 expected_result로 복사합니다...")
            conn.execute(text("""
                UPDATE "TestCases" 
                SET expected_result = description 
                WHERE expected_result IS NULL AND description IS NOT NULL
            """))
            print("✅ 데이터 복사 완료")
            
            # 3. description 컬럼 삭제 (선택사항)
            print("⚠️  description 컬럼을 삭제하시겠습니까? (y/N): ", end="")
            response = input().strip().lower()
            
            if response == 'y':
                print("🔄 description 컬럼을 삭제합니다...")
                conn.execute(text("""
                    ALTER TABLE "TestCases" 
                    DROP COLUMN description
                """))
                print("✅ description 컬럼 삭제 완료")
            else:
                print("ℹ️  description 컬럼을 유지합니다.")
            
            conn.commit()
            print("🎉 PostgreSQL 마이그레이션 완료!")
            return True
            
    except Exception as e:
        print(f"❌ 마이그레이션 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 PostgreSQL 테스트 케이스 구조 마이그레이션을 시작합니다...")
    success = migrate_postgresql_structure()
    
    if success:
        print("✅ 마이그레이션이 성공적으로 완료되었습니다.")
        sys.exit(0)
    else:
        print("❌ 마이그레이션이 실패했습니다.")
        sys.exit(1) 