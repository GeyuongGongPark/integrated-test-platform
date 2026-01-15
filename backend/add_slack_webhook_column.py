#!/usr/bin/env python3
"""
NotificationSettings 테이블에 slack_webhook_url 컬럼 추가 스크립트
이 스크립트는 직접 실행하여 컬럼을 추가할 수 있습니다.
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db
from app import app
from sqlalchemy import text, inspect

def add_slack_webhook_column():
    """slack_webhook_url 컬럼 추가"""
    with app.app_context():
        inspector = inspect(db.engine)
        
        # NotificationSettings 테이블 존재 확인
        if 'NotificationSettings' not in inspector.get_table_names():
            print("❌ NotificationSettings 테이블이 존재하지 않습니다.")
            return False
        
        # 컬럼 존재 확인
        columns = [col['name'] for col in inspector.get_columns('NotificationSettings')]
        if 'slack_webhook_url' in columns:
            print("✅ slack_webhook_url 컬럼이 이미 존재합니다.")
            return True
        
        # 컬럼 추가
        try:
            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE NotificationSettings "
                    "ADD COLUMN slack_webhook_url VARCHAR(500) NULL"
                ))
                conn.commit()
            print("✅ slack_webhook_url 컬럼이 성공적으로 추가되었습니다.")
            return True
        except Exception as e:
            print(f"❌ 컬럼 추가 중 오류 발생: {str(e)}")
            return False

if __name__ == '__main__':
    print("🔧 NotificationSettings 테이블에 slack_webhook_url 컬럼 추가 중...")
    success = add_slack_webhook_column()
    sys.exit(0 if success else 1)

