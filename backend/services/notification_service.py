"""
알림 서비스
알림 생성 및 전송을 담당하는 서비스
"""
from models import db, Notification, NotificationSettings, User, TestCase, TestResult
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
import json
import os
import requests

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
            
            # 슬랙 웹훅으로 알림 전송 (설정된 경우)
            self._send_slack_notification(notification, user_id)
            
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
    
    def _send_slack_notification(self, notification, user_id):
        """슬랙 웹훅을 통해 알림 전송"""
        try:
            # 사용자별 슬랙 설정 확인
            user_settings = NotificationSettings.query.filter_by(user_id=user_id).first()
            
            # 슬랙 웹훅 URL 확인 (사용자별 설정 우선, 없으면 전역 환경 변수)
            slack_webhook_url = None
            slack_enabled = False
            
            if user_settings:
                # 사용자별 설정이 있는 경우
                slack_enabled = user_settings.slack_enabled
                if user_settings.slack_webhook_url:
                    slack_webhook_url = user_settings.slack_webhook_url
                    logger.info(f"🔔 사용자별 슬랙 웹훅 URL 사용: User {user_id}, enabled={slack_enabled}")
                else:
                    # 사용자별 URL이 없으면 전역 환경 변수 사용
                    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
                    logger.info(f"🔔 전역 슬랙 웹훅 URL 사용: User {user_id}, enabled={slack_enabled}")
            else:
                # 사용자별 설정이 없는 경우 전역 환경 변수 사용
                slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
                logger.info(f"🔔 사용자 설정 없음, 전역 슬랙 웹훅 URL 사용: User {user_id}")
            
            # 슬랙 웹훅 URL이 없으면 건너뛰기
            if not slack_webhook_url:
                logger.warning(f"⚠️ 슬랙 웹훅 URL이 설정되지 않음: User {user_id}, 환경변수 확인 필요")
                return
            
            # 사용자별 설정이 있고 slack_enabled가 False면 건너뛰기
            if user_settings and not slack_enabled:
                logger.info(f"🔔 사용자 {user_id}의 슬랙 알림이 비활성화되어 있음 (slack_enabled=False)")
                return
            
            logger.info(f"🔔 슬랙 알림 전송 시도: User {user_id}, URL={slack_webhook_url[:30]}...")
            
            # 사용자 정보 가져오기
            user = User.query.get(user_id)
            username = user.username if user else 'Unknown User'
            
            # 알림 타입에 따른 이모지 및 색상 설정
            emoji_map = {
                'assignment': '👤',
                'mention': '💬',
                'test_failed': '❌',
                'test_completed': '✅',
                'test_started': '🚀',
                'schedule_run': '⏰'
            }
            
            color_map = {
                'high': '#dc3545',      # 빨간색
                'medium': '#ffc107',     # 노란색
                'low': '#17a2b8'         # 파란색
            }
            
            emoji = emoji_map.get(notification.notification_type, '🔔')
            color = color_map.get(notification.priority, '#6c757d')
            
            # 슬랙 메시지 포맷팅
            slack_message = {
                "text": f"{emoji} {notification.title}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} {notification.title}",
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*사용자:*\n{username}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*타입:*\n{notification.notification_type}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*메시지:*\n{notification.message}"
                        }
                    }
                ],
                "attachments": [
                    {
                        "color": color,
                        "footer": "Integrated Test Platform",
                        "ts": int(notification.created_at.timestamp()) if notification.created_at else None
                    }
                ]
            }
            
            # 관련 테스트 케이스 정보 추가
            if notification.related_test_case_id:
                test_case = TestCase.query.get(notification.related_test_case_id)
                if test_case:
                    slack_message["blocks"].append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*관련 테스트 케이스:*\n{test_case.name}"
                        }
                    })
            
            # 슬랙 웹훅으로 전송
            response = requests.post(
                slack_webhook_url,
                json=slack_message,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"슬랙 알림 전송 성공: User {user_id}, Notification {notification.id}")
            else:
                logger.warning(f"슬랙 알림 전송 실패: Status {response.status_code}, Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"슬랙 웹훅 요청 오류: {str(e)}")
        except Exception as e:
            logger.error(f"슬랙 알림 전송 오류: {str(e)}", exc_info=True)
    
    def get_user_notifications(self, user_id, unread_only=False, limit=50):
        """사용자 알림 조회"""
        try:
            logger.info(f"🔍 알림 서비스 조회: user_id={user_id}, unread_only={unread_only}, limit={limit}")
            
            query = Notification.query.filter_by(user_id=user_id)
            
            # 전체 알림 수 확인
            total_count = query.count()
            logger.info(f"🔍 사용자 {user_id}의 전체 알림 수: {total_count}개")
            
            if unread_only:
                query = query.filter_by(read=False)
            
            notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
            
            logger.info(f"🔍 조회된 알림 수: {len(notifications)}개")
            
            result = [n.to_dict() for n in notifications]
            logger.info(f"🔍 변환된 알림 수: {len(result)}개")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 알림 조회 오류: {str(e)}", exc_info=True)
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

