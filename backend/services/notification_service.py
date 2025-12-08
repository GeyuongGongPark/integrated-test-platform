"""
알림 서비스
알림 생성 및 전송을 담당하는 서비스
"""
from models import db, Notification, NotificationSettings, User, TestCase, TestResult
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
import json

logger = get_logger(__name__)

class NotificationService:
    """알림 서비스 싱글톤"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
        return cls._instance
    
    def create_notification(self, user_id, notification_type, title, message, 
                           related_test_case_id=None, related_automation_test_id=None,
                           related_performance_test_id=None, related_test_result_id=None,
                           priority='medium', channels='in_app'):
        """
        알림 생성
        
        Args:
            user_id: 사용자 ID
            notification_type: 알림 타입
            title: 알림 제목
            message: 알림 메시지
            related_test_case_id: 관련 테스트 케이스 ID
            related_automation_test_id: 관련 자동화 테스트 ID
            related_performance_test_id: 관련 성능 테스트 ID
            related_test_result_id: 관련 테스트 결과 ID
            priority: 우선순위
            channels: 알림 채널
        
        Returns:
            Notification: 생성된 알림 객체
        """
        try:
            notification = Notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                related_test_case_id=related_test_case_id,
                related_automation_test_id=related_automation_test_id,
                related_performance_test_id=related_performance_test_id,
                related_test_result_id=related_test_result_id,
                priority=priority,
                channels=channels
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # WebSocket을 통해 실시간 알림 전송
            self._send_realtime_notification(notification)
            
            logger.info(f"알림 생성 완료: {title} (User: {user_id})")
            return notification
            
        except Exception as e:
            logger.error(f"알림 생성 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def notify_test_failed(self, test_case_id, test_result_id, user_id=None):
        """테스트 실패 알림"""
        try:
            test_case = TestCase.query.get(test_case_id)
            if not test_case:
                return
            
            # 담당자에게 알림
            target_user_id = user_id or test_case.assignee_id or test_case.creator_id
            if not target_user_id:
                return
            
            title = f"테스트 실패: {test_case.name}"
            message = f"테스트 케이스 '{test_case.name}'가 실패했습니다."
            
            notification = self.create_notification(
                user_id=target_user_id,
                notification_type='test_failed',
                title=title,
                message=message,
                related_test_case_id=test_case_id,
                related_test_result_id=test_result_id,
                priority='high'
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"테스트 실패 알림 생성 오류: {str(e)}")
    
    def notify_test_completed(self, test_case_id, test_result_id, result_status, user_id=None):
        """테스트 완료 알림"""
        try:
            test_case = TestCase.query.get(test_case_id)
            if not test_case:
                return
            
            target_user_id = user_id or test_case.assignee_id or test_case.creator_id
            if not target_user_id:
                return
            
            status_text = '성공' if result_status == 'Pass' else '실패'
            title = f"테스트 완료: {test_case.name}"
            message = f"테스트 케이스 '{test_case.name}'가 {status_text}했습니다."
            
            priority = 'medium' if result_status == 'Pass' else 'high'
            
            notification = self.create_notification(
                user_id=target_user_id,
                notification_type='test_completed',
                title=title,
                message=message,
                related_test_case_id=test_case_id,
                related_test_result_id=test_result_id,
                priority=priority
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"테스트 완료 알림 생성 오류: {str(e)}")
    
    def notify_test_started(self, test_case_id, user_id=None):
        """테스트 시작 알림"""
        try:
            test_case = TestCase.query.get(test_case_id)
            if not test_case:
                return
            
            target_user_id = user_id or test_case.assignee_id or test_case.creator_id
            if not target_user_id:
                return
            
            title = f"테스트 시작: {test_case.name}"
            message = f"테스트 케이스 '{test_case.name}' 실행이 시작되었습니다."
            
            notification = self.create_notification(
                user_id=target_user_id,
                notification_type='test_started',
                title=title,
                message=message,
                related_test_case_id=test_case_id,
                priority='low'
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"테스트 시작 알림 생성 오류: {str(e)}")
    
    def notify_schedule_run(self, schedule_id, test_case_id, result_status, user_id=None):
        """스케줄 실행 알림"""
        try:
            test_case = TestCase.query.get(test_case_id)
            if not test_case:
                return
            
            target_user_id = user_id or test_case.assignee_id or test_case.creator_id
            if not target_user_id:
                return
            
            status_text = '성공' if result_status == 'success' else '실패'
            title = f"스케줄 실행 완료: {test_case.name}"
            message = f"스케줄된 테스트 '{test_case.name}' 실행이 {status_text}했습니다."
            
            notification = self.create_notification(
                user_id=target_user_id,
                notification_type='schedule_run',
                title=title,
                message=message,
                related_test_case_id=test_case_id,
                priority='medium'
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"스케줄 실행 알림 생성 오류: {str(e)}")
    
    def _send_realtime_notification(self, notification):
        """WebSocket을 통해 실시간 알림 전송"""
        try:
            from app import socketio
            
            # 해당 사용자에게만 알림 전송
            socketio.emit('notification', notification.to_dict(), room=f'user_{notification.user_id}')
            logger.debug(f"실시간 알림 전송: User {notification.user_id}")
            
        except Exception as e:
            logger.error(f"실시간 알림 전송 오류: {str(e)}")
    
    def get_user_notifications(self, user_id, unread_only=False, limit=50):
        """사용자 알림 조회"""
        try:
            query = Notification.query.filter_by(user_id=user_id)
            
            if unread_only:
                query = query.filter_by(read=False)
            
            notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
            
            return [n.to_dict() for n in notifications]
            
        except Exception as e:
            logger.error(f"알림 조회 오류: {str(e)}")
            return []
    
    def mark_as_read(self, notification_id, user_id):
        """알림 읽음 처리"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                notification.read = True
                notification.read_at = get_kst_now()
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"알림 읽음 처리 오류: {str(e)}")
            db.session.rollback()
            return False
    
    def mark_all_as_read(self, user_id):
        """사용자의 모든 알림 읽음 처리"""
        try:
            Notification.query.filter_by(
                user_id=user_id,
                read=False
            ).update({'read': True, 'read_at': get_kst_now()})
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"전체 알림 읽음 처리 오류: {str(e)}")
            db.session.rollback()
            return False

# 전역 알림 서비스 인스턴스
notification_service = NotificationService()

