#!/usr/bin/env python3
"""
PostgreSQL에 AutomationTests 테이블을 생성하는 스크립트
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

def create_automation_tests_table():
    """PostgreSQL에 AutomationTests 테이블을 생성합니다."""
    database_url = get_database_url()
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return False
    
    try:
        # 데이터베이스 연결
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # AutomationTests 테이블이 존재하는지 확인
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_name = 'AutomationTests'
            """))
            
            table_exists = result.fetchone()[0] > 0
            
            if table_exists:
                print("ℹ️  AutomationTests 테이블이 이미 존재합니다.")
                return True
            
            print("🔄 AutomationTests 테이블을 생성합니다...")
            
            # AutomationTests 테이블 생성
            conn.execute(text("""
                CREATE TABLE "AutomationTests" (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    test_type VARCHAR(50) NOT NULL,
                    script_path VARCHAR(512) NOT NULL,
                    environment VARCHAR(50) DEFAULT 'dev',
                    parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            print("✅ AutomationTests 테이블 생성 완료")
            
            # updated_at 컬럼에 트리거 생성 (선택사항)
            print("🔄 updated_at 트리거를 생성합니다...")
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """))
            
            conn.execute(text("""
                CREATE TRIGGER update_automation_tests_updated_at 
                BEFORE UPDATE ON "AutomationTests"
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """))
            
            print("✅ updated_at 트리거 생성 완료")
            
            conn.commit()
            print("🎉 AutomationTests 테이블 생성 완료!")
            return True
            
    except Exception as e:
        print(f"❌ 테이블 생성 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 PostgreSQL AutomationTests 테이블 생성을 시작합니다...")
    success = create_automation_tests_table()
    
    if success:
        print("✅ 테이블 생성이 성공적으로 완료되었습니다.")
        sys.exit(0)
    else:
        print("❌ 테이블 생성이 실패했습니다.")
        sys.exit(1) 