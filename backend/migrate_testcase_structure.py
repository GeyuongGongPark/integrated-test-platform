#!/usr/bin/env python3
"""
테스트 케이스 구조 변경 마이그레이션 스크립트
기존 description 필드를 expected_result로 변경하고 새로운 필드 구조에 맞춰 업데이트
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def get_database_url():
    """데이터베이스 URL을 가져옵니다."""
    if os.environ.get('VERCEL'):
        # Vercel 환경
        return os.environ.get('DATABASE_URL')
    elif os.environ.get('FLASK_ENV') == 'production':
        # Production 환경
        return os.environ.get('DATABASE_URL')
    else:
        # Development 환경
        return os.environ.get('DATABASE_URL', 'sqlite:///instance/test.db')

def migrate_testcase_structure():
    """테스트 케이스 구조를 마이그레이션합니다."""
    database_url = get_database_url()
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return False
    
    try:
        # 데이터베이스 연결
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # SQLite용 컬럼 확인
            inspector = inspect(engine)
            columns = inspector.get_columns('TestCases')
            column_names = [col['name'] for col in columns]
            
            has_expected_result = 'expected_result' in column_names
            has_description = 'description' in column_names
            
            if not has_expected_result:
                print("🔄 expected_result 컬럼을 추가합니다...")
                conn.execute(text("""
                    ALTER TABLE "TestCases" 
                    ADD COLUMN expected_result TEXT
                """))
                print("✅ expected_result 컬럼 추가 완료")
            
            # description 컬럼의 데이터를 expected_result로 복사
            if has_description:
                print("🔄 description 데이터를 expected_result로 복사합니다...")
                conn.execute(text("""
                    UPDATE "TestCases" 
                    SET expected_result = description 
                    WHERE expected_result IS NULL AND description IS NOT NULL
                """))
                print("✅ 데이터 복사 완료")
                
                # description 컬럼 삭제 (선택사항)
                print("⚠️  description 컬럼을 삭제하시겠습니까? (y/N): ", end="")
                response = input().strip().lower()
                
                if response == 'y':
                    print("🔄 description 컬럼을 삭제합니다...")
                    # SQLite에서는 컬럼 삭제가 복잡하므로 임시 테이블 생성
                    conn.execute(text("""
                        CREATE TABLE "TestCases_new" (
                            id INTEGER PRIMARY KEY,
                            project_id INTEGER NOT NULL,
                            main_category VARCHAR(255) NOT NULL,
                            sub_category VARCHAR(255) NOT NULL,
                            detail_category VARCHAR(255) NOT NULL,
                            pre_condition TEXT,
                            expected_result TEXT,
                            remark TEXT,
                            result_status VARCHAR(10) DEFAULT 'N/T',
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            environment VARCHAR(50) DEFAULT 'dev',
                            deployment_date DATE,
                            folder_id INTEGER,
                            automation_code_path VARCHAR(512),
                            automation_code_type VARCHAR(50)
                        )
                    """))
                    
                    # 데이터 복사
                    conn.execute(text("""
                        INSERT INTO "TestCases_new" 
                        SELECT id, project_id, main_category, sub_category, detail_category,
                               pre_condition, expected_result, remark, result_status,
                               created_at, updated_at, environment, deployment_date,
                               folder_id, automation_code_path, automation_code_type
                        FROM "TestCases"
                    """))
                    
                    # 기존 테이블 삭제 및 새 테이블 이름 변경
                    conn.execute(text('DROP TABLE "TestCases"'))
                    conn.execute(text('ALTER TABLE "TestCases_new" RENAME TO "TestCases"'))
                    
                    print("✅ description 컬럼 삭제 완료")
                else:
                    print("ℹ️  description 컬럼을 유지합니다.")
            
            conn.commit()
            print("🎉 마이그레이션 완료!")
            return True
            
    except Exception as e:
        print(f"❌ 마이그레이션 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 테스트 케이스 구조 마이그레이션을 시작합니다...")
    success = migrate_testcase_structure()
    
    if success:
        print("✅ 마이그레이션이 성공적으로 완료되었습니다.")
        sys.exit(0)
    else:
        print("❌ 마이그레이션이 실패했습니다.")
        sys.exit(1) 