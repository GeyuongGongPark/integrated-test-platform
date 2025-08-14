# 🔐 인증 시스템 구현 계획서

## 📋 개요

통합 테스트 플랫폼에 사용자 인증 시스템을 구축하여 개인화된 테스트 환경과 보안을 제공합니다. JWT 기반의 토큰 인증과 사용자 권한 관리 시스템을 포함합니다.

## 🏗️ 아키텍처 설계

### 1.1 전체 시스템 구조

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (Flask)       │◄──►│   (MySQL)       │
│                 │    │                 │    │                 │
│ - 로그인/회원가입   │    │ - JWT 인증       │    │ - 사용자 정보      │
│ - 프로필 관리      │    │ - 권한 관리       │    │ - 세션 관리        │
│ - 권한별 UI       │    │ - 비밀번호 암호화│       │ - 로그 기록       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.2 인증 플로우

```
회원가입 → 이메일 인증 → 로그인 → JWT 토큰 발급 → API 요청 시 토큰 검증 → 권한 확인 → 리소스 접근
```

## 🔧 백엔드 구현 방안

### 2.1 사용자 모델 설계

```python
# backend/models.py
class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')  # admin, user, tester
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255))
    password_reset_token = db.Column(db.String(255))
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    test_cases = db.relationship('TestCase', backref='creator', lazy='dynamic')
    automation_tests = db.relationship('AutomationTest', backref='creator', lazy='dynamic')
    performance_tests = db.relationship('PerformanceTest', backref='creator', lazy='dynamic')
    
    def set_password(self, password):
        """비밀번호 해시화"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """비밀번호 검증"""
        return check_password_hash(self.password_hash, password)
    
    def generate_email_verification_token(self):
        """이메일 인증 토큰 생성"""
        self.email_verification_token = secrets.token_urlsafe(32)
        return self.email_verification_token
    
    def generate_password_reset_token(self):
        """비밀번호 재설정 토큰 생성"""
        self.password_reset_token = secrets.token_urlsafe(32)
        return self.password_reset_token

class UserSession(db.Model):
    __tablename__ = 'UserSessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', backref='sessions')
```

### 2.2 환경 변수 설정

```bash
# .env
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1시간
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7일
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
FRONTEND_URL=http://localhost:3000
```

### 2.3 JWT 설정

```python
# backend/config.py
class Config:
    # 기존 설정...
    
    # JWT 설정
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 604800)))
    
    # 이메일 설정
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # 프론트엔드 URL
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
```

### 2.4 이메일 유틸리티

```python
# backend/utils/email_service.py
from flask_mail import Mail, Message
from flask import current_app, render_template_string

mail = Mail()

class EmailService:
    @staticmethod
    def send_verification_email(user):
        """이메일 인증 메일 발송"""
        try:
            verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={user.email_verification_token}"
            
            html_content = render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>이메일 인증</title>
            </head>
            <body>
                <h2>🎉 통합 테스트 플랫폼 가입을 환영합니다!</h2>
                <p>안녕하세요, {{ user.username }}님!</p>
                <p>아래 버튼을 클릭하여 이메일 인증을 완료해주세요.</p>
                <a href="{{ verification_url }}" style="
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                ">이메일 인증하기</a>
                <p>버튼이 작동하지 않는 경우, 아래 링크를 복사하여 브라우저에 붙여넣기 해주세요:</p>
                <p>{{ verification_url }}</p>
                <p>감사합니다!</p>
            </body>
            </html>
            """, user=user, verification_url=verification_url)
            
            msg = Message(
                subject='[통합 테스트 플랫폼] 이메일 인증',
                recipients=[user.email],
                html=html_content
            )
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"이메일 발송 실패: {e}")
            return False
    
    @staticmethod
    def send_password_reset_email(user):
        """비밀번호 재설정 메일 발송"""
        try:
            reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={user.password_reset_token}"
            
            html_content = render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>비밀번호 재설정</title>
            </head>
            <body>
                <h2>🔐 비밀번호 재설정</h2>
                <p>안녕하세요, {{ user.username }}님!</p>
                <p>비밀번호 재설정을 요청하셨습니다.</p>
                <p>아래 버튼을 클릭하여 새 비밀번호를 설정해주세요.</p>
                <a href="{{ reset_url }}" style="
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #dc3545;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                ">비밀번호 재설정</a>
                <p>이 요청을 하지 않으셨다면, 이 메일을 무시하셔도 됩니다.</p>
                <p>감사합니다!</p>
            </body>
            </html>
            """, user=user, reset_url=reset_url)
            
            msg = Message(
                subject='[통합 테스트 플랫폼] 비밀번호 재설정',
                recipients=[user.email],
                html=html_content
            )
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"이메일 발송 실패: {e}")
            return False
```

## 🌐 API 엔드포인트 설계

### 3.1 인증 API

```python
# backend/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, UserSession
from utils.email_service import EmailService
from utils.auth_decorators import admin_required
import secrets
from datetime import datetime, timedelta

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
        user.generate_email_verification_token()
        
        db.session.add(user)
        db.session.commit()
        
        # 이메일 인증 메일 발송
        EmailService.send_verification_email(user)
        
        return jsonify({
            'message': '회원가입이 완료되었습니다. 이메일 인증을 완료해주세요.',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '회원가입 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """이메일 인증"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': '인증 토큰이 필요합니다.'}), 400
        
        user = User.query.filter_by(email_verification_token=token).first()
        
        if not user:
            return jsonify({'error': '유효하지 않은 인증 토큰입니다.'}), 400
        
        if user.is_verified:
            return jsonify({'error': '이미 인증된 이메일입니다.'}), 400
        
        user.is_verified = True
        user.email_verification_token = None
        db.session.commit()
        
        return jsonify({'message': '이메일 인증이 완료되었습니다.'}), 200
        
    except Exception as e:
        return jsonify({'error': '이메일 인증 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """사용자 로그인"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '사용자명과 비밀번호를 입력해주세요.'}), 400
        
        # 사용자 조회
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': '사용자명 또는 비밀번호가 올바르지 않습니다.'}), 400
        
        if not user.is_active:
            return jsonify({'error': '비활성화된 계정입니다.'}), 400
        
        if not user.is_verified:
            return jsonify({'error': '이메일 인증을 완료해주세요.'}), 400
        
        # JWT 토큰 생성
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # 세션 정보 저장
        session = UserSession(
            user_id=user.id,
            session_token=refresh_token,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(session)
        
        # 마지막 로그인 시간 업데이트
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '로그인이 성공했습니다.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': '로그인 중 오류가 발생했습니다.'}), 500

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

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """사용자 로그아웃"""
    try:
        current_user_id = get_jwt_identity()
        
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
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_verified': user.is_verified,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': '프로필 조회 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """사용자 프로필 수정"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
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
        user = User.query.get(current_user_id)
        
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

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """비밀번호 재설정 요청"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': '이메일을 입력해주세요.'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': '해당 이메일로 가입된 계정이 없습니다.'}), 400
        
        if not user.is_active:
            return jsonify({'error': '비활성화된 계정입니다.'}), 400
        
        # 비밀번호 재설정 토큰 생성
        user.generate_password_reset_token()
        db.session.commit()
        
        # 비밀번호 재설정 메일 발송
        EmailService.send_password_reset_email(user)
        
        return jsonify({'message': '비밀번호 재설정 메일이 발송되었습니다.'}), 200
        
    except Exception as e:
        return jsonify({'error': '비밀번호 재설정 요청 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """비밀번호 재설정"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({'error': '토큰과 새 비밀번호를 입력해주세요.'}), 400
        
        user = User.query.filter_by(password_reset_token=token).first()
        
        if not user:
            return jsonify({'error': '유효하지 않은 토큰입니다.'}), 400
        
        if len(new_password) < 8:
            return jsonify({'error': '새 비밀번호는 최소 8자 이상이어야 합니다.'}), 400
        
        user.set_password(new_password)
        user.password_reset_token = None
        db.session.commit()
        
        return jsonify({'message': '비밀번호가 재설정되었습니다.'}), 200
        
    except Exception as e:
        return jsonify({'error': '비밀번호 재설정 중 오류가 발생했습니다.'}), 500

# 관리자 전용 API
@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """사용자 목록 조회 (관리자 전용)"""
    try:
        users = User.query.all()
        user_list = []
        
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify({'users': user_list}), 200
        
    except Exception as e:
        return jsonify({'error': '사용자 목록 조회 중 오류가 발생했습니다.'}), 500

@auth_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
@admin_required
def toggle_user_status(user_id):
    """사용자 활성화/비활성화 (관리자 전용)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = '활성화' if user.is_active else '비활성화'
        return jsonify({'message': f'사용자가 {status}되었습니다.'}), 200
        
    except Exception as e:
        return jsonify({'error': '사용자 상태 변경 중 오류가 발생했습니다.'}), 500
```

### 3.2 권한 관리 데코레이터

```python
# backend/utils/auth_decorators.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User

def admin_required(fn):
    """관리자 권한 확인 데코레이터"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403
        
        return fn(*args, **kwargs)
    return wrapper

def role_required(allowed_roles):
    """특정 역할 권한 확인 데코레이터"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or user.role not in allowed_roles:
                return jsonify({'error': '접근 권한이 없습니다.'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

## 🎨 프론트엔드 구현 방안

### 4.1 인증 컨텍스트

```javascript
// frontend/src/contexts/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken'));
    const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken'));

    // axios 인터셉터 설정
    useEffect(() => {
        if (accessToken) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
        }
    }, [accessToken]);

    // 토큰 만료 시 자동 갱신
    useEffect(() => {
        if (refreshToken) {
            const tokenRefreshInterval = setInterval(refreshAccessToken, 14 * 60 * 1000); // 14분마다
            return () => clearInterval(tokenRefreshInterval);
        }
    }, [refreshToken]);

    const login = async (username, password) => {
        try {
            const response = await axios.post('/auth/login', { username, password });
            const { access_token, refresh_token, user: userData } = response.data;
            
            setAccessToken(access_token);
            setRefreshToken(refresh_token);
            setUser(userData);
            
            localStorage.setItem('accessToken', access_token);
            localStorage.setItem('refreshToken', refresh_token);
            
            axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
            
            return { success: true };
        } catch (error) {
            return { 
                success: false, 
                error: error.response?.data?.error || '로그인 중 오류가 발생했습니다.' 
            };
        }
    };

    const register = async (userData) => {
        try {
            const response = await axios.post('/auth/register', userData);
            return { success: true, message: response.data.message };
        } catch (error) {
            return { 
                success: false, 
                error: error.response?.data?.error || '회원가입 중 오류가 발생했습니다.' 
            };
        }
    };

    const logout = async () => {
        try {
            if (accessToken) {
                await axios.post('/auth/logout');
            }
        } catch (error) {
            console.error('로그아웃 중 오류:', error);
        } finally {
            setUser(null);
            setAccessToken(null);
            setRefreshToken(null);
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            delete axios.defaults.headers.common['Authorization'];
        }
    };

    const refreshAccessToken = async () => {
        try {
            const response = await axios.post('/auth/refresh', {}, {
                headers: { 'Authorization': `Bearer ${refreshToken}` }
            });
            
            const { access_token } = response.data;
            setAccessToken(access_token);
            localStorage.setItem('accessToken', access_token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        } catch (error) {
            console.error('토큰 갱신 실패:', error);
            logout();
        }
    };

    const updateProfile = async (profileData) => {
        try {
            const response = await axios.put('/auth/profile', profileData);
            setUser(prevUser => ({ ...prevUser, ...profileData }));
            return { success: true, message: response.data.message };
        } catch (error) {
            return { 
                success: false, 
                error: error.response?.data?.error || '프로필 수정 중 오류가 발생했습니다.' 
            };
        }
    };

    const changePassword = async (currentPassword, newPassword) => {
        try {
            const response = await axios.post('/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword
            });
            return { success: true, message: response.data.message };
        } catch (error) {
            return { 
                success: false, 
                error: error.response?.data?.error || '비밀번호 변경 중 오류가 발생했습니다.' 
            };
        }
    };

    const forgotPassword = async (email) => {
        try {
            const response = await axios.post('/auth/forgot-password', { email });
            return { success: true, message: response.data.message };
        } catch (error) {
            return { 
                success: false, 
                error: error.response?.data?.error || '비밀번호 재설정 요청 중 오류가 발생했습니다.' 
            };
        }
    };

    const resetPassword = async (token, newPassword) => {
        try {
            const response = await axios.post('/auth/reset-password', {
                token,
                new_password: newPassword
            });
            return { success: true, message: response.data.message };
        } catch (error) {
            return { 
                success: false, 
                error: error.response?.data?.error || '비밀번호 재설정 중 오류가 발생했습니다.' 
            };
        }
    };

    // 사용자 정보 자동 로드
    useEffect(() => {
        const loadUser = async () => {
            if (accessToken) {
                try {
                    const response = await axios.get('/auth/profile');
                    setUser(response.data);
                } catch (error) {
                    console.error('사용자 정보 로드 실패:', error);
                    logout();
                }
            }
            setLoading(false);
        };

        loadUser();
    }, [accessToken]);

    const value = {
        user,
        loading,
        login,
        register,
        logout,
        updateProfile,
        changePassword,
        forgotPassword,
        resetPassword,
        isAuthenticated: !!user,
        isAdmin: user?.role === 'admin'
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};
```

### 4.2 로그인 컴포넌트

```javascript
// frontend/src/components/auth/Login.js
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import './Auth.css';

const Login = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const result = await login(formData.username, formData.password);
        
        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error);
        }
        
        setLoading(false);
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <h2>🔐 로그인</h2>
                    <p>통합 테스트 플랫폼에 오신 것을 환영합니다</p>
                </div>

                {error && (
                    <div className="error-message">
                        ❌ {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="username">사용자명</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            required
                            placeholder="사용자명을 입력하세요"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">비밀번호</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            placeholder="비밀번호를 입력하세요"
                        />
                    </div>

                    <button 
                        type="submit" 
                        className="btn btn-primary btn-block"
                        disabled={loading}
                    >
                        {loading ? '로그인 중...' : '로그인'}
                    </button>
                </form>

                <div className="auth-links">
                    <Link to="/forgot-password">비밀번호를 잊으셨나요?</Link>
                    <span className="divider">|</span>
                    <Link to="/register">계정이 없으신가요? 회원가입</Link>
                </div>
            </div>
        </div>
    );
};

export default Login;
```

### 4.3 회원가입 컴포넌트

```javascript
// frontend/src/components/auth/Register.js
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import './Auth.css';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        firstName: '',
        lastName: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const validateForm = () => {
        if (formData.password !== formData.confirmPassword) {
            setError('비밀번호가 일치하지 않습니다.');
            return false;
        }
        
        if (formData.password.length < 8) {
            setError('비밀번호는 최소 8자 이상이어야 합니다.');
            return false;
        }
        
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccess('');

        if (!validateForm()) {
            setLoading(false);
            return;
        }

        const userData = {
            username: formData.username,
            email: formData.email,
            password: formData.password,
            first_name: formData.firstName,
            last_name: formData.lastName
        };

        const result = await register(userData);
        
        if (result.success) {
            setSuccess(result.message);
            setTimeout(() => {
                navigate('/login');
            }, 3000);
        } else {
            setError(result.error);
        }
        
        setLoading(false);
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <h2>📝 회원가입</h2>
                    <p>새로운 계정을 만들어보세요</p>
                </div>

                {error && (
                    <div className="error-message">
                        ❌ {error}
                    </div>
                )}

                {success && (
                    <div className="success-message">
                        ✅ {success}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="firstName">이름</label>
                            <input
                                type="text"
                                id="firstName"
                                name="firstName"
                                value={formData.firstName}
                                onChange={handleChange}
                                placeholder="이름을 입력하세요"
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="lastName">성</label>
                            <input
                                type="text"
                                id="lastName"
                                name="lastName"
                                value={formData.lastName}
                                onChange={handleChange}
                                placeholder="성을 입력하세요"
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="username">사용자명 *</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            required
                            placeholder="사용자명을 입력하세요"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">이메일 *</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            placeholder="이메일을 입력하세요"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">비밀번호 *</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            placeholder="비밀번호를 입력하세요 (최소 8자)"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">비밀번호 확인 *</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                            placeholder="비밀번호를 다시 입력하세요"
                        />
                    </div>

                    <button 
                        type="submit" 
                        className="btn btn-primary btn-block"
                        disabled={loading}
                    >
                        {loading ? '가입 중...' : '회원가입'}
                    </button>
                </form>

                <div className="auth-links">
                    <span>이미 계정이 있으신가요?</span>
                    <Link to="/login">로그인</Link>
                </div>
            </div>
        </div>
    );
};

export default Register;
```

## 📅 구현 단계별 계획

### Phase 1: 기본 인증 시스템 (1-2주)
1. 사용자 모델 및 데이터베이스 설계
2. JWT 설정 및 기본 인증 API 구현
3. 회원가입/로그인 API 구현
4. 기본 프론트엔드 컴포넌트 구현

### Phase 2: 고급 인증 기능 (1-2주)
1. 이메일 인증 시스템 구현
2. 비밀번호 재설정 기능 구현
3. 프로필 관리 기능 구현
4. 세션 관리 및 보안 강화

### Phase 3: 권한 관리 시스템 (1주)
1. 사용자 역할 및 권한 시스템 구현
2. 관리자 전용 API 구현
3. 권한별 UI 접근 제어 구현
4. 사용자 관리 대시보드 구현

### Phase 4: 보안 및 최적화 (1주)
1. 보안 강화 (CSRF, XSS 방지)
2. 로깅 및 모니터링 시스템 구현
3. 성능 최적화
4. 테스트 코드 작성

## 🔒 보안 고려사항

### 5.1 비밀번호 보안
- bcrypt를 사용한 비밀번호 해시화
- 최소 8자 이상 비밀번호 정책
- 비밀번호 재사용 방지

### 5.2 토큰 보안
- JWT 토큰 만료 시간 설정
- 리프레시 토큰을 통한 자동 갱신
- 토큰 탈취 시 즉시 무효화

### 5.3 세션 보안
- IP 주소 및 User-Agent 기록
- 의심스러운 로그인 시도 감지
- 자동 로그아웃 기능

### 5.4 API 보안
- CORS 설정 최적화
- Rate Limiting 구현
- 입력값 검증 및 Sanitization

## 📝 참고 자료

- [Flask-JWT-Extended 문서](https://flask-jwt-extended.readthedocs.io/)
- [Flask-Mail 문서](https://pythonhosted.org/Flask-Mail/)
- [Werkzeug 보안 유틸리티](https://werkzeug.palletsprojects.com/en/2.0.x/utils/)
- [React Router 문서](https://reactrouter.com/)
- [Axios 인터셉터](https://axios-http.com/docs/interceptors)

---

**버전**: 1.0  
**상태**: 계획 단계  

