#!/usr/bin/env python3
"""
환경 변수 및 Flask 설정 디버그 스크립트
"""

import os
from dotenv import load_dotenv
from app import app

# .env 파일 로드
load_dotenv()

def debug_environment():
    """환경 변수 및 Flask 설정 확인"""
    print("🔍 환경 변수 및 Flask 설정 확인 중...")
    
    # 환경 변수 확인
    print(f"\n📊 환경 변수:")
    print(f"  - DATABASE_URL: {os.getenv('DATABASE_URL')}")
    print(f"  - DEV_DATABASE_URL: {os.getenv('DEV_DATABASE_URL')}")
    print(f"  - FLASK_ENV: {os.getenv('FLASK_ENV')}")
    
    # Flask 설정 확인
    with app.app_context():
        print(f"\n📊 Flask 설정:")
        print(f"  - SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        print(f"  - FLASK_ENV: {app.config.get('ENV')}")
        print(f"  - DEBUG: {app.config.get('DEBUG')}")
        
        # 현재 사용 중인 데이터베이스 확인
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'postgresql' in db_uri:
            print(f"  - ✅ PostgreSQL 사용 중")
        elif 'sqlite' in db_uri:
            print(f"  - ❌ SQLite 사용 중")
        else:
            print(f"  - ❓ 알 수 없는 데이터베이스: {db_uri}")

if __name__ == "__main__":
    debug_environment() 