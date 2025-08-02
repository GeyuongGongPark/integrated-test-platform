#!/usr/bin/env python3
"""
Neon PostgreSQL 데이터 확인 스크립트
"""

import psycopg2
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def connect_neon():
    """Neon PostgreSQL 데이터베이스 연결"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    
    return psycopg2.connect(database_url)

def check_data():
    """데이터 확인"""
    print("🔍 Neon PostgreSQL 데이터 확인 중...")
    
    try:
        conn = connect_neon()
        cursor = conn.cursor()
        
        # 테이블 목록 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"📋 테이블 목록:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 각 테이블의 데이터 수 확인
        print(f"\n📊 테이블별 데이터 수:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count}개 행")
        
        # TestCases 테이블 데이터 확인
        print(f"\n🧪 TestCases 데이터:")
        cursor.execute('SELECT id, project_id, main_category, sub_category, detail_category, description, result_status FROM "TestCases"')
        test_cases = cursor.fetchall()
        for tc in test_cases:
            print(f"  - ID: {tc[0]}, 프로젝트: {tc[1]}, 카테고리: {tc[2]}/{tc[3]}/{tc[4]}, 상태: {tc[6]}")
        
        # projects 테이블 데이터 확인
        print(f"\n📋 projects 데이터:")
        cursor.execute('SELECT id, name, description FROM "projects"')
        projects = cursor.fetchall()
        for project in projects:
            print(f"  - ID: {project[0]}, 이름: {project[1]}, 설명: {project[2]}")
        
        # test_result 테이블 데이터 확인
        print(f"\n📈 test_result 데이터:")
        cursor.execute('SELECT id, test_case_id, result, executed_at FROM "test_result"')
        test_results = cursor.fetchall()
        for tr in test_results:
            print(f"  - ID: {tr[0]}, 테스트케이스: {tr[1]}, 결과: {tr[2]}, 실행시간: {tr[3]}")
        
        conn.close()
        print("\n✅ 데이터 확인 완료!")
        
    except Exception as e:
        print(f"❌ 데이터 확인 오류: {e}")

if __name__ == "__main__":
    check_data() 