from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, User, UserSession
from datetime import datetime, timedelta
from utils.timezone_utils import get_kst_now, get_kst_isoformat
from utils.logger import get_logger
from utils.response_utils import (
    success_response, error_response, created_response, 
    validation_error_response, unauthorized_response, 
    not_found_response, forbidden_response
)
from utils.cors_helpers import handle_options_request, create_cors_response
from utils.auth_constants import MESSAGES, MIN_PASSWORD_LENGTH, ROLE_GUEST
from utils.auth_helpers import (
    create_user_session, create_tokens, create_guest_tokens,
    get_guest_user_data, validate_user_credentials, 
    update_user_last_login, deactivate_user_sessions
)
import secrets
import os

logger = get_logger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """사용자 회원가입
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
            first_name:
              type: string
            last_name:
              type: string
            role:
              type: string
          required:
            - username
            - email
            - password
    responses:
      201:
        description: 회원가입 성공
      400:
        description: 유효하지 않은 요청
    """
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        validation_error = validate_registration_data(data)
        if validation_error:
            return validation_error_response(validation_error)
        
        # 사용자 생성
        user = create_new_user(data)
        db.session.add(user)
        db.session.commit()
        
        return created_response(
            data={'user_id': user.id},
            message=MESSAGES['REGISTER_SUCCESS']
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"회원가입 오류: {str(e)}")
        return error_response('회원가입 중 오류가 발생했습니다.')

def validate_registration_data(data):
    """회원가입 데이터 검증"""
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return f'{field}는 필수입니다.'
    
    # 사용자명 중복 확인
    if User.query.filter_by(username=data['username']).first():
        return MESSAGES['USERNAME_EXISTS']
    
    # 이메일 중복 확인
    if User.query.filter_by(email=data['email']).first():
        return MESSAGES['EMAIL_EXISTS']
    
    # 비밀번호 강도 검증
    if len(data['password']) < MIN_PASSWORD_LENGTH:
        return MESSAGES['PASSWORD_TOO_SHORT']
    
    return None

def create_new_user(data):
    """새 사용자 생성"""
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        role=data.get('role', 'user')
    )
    user.set_password(data['password'])
    return user

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """사용자 로그인
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
          required:
            - username
            - password
    responses:
      200:
        description: 로그인 성공 및 토큰 반환
      401:
        description: 인증 실패
    """
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    try:
        logger.info("로그인 시도 시작")
        data = request.get_json()
        
        # 입력 데이터 검증
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return validation_error_response(MESSAGES['REQUIRED_FIELDS'])
        
        # 사용자 인증
        user, error_message = validate_user_credentials(username, password)
        if error_message:
            return unauthorized_response(error_message)
        
        # 마지막 로그인 시간 업데이트
        if not update_user_last_login(user):
            logger.warning("마지막 로그인 시간 업데이트 실패, 계속 진행")
        
        # JWT 토큰 생성
        access_token, refresh_token = create_tokens(user.id)
        
        # 세션 정보 저장 (실패해도 계속 진행)
        create_user_session(user.id, refresh_token, request)
        
        # 응답 데이터 생성
        user_response = user.to_dict()
        
        return success_response(
            data={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_response
            },
            message=MESSAGES['LOGIN_SUCCESS']
        )
        
    except Exception as e:
        logger.error(f"로그인 중 오류 발생: {str(e)}")
        return error_response('로그인 중 오류가 발생했습니다.')

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """액세스 토큰 갱신
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    responses:
      200:
        description: 새 액세스 토큰 반환
      401:
        description: 인증 실패
    """
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        
        return success_response(
            data={'access_token': new_access_token},
            message=MESSAGES['TOKEN_REFRESH_SUCCESS']
        )
        
    except Exception as e:
        logger.error(f"토큰 갱신 오류: {str(e)}")
        return error_response('토큰 갱신 중 오류가 발생했습니다.')

@auth_bp.route('/guest', methods=['POST', 'OPTIONS'])
def guest_login():
    """게스트 로그인
    ---
    tags:
      - Auth
    responses:
      200:
        description: 게스트 토큰 반환
    """
    if request.method == 'OPTIONS':
        return handle_options_request()
    
    try:
        logger.info("게스트 로그인 시도")
        
        # 게스트 사용자 데이터 생성
        guest_user = get_guest_user_data()
        
        # 게스트용 JWT 토큰 생성
        access_token = create_guest_tokens()
        
        logger.info("게스트 로그인 성공")
        
        return success_response(
            data={
                'access_token': access_token,
                'user': guest_user
            },
            message='게스트 로그인 성공'
        )
        
    except Exception as e:
        logger.error(f"게스트 로그인 중 오류 발생: {str(e)}")
        return error_response(f'게스트 로그인 중 오류가 발생했습니다: {str(e)}')

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """사용자 로그아웃"""
    try:
        current_user_id = get_jwt_identity()
        
        # 게스트 사용자가 아닌 경우에만 세션 비활성화
        if current_user_id != ROLE_GUEST:
            deactivate_user_sessions(int(current_user_id))
        
        return success_response(message=MESSAGES['LOGOUT_SUCCESS'])
        
    except Exception as e:
        logger.error(f"로그아웃 중 오류 발생: {str(e)}")
        return error_response('로그아웃 중 오류가 발생했습니다.')

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """사용자 프로필 조회"""
    try:
        logger.info("프로필 조회 시작")
        current_user_id = get_jwt_identity()
        
        # 게스트 사용자 처리
        if current_user_id == ROLE_GUEST:
            guest_user = get_guest_user_data()
            return success_response(data=guest_user)
        
        # 일반 사용자 처리
        user = User.query.get(int(current_user_id))
        
        if not user:
            return not_found_response(MESSAGES['USER_NOT_FOUND'])
        
        user_dict = user.to_dict()
        logger.info(f"프로필 조회 완료 - 사용자 ID: {current_user_id}")
        
        return success_response(data=user_dict)
        
    except Exception as e:
        logger.error(f"프로필 조회 중 오류 발생: {str(e)}")
        return error_response('프로필 조회 중 오류가 발생했습니다.')

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """사용자 프로필 수정"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        if not user:
            return not_found_response(MESSAGES['USER_NOT_FOUND'])
        
        data = request.get_json()
        
        # 수정 가능한 필드들 업데이트
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        db.session.commit()
        
        return success_response(message=MESSAGES['PROFILE_UPDATE_SUCCESS'])
        
    except Exception as e:
        logger.error(f"프로필 수정 중 오류 발생: {str(e)}")
        return error_response('프로필 수정 중 오류가 발생했습니다.')

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """비밀번호 변경"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        if not user:
            return not_found_response(MESSAGES['USER_NOT_FOUND'])
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # 입력 검증
        if not current_password or not new_password:
            return validation_error_response(MESSAGES['NEW_PASSWORD_REQUIRED'])
        
        if not user.check_password(current_password):
            return validation_error_response(MESSAGES['CURRENT_PASSWORD_INVALID'])
        
        if len(new_password) < MIN_PASSWORD_LENGTH:
            return validation_error_response(MESSAGES['PASSWORD_TOO_SHORT'])
        
        # 비밀번호 변경
        user.set_password(new_password)
        db.session.commit()
        
        return success_response(message=MESSAGES['PASSWORD_CHANGE_SUCCESS'])
        
    except Exception as e:
        logger.error(f"비밀번호 변경 중 오류 발생: {str(e)}")
        return error_response('비밀번호 변경 중 오류가 발생했습니다.')

@auth_bp.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 데이터베이스 연결 확인
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        return success_response(
            data={
                'status': 'healthy',
                'timestamp': get_kst_now().isoformat(),
                'database': 'connected'
            }
        )
    except Exception as e:
        logger.error(f"헬스 체크 실패: {str(e)}")
        return error_response(
            data={
                'status': 'unhealthy',
                'timestamp': get_kst_now().isoformat(),
                'database': 'disconnected',
                'error': str(e)
            }
        )
