"""
Rate Limiting 유틸리티
Flask-Limiter를 사용한 API 요청 제한
"""
from functools import wraps
from flask import request, jsonify
from utils.logger import get_logger
import time
from collections import defaultdict

logger = get_logger(__name__)

# 간단한 메모리 기반 Rate Limiter (프로덕션에서는 Redis 사용 권장)
_rate_limit_store = defaultdict(list)

def rate_limit(max_requests=100, window_seconds=60):
    """
    간단한 Rate Limiting 데코레이터
    
    Args:
        max_requests: 시간 윈도우 내 최대 요청 수
        window_seconds: 시간 윈도우 (초)
    
    사용 예:
        @rate_limit(max_requests=10, window_seconds=60)
        @app.route('/api/endpoint')
        def my_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 클라이언트 IP 주소 가져오기
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if client_ip:
                client_ip = client_ip.split(',')[0].strip()
            else:
                client_ip = 'unknown'
            
            current_time = time.time()
            
            # 오래된 요청 기록 제거
            _rate_limit_store[client_ip] = [
                req_time for req_time in _rate_limit_store[client_ip]
                if current_time - req_time < window_seconds
            ]
            
            # 요청 수 확인
            if len(_rate_limit_store[client_ip]) >= max_requests:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return jsonify({
                    'error': 'Too many requests',
                    'message': f'요청 한도를 초과했습니다. {window_seconds}초 후 다시 시도해주세요.',
                    'retry_after': window_seconds
                }), 429
            
            # 요청 기록 추가
            _rate_limit_store[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# 프로덕션 환경에서는 Flask-Limiter 사용 권장
# 설치: pip install flask-limiter
# 사용 예:
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# 
# limiter = Limiter(
#     app=app,
#     key_func=get_remote_address,
#     default_limits=["200 per day", "50 per hour"],
#     storage_uri="redis://localhost:6379"
# )
# 
# @app.route('/api/endpoint')
# @limiter.limit("10 per minute")
# def my_endpoint():
#     ...

