"""
알림 관리 API
"""
from flask import Blueprint, request, jsonify
from models import db, Notification, NotificationSettings, User
from utils.cors import add_cors_headers
from utils.auth_decorators import user_required, guest_allowed
from utils.logger import get_logger
from services.notification_service import notification_service
import json

logger = get_logger(__name__)

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications', methods=['GET', 'OPTIONS'])
@user_required
def get_notifications():
    """사용자 알림 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        user_id = request.user.id
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = request.args.get('limit', 50, type=int)
        
        notifications = notification_service.get_user_notifications(
            user_id, 
            unread_only=unread_only,
            limit=limit
        )
        
        # 읽지 않은 알림 수
        unread_count = Notification.query.filter_by(
            user_id=user_id,
            read=False
        ).count()
        
        response = jsonify({
            'notifications': notifications,
            'unread_count': unread_count,
            'total': len(notifications)
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"알림 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@notifications_bp.route('/notifications/<int:id>', methods=['GET', 'OPTIONS'])
@user_required
def get_notification(id):
    """알림 상세 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        user_id = request.user.id
        notification = Notification.query.filter_by(
            id=id,
            user_id=user_id
        ).first_or_404()
        
        response = jsonify(notification.to_dict())
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"알림 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@notifications_bp.route('/notifications/<int:id>/read', methods=['POST', 'OPTIONS'])
@user_required
def mark_notification_read(id):
    """알림 읽음 처리"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        user_id = request.user.id
        
        if notification_service.mark_as_read(id, user_id):
            response = jsonify({'message': '알림이 읽음 처리되었습니다'})
            return add_cors_headers(response), 200
        else:
            response = jsonify({'error': '알림을 찾을 수 없습니다'})
            return add_cors_headers(response), 404
        
    except Exception as e:
        logger.error(f"알림 읽음 처리 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@notifications_bp.route('/notifications/read-all', methods=['POST', 'OPTIONS'])
@user_required
def mark_all_notifications_read():
    """모든 알림 읽음 처리"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        user_id = request.user.id
        
        if notification_service.mark_all_as_read(user_id):
            response = jsonify({'message': '모든 알림이 읽음 처리되었습니다'})
            return add_cors_headers(response), 200
        else:
            response = jsonify({'error': '알림 읽음 처리에 실패했습니다'})
            return add_cors_headers(response), 500
        
    except Exception as e:
        logger.error(f"전체 알림 읽음 처리 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@notifications_bp.route('/notifications/<int:id>', methods=['DELETE', 'OPTIONS'])
@user_required
def delete_notification(id):
    """알림 삭제"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        user_id = request.user.id
        notification = Notification.query.filter_by(
            id=id,
            user_id=user_id
        ).first_or_404()
        
        db.session.delete(notification)
        db.session.commit()
        
        response = jsonify({'message': '알림이 삭제되었습니다'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"알림 삭제 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@notifications_bp.route('/notifications/settings', methods=['GET', 'OPTIONS'])
@user_required
def get_notification_settings():
    """알림 설정 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        user_id = request.user.id
        settings = NotificationSettings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            # 기본 설정 생성
            settings = NotificationSettings(
                user_id=user_id,
                settings='{}'
            )
            db.session.add(settings)
            db.session.commit()
        
        response = jsonify(settings.to_dict())
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"알림 설정 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@notifications_bp.route('/notifications/settings', methods=['PUT', 'OPTIONS'])
@user_required
def update_notification_settings():
    """알림 설정 업데이트"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        user_id = request.user.id
        data = request.get_json()
        
        settings = NotificationSettings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            settings = NotificationSettings(user_id=user_id)
            db.session.add(settings)
        
        if 'settings' in data:
            settings.settings = json.dumps(data['settings'])
        if 'email_enabled' in data:
            settings.email_enabled = data['email_enabled']
        if 'slack_enabled' in data:
            settings.slack_enabled = data['slack_enabled']
        if 'in_app_enabled' in data:
            settings.in_app_enabled = data['in_app_enabled']
        
        db.session.commit()
        
        response = jsonify({
            'message': '알림 설정이 업데이트되었습니다',
            'settings': settings.to_dict()
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"알림 설정 업데이트 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

