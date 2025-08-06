#!/usr/bin/env python3
"""
현재 데이터베이스의 테이블을 확인하는 스크립트
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

# .env 파일 로드
load_dotenv()

def check_database():
    """현재 데이터베이스의 테이블을 확인합니다."""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return
    
    try:
        print("🔗 데이터베이스에 연결 중...")
        engine = create_engine(database_url)
        
        # 연결 테스트
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ 데이터베이스 연결 성공")
        
        # 테이블 목록 확인
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 총 {len(tables)}개의 테이블을 발견했습니다:")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
        
        # 각 테이블의 행 수 확인
        print(f"\n📈 각 테이블의 데이터 수:")
        for table in tables:
            try:
                with engine.connect() as conn:
                    result = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    count = result.fetchone()[0]
                    print(f"  {table}: {count} 행")
            except Exception as e:
                print(f"  {table}: 확인 실패 - {str(e)}")
        
    except Exception as e:
        print(f"❌ 데이터베이스 확인 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🔍 현재 데이터베이스 상태를 확인합니다...")
    print("=" * 50)
    check_database() 