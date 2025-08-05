#!/usr/bin/env python3
"""
PostgreSQL 데이터베이스에 expected_result 컬럼 추가
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def fix_postgresql():
    """PostgreSQL 데이터베이스에 expected_result 컬럼을 추가합니다."""
    
    # PostgreSQL 데이터베이스 URL (하드코딩)
    database_url = "postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    try:
        print("🔄 PostgreSQL 데이터베이스에 연결 중...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # expected_result 컬럼이 있는지 확인
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
                
                # description 컬럼의 데이터를 expected_result로 복사
                print("🔄 description 데이터를 expected_result로 복사합니다...")
                conn.execute(text("""
                    UPDATE "TestCases" 
                    SET expected_result = description 
                    WHERE expected_result IS NULL AND description IS NOT NULL
                """))
                print("✅ 데이터 복사 완료")
            else:
                print("ℹ️  expected_result 컬럼이 이미 존재합니다.")
            
            conn.commit()
            print("🎉 PostgreSQL 데이터베이스 수정 완료!")
            return True
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 PostgreSQL 데이터베이스 수정을 시작합니다...")
    success = fix_postgresql()
    
    if success:
        print("✅ 수정이 성공적으로 완료되었습니다.")
        sys.exit(0)
    else:
        print("❌ 수정이 실패했습니다.")
        sys.exit(1) 