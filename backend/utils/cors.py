from flask import request
import os

def setup_cors(app):
    """CORS 설정을 위한 함수"""
    from flask_cors import CORS
    
    # CORS 설정 - 필요한 URL만 포함
    cors_origins = [
        'http://localhost:3000',  # 개발 환경
        'https://frontend-alpha-jade-15.vercel.app',  # 현재 프론트엔드 URL
        # Vercel URL 패턴 (와일드카드로 대체)
        'https://*.vercel.app'
    ]
    
    # 환경 변수에서 추가 CORS 설정 가져오기
    env_cors = os.environ.get('CORS_ORIGINS', '')
    if env_cors:
        cors_origins.extend(env_cors.split(','))
    
    print(f"🌐 CORS Origins: {cors_origins}")
    
    # CORS 설정 - 명시적 헤더 설정
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
        
        # 모든 Origin 허용 (더 구체적으로 설정)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = '*'
        
        # CORS 헤더 설정
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Access-Control-Allow-Origin'
        response.headers['Access-Control-Allow-Credentials'] = 'false'
        response.headers['Access-Control-Max-Age'] = '86400'
        response.headers['Access-Control-Expose-Headers'] = '*'
        
        # Vercel 환경에서 추가 헤더
        if os.environ.get('VERCEL'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # 디버깅을 위한 로깅
        if request.method == 'OPTIONS':
            print(f"🌐 CORS Preflight Request - Origin: {origin}, Method: {request.method}")
            print(f"🔧 Preflight Response Headers: {dict(response.headers)}")
        else:
            print(f"🌐 CORS Request - Origin: {origin}, Method: {request.method}, Path: {request.path}")
        
        return response

def add_cors_headers(response):
    """응답에 CORS 헤더 추가"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
    response.headers['Access-Control-Allow-Credentials'] = 'false'
    return response 