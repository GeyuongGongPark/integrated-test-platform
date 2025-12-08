"""
JWT 콜백 함수들
"""
from flask import jsonify, request
from utils.logger import get_logger

logger = get_logger(__name__)

def setup_jwt_callbacks(jwt):
    """JWT 콜백 함수들 설정"""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"토큰 만료: header={jwt_header}, payload={jwt_payload}")
        return jsonify({
            'message': '토큰이 만료되었습니다.',
            'error': 'token_expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"유효하지 않은 토큰: {error}")
        return jsonify({
            'message': '유효하지 않은 토큰입니다.',
            'error': 'invalid_token'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.warning(f"토큰 누락: {error}")
        logger.debug(f"요청 헤더: {dict(request.headers)}")
        logger.debug(f"요청 URL: {request.url}")
        logger.debug(f"요청 메서드: {request.method}")
        return jsonify({
            'message': '토큰이 필요합니다.',
            'error': 'authorization_required'
        }), 401
    
    return jwt

