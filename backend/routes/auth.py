from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, User, UserSession
from datetime import datetime, timedelta
from utils.timezone_utils import get_kst_now, get_kst_isoformat
from utils.logger import get_logger
import secrets
import os

logger = get_logger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """사용자 회원가입"""
    # OPTIONS 요청 처리 (CORS preflight)
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response, 200
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}는 필수입니다.'}), 400
        
        # 사용자명 중복 확인
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '이미 사용 중인 사용자명입니다.'}), 400
        
        # 이메일 중복 확인
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '이미 사용 중인 이메일입니다.'}), 400
        
        # 비밀번호 강도 검증
        if len(data['password']) < 8:
            return jsonify({'error': '비밀번호는 최소 8자 이상이어야 합니다.'}), 400
        
        # 사용자 생성
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '회원가입이 완료되었습니다.',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '회원가입 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """사용자 로그인"""
    # OPTIONS 요청 처리 (CORS preflight)
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response, 200
    
    try:
        logger.info("로그인 시도 시작")
        data = request.get_json()
        logger.debug(f"받은 데이터: {data}")
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '사용자명과 비밀번호를 입력해주세요.'}), 400
        
        logger.debug(f"사용자명: {username}")
        
        # 사용자 조회
        user = User.query.filter_by(username=username).first()
        logger.debug(f"사용자 조회 결과: {user}")
        
        if not user:
            return jsonify({'error': '사용자명 또는 비밀번호가 올바르지 않습니다.'}), 400
        
        if not user.check_password(password):
            return jsonify({'error': '사용자명 또는 비밀번호가 올바르지 않습니다.'}), 400
        
        if not user.is_active:
            return jsonify({'error': '비활성화된 계정입니다.'}), 400
        
        print(f"✅ 비밀번호 검증 성공")
        
        # 마지막 로그인 시간 업데이트 (먼저 처리)
        print(f"🕐 last_login 업데이트 전: {user.last_login}")
        print(f"🌍 현재 환경: {'Vercel' if 'vercel.app' in request.host_url else 'Local'}")
        print(f"🗄️ 데이터베이스 URL: {current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not Set')[:50]}...")
        
        user.last_login = get_kst_now()
        print(f"🕐 last_login 업데이트 후: {user.last_login}")
        
        # JWT 토큰 생성 (identity는 문자열이어야 함)
        print(f"🆔 토큰 생성 전 사용자 ID: {user.id}, 타입: {type(user.id)}")
        print(f"🔑 토큰 생성 시 JWT_SECRET_KEY: {current_app.config.get('JWT_SECRET_KEY', 'Not Set')}")
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        print(f"🎫 JWT 토큰 생성 완료")
        print(f"🔑 Access Token (첫 50자): {access_token[:50]}...")
        print(f"🔑 Refresh Token (첫 50자): {refresh_token[:50]}...")
        
        try:
            # 세션 정보 저장
            session = UserSession(
                user_id=user.id,
                session_token=refresh_token,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                expires_at=get_kst_now() + timedelta(days=7)
            )
            db.session.add(session)
            print(f"💾 세션 정보 저장 완료")
            
        except Exception as session_error:
            print(f"⚠️ 세션 저장 중 오류: {session_error}")
            # 세션 저장 실패해도 계속 진행
        
        # last_login 업데이트와 커밋을 try 밖에서 처리
        try:
            # 데이터베이스 테이블 구조 확인
            try:
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                columns = inspector.get_columns('Users')
                last_login_exists = any(col['name'] == 'last_login' for col in columns)
                print(f"🔍 Users 테이블 last_login 컬럼 존재: {last_login_exists}")
                if last_login_exists:
                    for col in columns:
                        if col['name'] == 'last_login':
                            print(f"🔍 last_login 컬럼 타입: {col['type']}, nullable: {col.get('nullable', 'unknown')}")
            except Exception as inspect_error:
                print(f"⚠️ 테이블 구조 확인 실패: {inspect_error}")
            
            db.session.commit()
            print(f"✅ 데이터베이스 커밋 완료")
            print(f"🕐 커밋 후 last_login 확인: {user.last_login}")
            
            # 세션 커밋 후 user 객체 새로고침
            db.session.refresh(user)
            print(f"🔄 새로고침 후 last_login: {user.last_login}")
            
            # 데이터베이스에서 직접 확인
            db_user = User.query.get(user.id)
            print(f"🗄️ DB에서 직접 조회한 last_login: {db_user.last_login}")
            
        except Exception as commit_error:
            print(f"⚠️ 커밋 중 오류: {commit_error}")
            db.session.rollback()
            # 롤백 후 최소한 last_login만이라도 업데이트
            try:
                user.last_login = get_kst_now()
                db.session.commit()
                print(f"🔄 last_login만 다시 업데이트 완료")
            except Exception as e:
                print(f"❌ last_login 업데이트 실패: {e}")
                db.session.rollback()
        
        # 응답용 사용자 데이터 생성 (last_login 포함)
        user_response = user.to_dict()
        print(f"📤 응답용 사용자 데이터 last_login: {user_response.get('last_login')}")
        
        return jsonify({
            'message': '로그인이 성공했습니다.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_response
        }), 200
        
    except Exception as e:
        print(f"❌ 로그인 중 오류 발생: {str(e)}")
        print(f"🔍 오류 타입: {type(e)}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
        return jsonify({'error': f'로그인 중 오류가 발생했습니다: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """액세스 토큰 갱신"""
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': '토큰 갱신 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/guest', methods=['POST', 'OPTIONS'])
def guest_login():
    """게스트 로그인"""
    # OPTIONS 요청 처리 (CORS preflight)
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response, 200
    
    try:
        print("🎭 게스트 로그인 시도")
        
        # 게스트 사용자 생성 (임시)
        guest_user = {
            'id': 'guest',
            'username': 'guest',
            'email': 'guest@test.com',
            'first_name': '게스트',
            'last_name': '사용자',
            'role': 'guest',
            'is_active': True,
            'created_at': get_kst_now().isoformat(),
            'updated_at': get_kst_now().isoformat(),
            'last_login': None
        }
        
        # 게스트용 JWT 토큰 생성 (짧은 유효기간)
        access_token = create_access_token(
            identity='guest',
            expires_delta=timedelta(hours=2)  # 2시간만 유효
        )
        
        print(f"🎫 게스트 토큰 생성 완료")
        
        return jsonify({
            'access_token': access_token,
            'user': guest_user,
            'message': '게스트 로그인 성공'
        }), 200
        
    except Exception as e:
        print(f"❌ 게스트 로그인 중 오류 발생: {str(e)}")
        return jsonify({'error': f'게스트 로그인 중 오류가 발생했습니다: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """사용자 로그아웃"""
    try:
        current_user_id = get_jwt_identity()
        
        # 게스트 사용자는 세션 정보가 없으므로 건너뛰기
        if current_user_id != 'guest':
            user = User.query.get(int(current_user_id))
            if user:
                # 세션 비활성화
                UserSession.query.filter_by(
                    user_id=current_user_id,
                    is_active=True
                ).update({'is_active': False})
                
                db.session.commit()
        
        return jsonify({'message': '로그아웃이 완료되었습니다.'}), 200
        
    except Exception as e:
        return jsonify({'error': '로그아웃 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """사용자 프로필 조회"""
    try:
        print("🔍 프로필 조회 시작")
        print(f"📋 Authorization 헤더: {request.headers.get('Authorization', 'None')}")
        print(f"🔑 환경변수 JWT_SECRET_KEY: {os.environ.get('JWT_SECRET_KEY', 'Not Set')}")
        print(f"🔑 Flask 앱 JWT_SECRET_KEY: {current_app.config.get('JWT_SECRET_KEY', 'Not Set')}")
        
        current_user_id = get_jwt_identity()
        print(f"🆔 JWT에서 추출한 사용자 ID: {current_user_id}")
        print(f"🆔 사용자 ID 타입: {type(current_user_id)}")
        
        # 게스트 사용자 처리
        if current_user_id == 'guest':
            guest_user = {
                'id': 'guest',
                'username': 'guest',
                'email': 'guest@test.com',
                'first_name': '게스트',
                'last_name': '사용자',
                'role': 'guest',
                'is_active': True,
                'created_at': get_kst_now().isoformat(),
                'updated_at': get_kst_now().isoformat(),
                'last_login': None
            }
            return jsonify(guest_user), 200
        
        # 일반 사용자 처리
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        user_dict = user.to_dict()
        print(f"👤 프로필 조회 - 사용자 ID: {current_user_id}")
        print(f"🕐 last_login 값: {user_dict.get('last_login')}")
        print(f"📅 created_at 값: {user_dict.get('created_at')}")
        
        return jsonify(user_dict), 200
        
    except Exception as e:
        return jsonify({'error': '프로필 조회 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """사용자 프로필 수정"""
    try:
        current_user_id = get_jwt_identity()
        # JWT identity는 문자열이므로 정수로 변환
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        data = request.get_json()
        
        # 수정 가능한 필드들
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        db.session.commit()
        
        return jsonify({'message': '프로필이 수정되었습니다.'}), 200
        
    except Exception as e:
        return jsonify({'error': '프로필 수정 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """비밀번호 변경"""
    try:
        current_user_id = get_jwt_identity()
        # JWT identity는 문자열이므로 정수로 변환
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': '현재 비밀번호와 새 비밀번호를 입력해주세요.'}), 400
        
        if not user.check_password(current_password):
            return jsonify({'error': '현재 비밀번호가 올바르지 않습니다.'}), 400
        
        if len(new_password) < 8:
            return jsonify({'error': '새 비밀번호는 최소 8자 이상이어야 합니다.'}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': '비밀번호가 변경되었습니다.'}), 200
        
    except Exception as e:
        return jsonify({'error': '비밀번호 변경 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 데이터베이스 연결 확인
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'timestamp': get_kst_now().isoformat(),
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': get_kst_now().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 500
