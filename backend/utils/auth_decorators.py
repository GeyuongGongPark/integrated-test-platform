from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt
from models import User

def admin_required(fn):
    """관리자 권한 확인 데코레이터"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # 게스트 사용자 체크
            if current_user_id == 'guest':
                return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
            
            user = User.query.get(int(current_user_id))
            
            if not user or user.role != 'admin':
                return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
            
            return fn(*args, **kwargs)
        except Exception:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
    return wrapper

def user_required(fn):
    """일반 사용자 권한 확인 데코레이터 (admin, user)"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            print(f"🔐 user_required 데코레이터 실행 - 요청 URL: {request.url}")
            print(f"🔑 Authorization 헤더: {request.headers.get('Authorization', '없음')}")
            
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            print(f"✅ JWT 검증 성공 - 사용자 ID: {current_user_id}")
            
            # 게스트 사용자 체크
            if current_user_id == 'guest':
                print(f"❌ 게스트 사용자는 접근 불가")
                return jsonify({'error': '사용자 권한이 필요합니다.'}), 403
            
            user = User.query.get(int(current_user_id))
            print(f"👤 데이터베이스에서 사용자 조회: {user}")
            
            if not user or user.role not in ['admin', 'user']:
                print(f"❌ 사용자 권한 부족: {user.role if user else '사용자 없음'}")
                return jsonify({'error': '사용자 권한이 필요합니다.'}), 403
            
            print(f"✅ 사용자 권한 확인 완료: {user.username} ({user.role})")
            # request.user에 사용자 정보 저장 (routes에서 사용)
            request.user = user
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"🚨 user_required 데코레이터 오류: {str(e)}")
            print(f"🔍 오류 타입: {type(e).__name__}")
            return jsonify({'error': '로그인이 필요합니다.'}), 401
    return wrapper

def guest_allowed(fn):
    """게스트 사용자도 허용하는 데코레이터 (모든 사용자)"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # 게스트 사용자 체크
            if current_user_id == 'guest':
                return fn(*args, **kwargs)
            
            user = User.query.get(int(current_user_id))
            
            if not user or not user.is_active:
                return jsonify({'error': '유효하지 않은 사용자입니다.'}), 401
            
            return fn(*args, **kwargs)
        except Exception:
            # JWT 토큰이 없어도 게스트로 간주하고 허용
            return fn(*args, **kwargs)
    return wrapper

def role_required(allowed_roles):
    """특정 역할 권한 확인 데코레이터"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                # 게스트 사용자 체크
                if current_user_id == 'guest':
                    if 'guest' not in allowed_roles:
                        return jsonify({'error': '접근 권한이 없습니다.'}), 403
                    return fn(*args, **kwargs)
                
                user = User.query.get(int(current_user_id))
                
                if not user or user.role not in allowed_roles:
                    return jsonify({'error': '접근 권한이 없습니다.'}), 403
                
                return fn(*args, **kwargs)
            except Exception:
                # JWT 토큰이 없고 guest가 허용된 역할이면 통과
                if 'guest' in allowed_roles:
                    return fn(*args, **kwargs)
                return jsonify({'error': '로그인이 필요합니다.'}), 401
        return wrapper
    return decorator

def login_required(fn):
    """로그인 필요 데코레이터 (JWT 토큰 검증)"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # 게스트 사용자 체크
            if current_user_id == 'guest':
                return fn(*args, **kwargs)
            
            user = User.query.get(int(current_user_id))
            
            if not user or not user.is_active:
                return jsonify({'error': '로그인이 필요합니다.'}), 401
            
            return fn(*args, **kwargs)
        except Exception:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
    return wrapper

def owner_required(fn):
    """소유자 권한 확인 데코레이터 (자신의 데이터만 수정 가능)"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # 게스트 사용자는 소유자 권한 없음
            if current_user_id == 'guest':
                return jsonify({'error': '소유자 권한이 필요합니다.'}), 403
            
            user = User.query.get(int(current_user_id))
            
            if not user or not user.is_active:
                return jsonify({'error': '유효하지 않은 사용자입니다.'}), 401
            
            # admin은 모든 데이터에 접근 가능
            if user.role == 'admin':
                return fn(*args, **kwargs)
            
            # user는 자신의 데이터만 접근 가능
            # URL 파라미터에서 user_id나 creator_id를 확인
            request_data = request.get_json() or {}
            url_user_id = request.view_args.get('user_id')
            creator_id = request_data.get('creator_id')
            
            if url_user_id and int(url_user_id) != user.id:
                return jsonify({'error': '자신의 데이터만 수정할 수 있습니다.'}), 403
            
            if creator_id and int(creator_id) != user.id:
                return jsonify({'error': '자신의 데이터만 수정할 수 있습니다.'}), 403
            
            return fn(*args, **kwargs)
        except Exception:
            return jsonify({'error': '로그인이 필요합니다.'}), 401
    return wrapper
