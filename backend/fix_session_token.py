#!/usr/bin/env python3
"""
session_token 컬럼 길이를 500자로 수정하는 스크립트
"""

import os
import sys
from sqlalchemy import create_engine, text

def fix_session_token_length():
    """UserSessions 테이블의 session_token 컬럼 길이를 500자로 수정"""
    
    # 데이터베이스 연결
    database_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:1q2w#E$R@127.0.0.1:3306/test_management')
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # 현재 컬럼 정보 확인
            result = conn.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'test_management' 
                AND TABLE_NAME = 'UserSessions' 
                AND COLUMN_NAME = 'session_token'
            """))
            
            column_info = result.fetchone()
            if column_info:
                print(f"🔍 현재 session_token 컬럼 정보:")
                print(f"   타입: {column_info[1]}")
                print(f"   길이: {column_info[2]}")
                print(f"   NULL 허용: {column_info[3]}")
                
                if column_info[2] and column_info[2] < 500:
                    print("🔧 컬럼 길이를 500자로 수정합니다...")
                    
                    # 컬럼 길이 수정
                    conn.execute(text("""
                        ALTER TABLE UserSessions 
                        MODIFY COLUMN session_token VARCHAR(500) NOT NULL
                    """))
                    
                    print("✅ session_token 컬럼 길이 수정 완료!")
                    
                    # 수정 후 확인
                    result = conn.execute(text("""
                        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = 'test_management' 
                        AND TABLE_NAME = 'UserSessions' 
                        AND COLUMN_NAME = 'session_token'
                    """))
                    
                    updated_info = result.fetchone()
                    print(f"🔍 수정 후 session_token 컬럼 정보:")
                    print(f"   타입: {updated_info[1]}")
                    print(f"   길이: {updated_info[2]}")
                    print(f"   NULL 허용: {updated_info[3]}")
                    
                else:
                    print("✅ session_token 컬럼 길이가 이미 충분합니다.")
            else:
                print("❌ UserSessions 테이블이나 session_token 컬럼을 찾을 수 없습니다.")
                
            conn.commit()
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 session_token 컬럼 길이 수정 시작...")
    success = fix_session_token_length()
    
    if success:
        print("🎉 모든 작업이 완료되었습니다!")
    else:
        print("💥 작업 중 오류가 발생했습니다.")
        sys.exit(1)
