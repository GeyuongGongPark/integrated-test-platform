from functools import wraps
from flask import jsonify, request
from .logger import get_logger

logger = get_logger(__name__)

class APIError(Exception):
    """API 에러를 위한 커스텀 예외 클래스"""
    def __init__(self, message, status_code=500, error_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

def handle_api_error(error):
    """API 에러 핸들러"""
    if isinstance(error, APIError):
        response = {
            'error': error.message,
            'error_code': error.error_code,
            'status_code': error.status_code
        }
        if error.details:
            response['details'] = error.details
        
        logger.error(f"API Error: {error.message} (Code: {error.error_code}, Status: {error.status_code})")
        return jsonify(response), error.status_code
    
    # 예상치 못한 에러
    logger.error(f"Unexpected error: {str(error)}", exc_info=True)
    return jsonify({
        'error': '내부 서버 오류가 발생했습니다.',
        'error_code': 'INTERNAL_ERROR',
        'status_code': 500
    }), 500

def safe_api_call(f):
    """API 함수를 안전하게 실행하는 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            return handle_api_error(e)
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'error': '요청을 처리하는 중 오류가 발생했습니다.',
                'error_code': 'PROCESSING_ERROR',
                'status_code': 500
            }), 500
    return decorated_function

def validate_required_fields(data, required_fields):
    """필수 필드 검증"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise APIError(
            f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}",
            status_code=400,
            error_code='MISSING_REQUIRED_FIELDS',
            details={'missing_fields': missing_fields}
        )

def validate_data_types(data, field_types):
    """데이터 타입 검증"""
    type_errors = []
    for field, expected_type in field_types.items():
        if field in data and not isinstance(data[field], expected_type):
            type_errors.append(f"{field} (예상: {expected_type.__name__}, 실제: {type(data[field]).__name__})")
    
    if type_errors:
        raise APIError(
            f"데이터 타입이 올바르지 않습니다: {', '.join(type_errors)}",
            status_code=400,
            error_code='INVALID_DATA_TYPE',
            details={'type_errors': type_errors}
        )

def log_api_request(f):
    """API 요청을 로깅하는 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"API Request: {request.method} {request.path} - User: {request.headers.get('Authorization', 'Guest')}")
        try:
            result = f(*args, **kwargs)
            logger.info(f"API Response: {request.method} {request.path} - Success")
            return result
        except Exception as e:
            logger.error(f"API Response: {request.method} {request.path} - Error: {str(e)}")
            raise
    return decorated_function
