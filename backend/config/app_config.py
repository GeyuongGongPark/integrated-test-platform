"""
Flask 앱 설정 관리
"""
import os
from datetime import timedelta
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger(__name__)

# .env 파일 로드 (절대 경로 사용)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)

def get_database_url():
    """데이터베이스 URL 설정"""
    is_vercel = 'vercel.app' in os.environ.get('VERCEL_URL', '') or os.environ.get('VERCEL') == '1'
    
    if is_vercel:
        # Vercel 환경에서는 환경 변수 사용
        database_url = os.environ.get('DATABASE_URL')
        
        # DATABASE_URL이 없으면 SQLite 사용
        if not database_url:
            logger.warning("DATABASE_URL이 설정되지 않음, SQLite 사용")
            database_url = 'sqlite:///:memory:'
        elif database_url.startswith('mysql://'):
            database_url = database_url.replace('mysql://', 'mysql+pymysql://')
            # ssl_mode 파라미터 제거하고 기본 SSL 설정 사용
            if '?' in database_url:
                # 기존 파라미터가 있으면 ssl_mode만 제거
                params = database_url.split('?')[1].split('&')
                filtered_params = [p for p in params if not p.startswith('ssl_mode=')]
                if filtered_params:
                    database_url = database_url.split('?')[0] + '?' + '&'.join(filtered_params)
            logger.info("Vercel 환경에서 MySQL 연결 설정 적용")
        else:
            logger.info(f"Vercel 환경에서 데이터베이스 URL 사용: {database_url[:20]}...")
    else:
        # 로컬 개발 환경
        # 1. 환경 변수에서 DATABASE_URL 확인
        database_url = os.environ.get('DATABASE_URL')
        
        # 2. DB_TYPE 환경 변수 확인 (sqlite 또는 mysql)
        db_type = os.environ.get('DB_TYPE', 'sqlite').lower()
        
        if database_url:
            # 환경 변수에 DATABASE_URL이 있으면 사용
            logger.info("로컬 환경에서 환경 변수 DATABASE_URL 사용")
        elif db_type == 'mysql':
            # MySQL 사용 (기본값)
            from urllib.parse import quote_plus
            db_host = os.environ.get('DB_HOST', 'localhost')
            db_port = os.environ.get('DB_PORT', '3306')
            db_user = os.environ.get('DB_USER', 'root')
            db_password = os.environ.get('DB_PASSWORD', '1q2w#E$R')
            db_name = os.environ.get('DB_NAME', 'test_management')
            # 비밀번호 URL 인코딩 (특수문자 처리)
            encoded_password = quote_plus(db_password)
            database_url = f'mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
            logger.info(f"로컬 환경에서 MySQL 사용: {db_host}:{db_port}/{db_name}")
        else:
            # SQLite 사용 (기본값, 가장 간단)
            db_path = os.environ.get('DB_PATH', 'local.db')
            # 절대 경로 또는 상대 경로 처리
            if not os.path.isabs(db_path):
                # 상대 경로인 경우 프로젝트 루트 기준
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                db_path = os.path.join(project_root, db_path)
            database_url = f'sqlite:///{db_path}'
            logger.info(f"로컬 환경에서 SQLite 사용: {db_path}")
    
    return database_url

def get_database_engine_options(database_url):
    """데이터베이스 엔진 옵션 설정"""
    is_vercel = 'vercel.app' in os.environ.get('VERCEL_URL', '') or os.environ.get('VERCEL') == '1'
    
    if 'sqlite' in database_url:
        # SQLite 환경
        if is_vercel:
            logger.info("Vercel 환경에서 SQLite 사용")
        else:
            logger.info("로컬 환경에서 SQLite 사용")
        return {}
    else:
        # MySQL/Postgres 환경 (Vercel 또는 로컬)
        options = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }

        if 'mysql' in database_url:
            options['connect_args'] = {
                'connect_timeout': 10,
                'read_timeout': 30,
                'write_timeout': 30
            }

            # Vercel 환경에서만 SSL 사용
            if is_vercel:
                options['connect_args']['ssl'] = {'ssl': True}

        return options

def configure_app(app):
    """Flask 앱 설정 적용"""
    # 기본 설정
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key or secret_key == 'fallback-secret-key':
        logger.warning("⚠️ SECRET_KEY가 환경 변수로 설정되지 않았습니다. 프로덕션 환경에서는 반드시 설정하세요.")
    app.config['SECRET_KEY'] = secret_key or 'fallback-secret-key'
    
    # JWT 설정
    jwt_secret_key = os.environ.get('JWT_SECRET_KEY')
    if not jwt_secret_key or jwt_secret_key == 'your-secret-key-change-in-production':
        logger.warning("⚠️ JWT_SECRET_KEY가 환경 변수로 설정되지 않았습니다. 프로덕션 환경에서는 반드시 강력한 시크릿 키를 설정하세요.")
    app.config['JWT_SECRET_KEY'] = jwt_secret_key or 'your-secret-key-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # 24시간으로 연장
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # 30일로 연장
    
    # 데이터베이스 설정
    database_url = get_database_url()
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = get_database_engine_options(database_url)
    
    # 환경 변수 로깅 (디버깅용)
    is_vercel = 'vercel.app' in os.environ.get('VERCEL_URL', '') or os.environ.get('VERCEL') == '1'
    logger.debug(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
    logger.debug(f"Secret Key: {app.config['SECRET_KEY']}")
    logger.debug(f"JWT Secret Key: {app.config['JWT_SECRET_KEY']}")
    logger.info(f"Environment: {'production' if is_vercel else 'development'}")
    logger.debug(f"Vercel URL: {os.environ.get('VERCEL_URL', 'Not Vercel')}")
    logger.debug(f".env 파일 경로: {env_path}")
    logger.debug(f".env 파일 존재: {os.path.exists(env_path)}")
    
    # Slack webhook URL 확인
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if slack_webhook_url:
        logger.info(f"✅ SLACK_WEBHOOK_URL 환경 변수 로드됨: {slack_webhook_url[:30]}...")
    else:
        logger.warning("⚠️ SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    return app

def is_vercel_environment():
    """Vercel 환경 여부 확인"""
    return 'vercel.app' in os.environ.get('VERCEL_URL', '') or os.environ.get('VERCEL') == '1'

