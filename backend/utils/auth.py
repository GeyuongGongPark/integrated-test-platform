from functools import wraps
from flask import jsonify
from models import User

# 권한 데코레이터 함수
def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 실제 구현에서는 현재 로그인한 사용자 정보를 가져와야 함
            # 여기서는 임시로 Administrator 권한을 가진 사용자로 가정
            current_user = User.query.filter_by(username='admin').first()
            if not current_user or not current_user.has_permission(permission):
                return jsonify({'error': '권한이 없습니다.'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator 