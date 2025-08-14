from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, User, UserSession
from datetime import datetime, timedelta
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """사용자 회원가입"""
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

@auth_bp.route('/login', methods=['POST'])
def login():
    """사용자 로그인"""
    try:
        print("🔐 로그인 시도 시작")
        data = request.get_json()
        print(f"📝 받은 데이터: {data}")
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '사용자명과 비밀번호를 입력해주세요.'}), 400
        
        print(f"👤 사용자명: {username}")
        
        # 사용자 조회
        user = User.query.filter_by(username=username).first()
        print(f"🔍 사용자 조회 결과: {user}")
        
        if not user:
            return jsonify({'error': '사용자명 또는 비밀번호가 올바르지 않습니다.'}), 400
        
        if not user.check_password(password):
            return jsonify({'error': '사용자명 또는 비밀번호가 올바르지 않습니다.'}), 400
        
        if not user.is_active:
            return jsonify({'error': '비활성화된 계정입니다.'}), 400
        
        print(f"✅ 비밀번호 검증 성공")
        
        # JWT 토큰 생성 (identity는 문자열이어야 함)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        print(f"🎫 JWT 토큰 생성 완료")
        
        try:
            # 세션 정보 저장
            session = UserSession(
                user_id=user.id,
                session_token=refresh_token,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            db.session.add(session)
            print(f"💾 세션 정보 저장 완료")
            
            # 마지막 로그인 시간 업데이트
            user.last_login = datetime.utcnow()
            db.session.commit()
            print(f"✅ 데이터베이스 커밋 완료")
            
        except Exception as session_error:
            print(f"⚠️ 세션 저장 중 오류: {session_error}")
            db.session.rollback()
            # 세션 저장 실패해도 로그인은 성공
        
        return jsonify({
            'message': '로그인이 성공했습니다.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
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

@auth_bp.route('/guest', methods=['POST'])
def guest_login():
    """게스트 로그인"""
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
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
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
        current_user_id = get_jwt_identity()
        
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
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'last_login': None
            }
            return jsonify(guest_user), 200
        
        # 일반 사용자 처리
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        return jsonify(user.to_dict()), 200
        
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
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 500
