"""
SocketIO 이벤트 핸들러
실시간 통신을 위한 WebSocket 이벤트 처리
"""
from flask_socketio import emit, join_room, leave_room, disconnect
from flask import request
from utils.logger import get_logger
from utils.auth_decorators import get_user_from_token
from models import Notification, TestResult, TestCase
from services.notification_service import notification_service
from datetime import datetime
from utils.timezone_utils import get_kst_now

logger = get_logger(__name__)

def register_socketio_handlers(socketio):
    """SocketIO 이벤트 핸들러 등록"""
    
    @socketio.on('connect')
    def handle_connect(auth):
        """클라이언트 연결 처리"""
        try:
            # JWT 토큰 검증
            token = auth.get('token') if auth else None
            if not token:
                logger.warning("토큰이 제공되지 않음")
                disconnect()
                return False
            
            user = get_user_from_token(token)
            if not user:
                logger.warning(f"유효하지 않은 토큰: {token[:20]}...")
                disconnect()
                return False
            
            # 사용자별 룸에 조인
            user_room = f'user_{user.id}'
            join_room(user_room)
            
            # 전역 룸에도 조인 (모든 사용자)
            join_room('all_users')
            
            logger.info(f"사용자 연결: {user.username} (Room: {user_room})")
            
            # 연결 성공 알림
            emit('connected', {
                'message': '연결되었습니다',
                'user_id': user.id,
                'username': user.username
            })
            
            return True
            
        except Exception as e:
            logger.error(f"연결 처리 오류: {str(e)}")
            disconnect()
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """클라이언트 연결 해제 처리"""
        logger.info(f"클라이언트 연결 해제: {request.sid}")
    
    @socketio.on('join_test_execution')
    def handle_join_test_execution(data):
        """테스트 실행 모니터링 룸 조인"""
        try:
            test_case_id = data.get('test_case_id')
            if test_case_id:
                room = f'test_execution_{test_case_id}'
                join_room(room)
                logger.info(f"테스트 실행 룸 조인: {room}")
                emit('joined', {'room': room})
        except Exception as e:
            logger.error(f"테스트 실행 룸 조인 오류: {str(e)}")
    
    @socketio.on('leave_test_execution')
    def handle_leave_test_execution(data):
        """테스트 실행 모니터링 룸 떠나기"""
        try:
            test_case_id = data.get('test_case_id')
            if test_case_id:
                room = f'test_execution_{test_case_id}'
                leave_room(room)
                logger.info(f"테스트 실행 룸 떠남: {room}")
        except Exception as e:
            logger.error(f"테스트 실행 룸 떠나기 오류: {str(e)}")
    
    @socketio.on('subscribe_notifications')
    def handle_subscribe_notifications():
        """알림 구독"""
        try:
            # 이미 user_{user_id} 룸에 조인되어 있으므로 추가 작업 불필요
            emit('subscribed', {'message': '알림을 구독했습니다'})
        except Exception as e:
            logger.error(f"알림 구독 오류: {str(e)}")
    
    @socketio.on('get_notifications')
    def handle_get_notifications(data):
        """알림 요청"""
        try:
            token = data.get('token')
            user = get_user_from_token(token)
            
            if user:
                notifications = notification_service.get_user_notifications(
                    user.id,
                    unread_only=False,
                    limit=20
                )
                emit('notifications', {'notifications': notifications})
        except Exception as e:
            logger.error(f"알림 요청 처리 오류: {str(e)}")

def emit_test_execution_update(test_case_id, status, progress=None, result=None):
    """테스트 실행 상태 업데이트 브로드캐스트"""
    try:
        from app import socketio
        
        data = {
            'test_case_id': test_case_id,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if progress is not None:
            data['progress'] = progress
        
        if result is not None:
            data['result'] = result
        
        socketio.emit('test_execution_update', data, room=f'test_execution_{test_case_id}')
        logger.debug(f"테스트 실행 업데이트 전송: Test Case {test_case_id}, Status: {status}")
        
    except Exception as e:
        logger.error(f"테스트 실행 업데이트 전송 오류: {str(e)}")

def emit_test_result(test_result_id):
    """테스트 결과 브로드캐스트"""
    try:
        from app import socketio
        
        test_result = TestResult.query.get(test_result_id)
        if not test_result:
            return
        
        test_case = TestCase.query.get(test_result.test_case_id)
        if not test_case:
            return
        
        data = {
            'test_result_id': test_result_id,
            'test_case_id': test_result.test_case_id,
            'test_case_name': test_case.name,
            'result': test_result.result,
            'execution_duration': test_result.execution_duration,
            'executed_at': test_result.executed_at.isoformat() if test_result.executed_at else None
        }
        
        # 테스트 실행 룸에 브로드캐스트
        socketio.emit('test_result', data, room=f'test_execution_{test_result.test_case_id}')
        
        # 전역 룸에도 브로드캐스트
        socketio.emit('test_result', data, room='all_users')
        
        logger.debug(f"테스트 결과 브로드캐스트: Test Result {test_result_id}")
        
    except Exception as e:
        logger.error(f"테스트 결과 브로드캐스트 오류: {str(e)}")

