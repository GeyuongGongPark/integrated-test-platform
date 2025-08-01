#!/usr/bin/env python3
"""
PlanetScale 데이터베이스 연결 테스트 스크립트
"""

import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def test_planetscale_connection():
    """PlanetScale 연결을 테스트합니다."""
    
    # 환경 변수에서 데이터베이스 URL 가져오기
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
        print("env.example 파일을 .env로 복사하고 DATABASE_URL을 설정해주세요.")
        return False
    
    try:
        # 연결 문자열 파싱 (mysql://username:password@host:port/database)
        # 예: mysql://username:password@aws.connect.psdb.cloud/test-platform-db?sslaccept=strict
        
        # PyMySQL을 사용한 연결 테스트
        connection = pymysql.connect(
            host=database_url.split('@')[1].split('/')[0].split(':')[0],
            port=int(database_url.split('@')[1].split('/')[0].split(':')[1]),
            user=database_url.split('://')[1].split(':')[0],
            password=database_url.split('://')[1].split(':')[1].split('@')[0],
            database=database_url.split('/')[-1].split('?')[0],
            ssl={'ssl': {'ssl-mode': 'preferred'}}
        )
        
        print("✅ PlanetScale 연결 성공!")
        
        # 테이블 생성 테스트
        with connection.cursor() as cursor:
            # 테스트 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 테스트 데이터 삽입
            cursor.execute("""
                INSERT INTO test_connection (message) VALUES ('PlanetScale 연결 테스트 성공!')
            """)
            
            # 테스트 데이터 조회
            cursor.execute("SELECT * FROM test_connection ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                print(f"✅ 테스트 데이터 조회 성공: {result}")
            
            # 테스트 테이블 삭제
            cursor.execute("DROP TABLE test_connection")
            
        connection.commit()
        connection.close()
        
        print("✅ 모든 테스트가 성공적으로 완료되었습니다!")
        return True
        
    except Exception as e:
        print(f"❌ PlanetScale 연결 실패: {str(e)}")
        print("\n🔧 문제 해결 방법:")
        print("1. DATABASE_URL이 올바른 형식인지 확인")
        print("2. PlanetScale 대시보드에서 연결 정보 재확인")
        print("3. SSL 설정 확인")
        return False

if __name__ == "__main__":
    test_planetscale_connection() 