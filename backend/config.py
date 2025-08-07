import os
from datetime import datetime

class Config:
    """기본 설정"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        os.environ.get('DATABASE_URL') or \
        'sqlite:///test_management.db'

class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    # Vercel 환경에서는 PostgreSQL을 강제로 사용
    if os.environ.get('VERCEL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        if not SQLALCHEMY_DATABASE_URI:
            raise ValueError("Vercel 환경에서 DATABASE_URL이 설정되지 않았습니다.")
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL') or \
            os.environ.get('DATABASE_URL') or \
            'sqlite:///test_management.db'
    
    # Vercel 환경에서 파일 시스템 접근 방지
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    @classmethod
    def init_app(cls, app):
        # Vercel 환경에서 instance_path 설정
        if os.environ.get('VERCEL'):
            app.instance_path = '/tmp'
        # 프로덕션 환경에서 SSL 설정 (선택사항)
        pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 