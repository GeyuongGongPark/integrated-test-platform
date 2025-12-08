"""
데이터베이스 헬퍼 유틸리티
로컬 개발 환경에서 데이터베이스 설정을 쉽게 확인할 수 있는 도구
"""
import os
from sqlalchemy import create_engine, text
from utils.logger import get_logger

logger = get_logger(__name__)


def test_database_connection(database_url):
    """데이터베이스 연결 테스트"""
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            if 'sqlite' in database_url:
                result = conn.execute(text('SELECT 1'))
            else:
                result = conn.execute(text('SELECT 1'))
                conn.commit()
        logger.info("✅ 데이터베이스 연결 성공")
        return True
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
        return False


def get_database_info(database_url):
    """데이터베이스 정보 반환"""
    if 'sqlite' in database_url:
        db_path = database_url.replace('sqlite:///', '')
        return {
            'type': 'SQLite',
            'path': db_path,
            'exists': os.path.exists(db_path) if db_path else False
        }
    else:
        # MySQL URL 파싱
        # mysql+pymysql://user:password@host:port/database
        try:
            url_parts = database_url.replace('mysql+pymysql://', '').split('@')
            if len(url_parts) == 2:
                user_pass = url_parts[0].split(':')
                host_db = url_parts[1].split('/')
                host_port = host_db[0].split(':')
                
                return {
                    'type': 'MySQL',
                    'host': host_port[0],
                    'port': host_port[1] if len(host_port) > 1 else '3306',
                    'database': host_db[1] if len(host_db) > 1 else '',
                    'user': user_pass[0]
                }
        except Exception:
            pass
        
        return {
            'type': 'MySQL',
            'url': database_url[:50] + '...' if len(database_url) > 50 else database_url
        }

