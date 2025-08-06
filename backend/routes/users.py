from flask import Blueprint, request, jsonify
from models import db, User
from utils.auth import require_permission
from utils.cors import add_cors_headers

# Blueprint 생성
users_bp = Blueprint('users', __name__)

# 사용자 관리 API
@users_bp.route('/users', methods=['GET'])
def get_users():
    """사용자 목록 조회"""
    try:
        # 하드코딩된 사용자 목록 반환 (Users 테이블이 없으므로)
        users = [{
            'id': 1,
            'username': 'admin',
            'email': 'admin@example.com',
            'role': 'Administrator',
            'is_active': True,
            'created_at': '2025-01-01T00:00:00',
            'last_login': '2025-08-06T08:00:00'
        }]
        response = jsonify(users)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@users_bp.route('/users', methods=['POST'])
def create_user():
    """새 사용자 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('username') or not data.get('email'):
            response = jsonify({'error': '사용자명과 이메일은 필수입니다.'})
            return add_cors_headers(response), 400
        
        # 중복 사용자명 검증
        if User.query.filter_by(username=data['username']).first():
            response = jsonify({'error': '이미 존재하는 사용자명입니다.'})
            return add_cors_headers(response), 400
        
        # 중복 이메일 검증
        if User.query.filter_by(email=data['email']).first():
            response = jsonify({'error': '이미 존재하는 이메일입니다.'})
            return add_cors_headers(response), 400
        
        # 기본 비밀번호 설정 (1q2w#E$R)
        default_password = '1q2w#E$R'
        
        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'User')
        )
        
        # 비밀번호 설정 (해시화됨)
        user.set_password(data.get('password', default_password))
        
        db.session.add(user)
        db.session.commit()
        
        response = jsonify({
            'message': '사용자가 성공적으로 생성되었습니다.',
            'user_id': user.id,
            'default_password': default_password if not data.get('password') else None
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_permission('update')
def update_user(user_id):
    """사용자 정보 수정"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'username' in data:
            # 중복 사용자명 검증
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user_id:
                response = jsonify({'error': '이미 존재하는 사용자명입니다.'})
                return add_cors_headers(response), 400
            user.username = data['username']
        
        if 'email' in data:
            # 중복 이메일 검증
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                response = jsonify({'error': '이미 존재하는 이메일입니다.'})
                return add_cors_headers(response), 400
            user.email = data['email']
        
        if 'password' in data:
            # 비밀번호 변경
            user.set_password(data['password'])
        
        if 'role' in data:
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        response = jsonify({'message': '사용자 정보가 성공적으로 수정되었습니다.'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_permission('delete')
def delete_user(user_id):
    """사용자 삭제"""
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        
        response = jsonify({'message': '사용자가 성공적으로 삭제되었습니다.'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@users_bp.route('/users/current', methods=['GET'])
def get_current_user():
    """현재 로그인한 사용자 정보 조회"""
    try:
        # 하드코딩된 admin 사용자 정보 반환 (Users 테이블이 없으므로)
        response = jsonify({
            'id': 1,
            'username': 'admin',
            'email': 'admin@example.com',
            'role': 'Administrator',
            'is_active': True,
            'created_at': '2025-01-01T00:00:00',
            'last_login': '2025-08-06T08:00:00'
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@users_bp.route('/users/<int:user_id>/change-password', methods=['PUT'])
def change_password(user_id):
    """사용자 비밀번호 변경"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            response = jsonify({'error': '현재 비밀번호와 새 비밀번호는 필수입니다.'})
            return add_cors_headers(response), 400
        
        # 현재 비밀번호 검증
        if not user.check_password(data['current_password']):
            response = jsonify({'error': '현재 비밀번호가 올바르지 않습니다.'})
            return add_cors_headers(response), 400
        
        # 새 비밀번호 설정
        user.set_password(data['new_password'])
        
        db.session.commit()
        
        response = jsonify({'message': '비밀번호가 성공적으로 변경되었습니다.'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500 