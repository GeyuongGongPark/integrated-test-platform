from flask import request
import os
from utils.logger import get_logger

logger = get_logger(__name__)

def setup_cors(app):
    """CORS 설정 - 로컬 및 Vercel 환경 모두 지원"""
    from flask_cors import CORS
    
    # Vercel 환경인지 확인
    is_vercel = 'vercel.app' in os.environ.get('VERCEL_URL', '') or os.environ.get('VERCEL') == '1'
    
    if is_vercel:
        logger.info("Vercel 환경에서 고급 CORS 설정을 적용합니다.")
    else:
        logger.info("로컬 환경에서 기본 CORS 설정을 적용합니다.")
    
    # CORS 설정 - 모든 origin 허용
    CORS(app, 
         origins=['*'], 
         supports_credentials=False, 
         allow_headers=['*'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'],
         expose_headers=['*'],
         max_age=86400)
    
    # 명시적 CORS 헤더 설정
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        
        # 모든 Origin 허용
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = '*'
        
        # CORS 헤더 설정
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        response.headers['Access-Control-Max-Age'] = '86400'
        response.headers['Access-Control-Expose-Headers'] = '*'
        
        # Vercel 환경에서 추가 헤더
        if is_vercel:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # 디버깅을 위한 로깅
        if request.method == 'OPTIONS':
            logger.debug(f"CORS Preflight Request - Origin: {origin}, Method: {request.method}")
            logger.debug(f"Preflight Response Headers: {dict(response.headers)}")
        else:
            logger.debug(f"CORS Request - Origin: {origin}, Method: {request.method}, Path: {request.path}")
        
        return response

def add_cors_headers(response):
    """응답에 CORS 헤더 추가 (모든 환경에서 사용)"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
    response.headers['Access-Control-Allow-Credentials'] = 'false'
    return response 