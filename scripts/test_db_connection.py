#!/usr/bin/env python3
"""
데이터베이스 연결 테스트 스크립트
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

# 프로젝트 루트로 경로 설정
project_root = Path(__file__).parent.parent
os.chdir(project_root)

# .env 파일 로드
load_dotenv()

def test_mysql_connection():
    """MySQL 연결 테스트"""
    try:
        import pymysql
        
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = int(os.environ.get('DB_PORT', '3306'))
        db_user = os.environ.get('DB_USER', 'root')
        db_password = os.environ.get('DB_PASSWORD', '1q2w#E$R')
        db_name = os.environ.get('DB_NAME', 'test_management')
        
        print(f"🔍 MySQL 연결 테스트 중...")
        print(f"   호스트: {db_host}:{db_port}")
        print(f"   사용자: {db_user}")
        print(f"   데이터베이스: {db_name}")
        
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        print("✅ MySQL 연결 성공!")
        return True
        
    except ImportError:
        print("❌ pymysql 모듈이 설치되지 않았습니다.")
        print("   설치: pip install pymysql")
        return False
    except Exception as e:
        print(f"❌ MySQL 연결 실패: {e}")
        return False

def test_sqlalchemy_connection():
    """SQLAlchemy를 통한 연결 테스트"""
    try:
        from sqlalchemy import create_engine, text
        
        db_type = os.environ.get('DB_TYPE', 'sqlite').lower()
        
        if db_type == 'mysql' or os.environ.get('DATABASE_URL', '').startswith('mysql'):
            db_host = os.environ.get('DB_HOST', 'localhost')
            db_port = os.environ.get('DB_PORT', '3306')
            db_user = os.environ.get('DB_USER', 'root')
            db_password = os.environ.get('DB_PASSWORD', '1q2w#E$R')
            db_name = os.environ.get('DB_NAME', 'test_management')
            
            # 비밀번호 URL 인코딩
            encoded_password = quote_plus(db_password)
            database_url = f'mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
        else:
            database_url = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
        
        print(f"\n🔍 SQLAlchemy 연결 테스트 중...")
        print(f"   URL: {database_url[:50]}...")
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            result.fetchone()
        
        print("✅ SQLAlchemy 연결 성공!")
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy 연결 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("데이터베이스 연결 테스트")
    print("=" * 50)
    
    # 환경 변수 확인
    print("\n📋 환경 변수 확인:")
    db_type = os.environ.get('DB_TYPE', 'sqlite')
    print(f"   DB_TYPE: {db_type}")
    
    if db_type == 'mysql':
        print(f"   DB_HOST: {os.environ.get('DB_HOST', 'localhost')}")
        print(f"   DB_PORT: {os.environ.get('DB_PORT', '3306')}")
        print(f"   DB_USER: {os.environ.get('DB_USER', 'root')}")
        print(f"   DB_NAME: {os.environ.get('DB_NAME', 'test_management')}")
    
    # 연결 테스트
    print("\n" + "=" * 50)
    success1 = test_mysql_connection()
    
    print("\n" + "=" * 50)
    success2 = test_sqlalchemy_connection()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ 모든 연결 테스트 통과!")
        sys.exit(0)
    else:
        print("❌ 연결 테스트 실패")
        sys.exit(1)

