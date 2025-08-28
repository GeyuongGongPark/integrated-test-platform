from flask import jsonify
from .logger import get_logger

logger = get_logger(__name__)

def success_response(data=None, message="성공적으로 처리되었습니다.", status_code=200):
    """성공 응답 생성"""
    response = {
        'success': True,
        'message': message,
        'status_code': status_code
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def error_response(message="오류가 발생했습니다.", error_code=None, status_code=500, details=None):
    """에러 응답 생성"""
    response = {
        'success': False,
        'message': message,
        'status_code': status_code
    }
    
    if error_code:
        response['error_code'] = error_code
    
    if details:
        response['details'] = details
    
    logger.error(f"Error Response: {message} (Code: {error_code}, Status: {status_code})")
    return jsonify(response), status_code

def paginated_response(data, page, per_page, total, message="데이터를 성공적으로 조회했습니다."):
    """페이지네이션 응답 생성"""
    response = {
        'success': True,
        'message': message,
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_next': page * per_page < total,
            'has_prev': page > 1
        }
    }
    
    return jsonify(response), 200

def list_response(data, message="목록을 성공적으로 조회했습니다."):
    """리스트 응답 생성"""
    return success_response(
        data=data,
        message=message
    )

def single_response(data, message="데이터를 성공적으로 조회했습니다."):
    """단일 데이터 응답 생성"""
    return success_response(
        data=data,
        message=message
    )

def created_response(data, message="성공적으로 생성되었습니다."):
    """생성 성공 응답"""
    return success_response(
        data=data,
        message=message,
        status_code=201
    )

def updated_response(data, message="성공적으로 수정되었습니다."):
    """수정 성공 응답"""
    return success_response(
        data=data,
        message=message
    )

def deleted_response(message="성공적으로 삭제되었습니다."):
    """삭제 성공 응답"""
    return success_response(
        message=message
    )

def not_found_response(message="요청한 리소스를 찾을 수 없습니다."):
    """리소스 없음 응답"""
    return error_response(
        message=message,
        error_code='RESOURCE_NOT_FOUND',
        status_code=404
    )

def validation_error_response(message="입력 데이터가 올바르지 않습니다.", details=None):
    """검증 오류 응답"""
    return error_response(
        message=message,
        error_code='VALIDATION_ERROR',
        status_code=400,
        details=details
    )

def unauthorized_response(message="인증이 필요합니다."):
    """인증 필요 응답"""
    return error_response(
        message=message,
        error_code='UNAUTHORIZED',
        status_code=401
    )

def forbidden_response(message="접근 권한이 없습니다."):
    """접근 거부 응답"""
    return error_response(
        message=message,
        error_code='FORBIDDEN',
        status_code=403
    )
