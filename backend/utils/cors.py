from flask import request
import os

def setup_cors(app):
    """Vercel 환경에서만 사용되는 고급 CORS 설정"""
    from flask_cors import CORS
    
    # Vercel 환경인지 확인
    is_vercel = 'vercel.app' in os.environ.get('VERCEL_URL', '') or os.environ.get('VERCEL') == '1'
    
    if not is_vercel:
        print("🌐 로컬 환경이므로 고급 CORS 설정을 건너뜁니다.")
        return
    
    print("🌐 Vercel 환경에서 고급 CORS 설정을 적용합니다.")
    
    # CORS 설정 - 필요한 URL만 포함
    cors_origins = [
        'http://localhost:3000',  # 개발 환경
        'https://frontend-alpha-ten-pi.vercel.app',  # 현재 프론트엔드 URL
        'https://frontend-alpha-jade-15.vercel.app',  # 이전 프론트엔드 URL
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
        if is_vercel:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # 디버깅을 위한 로깅 (Vercel 환경에서만)
        if is_vercel:
            if request.method == 'OPTIONS':
                print(f"🌐 CORS Preflight Request - Origin: {origin}, Method: {request.method}")
                print(f"🔧 Preflight Response Headers: {dict(response.headers)}")
            else:
                print(f"🌐 CORS Request - Origin: {origin}, Method: {request.method}, Path: {request.path}")
        
        return response

def add_cors_headers(response):
    """응답에 CORS 헤더 추가 (Vercel 환경에서만 사용)"""
    # Vercel 환경인지 확인
    is_vercel = 'vercel.app' in os.environ.get('VERCEL_URL', '') or os.environ.get('VERCEL') == '1'
    
    if not is_vercel:
        return response
    
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
    response.headers['Access-Control-Allow-Credentials'] = 'false'
    return response 