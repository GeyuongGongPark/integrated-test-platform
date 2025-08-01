import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """기본 설정"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql://root@localhost:3306/testmanager'

class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    @classmethod
    def init_app(cls, app):
        # 프로덕션 환경에서 SSL 설정
        if os.environ.get('SSL_REDIRECT'):
            from flask_sslify import SSLify
            sslify = SSLify(app)

class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 