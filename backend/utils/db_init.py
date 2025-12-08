"""
데이터베이스 초기화 및 관리 유틸리티
"""
import time
from sqlalchemy import text
from models import db, User
from utils.logger import get_logger
from utils.timezone_utils import get_kst_now, get_kst_isoformat

logger = get_logger(__name__)

def test_database_connection(app):
    """데이터베이스 연결 테스트 및 재시도 로직"""
    max_retries = 3
    retry_delay = 5  # 초 단위
    
    for i in range(max_retries):
        try:
            # 데이터베이스 연결 테스트
            if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
                db.session.execute(text('SELECT 1'))
                logger.info(f"SQLite 연결 테스트 성공 (시도 {i+1}/{max_retries})")
                return True
            else:
                db.session.execute(text('SELECT 1'))
                db.session.commit()
                logger.info(f"MySQL 연결 테스트 성공 (시도 {i+1}/{max_retries})")
                return True
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패 (시도 {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                logger.info(f"{retry_delay}초 후 다시 시도...")
                time.sleep(retry_delay)
            else:
                logger.error("데이터베이스 연결 재시도 실패. 앱을 종료합니다.")
                return False
    return False

def initialize_database(app):
    """데이터베이스 초기화 및 기본 사용자 생성"""
    try:
        # 데이터베이스 연결 테스트 및 재시도
        if not test_database_connection(app):
            return {
                'status': 'error',
                'message': 'Database connection failed after multiple retries',
                'timestamp': get_kst_isoformat(get_kst_now()),
                'error_type': 'ConnectionError',
                'database_url': app.config['SQLALCHEMY_DATABASE_URI'][:50] + '...' if len(app.config['SQLALCHEMY_DATABASE_URI']) > 50 else app.config['SQLALCHEMY_DATABASE_URI'],
                'environment': 'production' if 'vercel.app' in app.config.get('VERCEL_URL', '') else 'development'
            }, 500
        
        with app.app_context():
            # 테이블이 존재하지 않으면 자동 생성
            db.create_all()
            logger.info("데이터베이스 테이블 생성 완료")
            
            # 세션 격리 설정
            db.session.autoflush = False
            logger.info("세션 autoflush 비활성화")
            
            # 기본 사용자 생성 (테스트용)
            users_to_create = []
            
            # admin 사용자 체크 및 생성 준비
            if not User.query.filter_by(username='admin').first():
                admin_user = User(
                    username='admin',
                    email='admin@test.com',
                    first_name='관리자',
                    last_name='시스템',
                    role='admin',
                    is_active=True
                )
                admin_user.set_password('admin123')
                users_to_create.append(admin_user)
                logger.info("admin 사용자 생성 준비 완료")
            else:
                logger.info("admin 사용자가 이미 존재합니다")
            
            # testuser 체크 및 생성 준비
            if not User.query.filter_by(username='testuser').first():
                test_user = User(
                    username='testuser',
                    email='test@test.com',
                    first_name='테스트',
                    last_name='사용자',
                    role='user',
                    is_active=True
                )
                test_user.set_password('test123')
                users_to_create.append(test_user)
                logger.info("testuser 생성 준비 완료")
            else:
                logger.info("testuser가 이미 존재합니다")
            
            # 준비된 사용자들을 개별적으로 추가하고 커밋
            if users_to_create:
                for user in users_to_create:
                    try:
                        db.session.add(user)
                        db.session.commit()
                        logger.info(f"사용자 {user.username} 생성 완료")
                    except Exception as user_error:
                        db.session.rollback()
                        logger.error(f"사용자 {user.username} 생성 실패: {user_error}")
                        # 중복 오류인 경우 무시
                        if 'duplicate' not in str(user_error).lower() and 'unique' not in str(user_error).lower():
                            raise user_error
                logger.info(f"{len(users_to_create)}명의 사용자 생성 완료")
            else:
                logger.info("생성할 사용자가 없습니다")
            
            logger.info("데이터베이스 초기화 완료")
            
            # 세션 정리
            db.session.close()
            logger.info("세션 정리 완료")
        
        return {
            'status': 'success',
            'message': 'Database initialized successfully',
            'timestamp': get_kst_isoformat(get_kst_now())
        }, 200
        
    except Exception as e:
        logger.error(f"init-db 오류 발생: {str(e)}")
        logger.error(f"오류 타입: {type(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        
        # 세션 롤백
        try:
            db.session.rollback()
            logger.info("데이터베이스 세션 롤백 완료")
        except Exception as rollback_error:
            logger.error(f"롤백 중 오류 발생: {rollback_error}")
        
        return {
            'status': 'error',
            'message': f'Database initialization failed: {str(e)}',
            'timestamp': get_kst_isoformat(get_kst_now()),
            'error_type': str(type(e)),
            'traceback': traceback.format_exc()
        }, 500

