"""
테스트 스케줄러 서비스
APScheduler를 사용하여 테스트 케이스 자동 실행 스케줄 관리
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from datetime import datetime, timedelta
import json
import logging
from croniter import croniter
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger

logger = get_logger(__name__)

class SchedulerService:
    """테스트 스케줄러 서비스 싱글톤"""
    _instance = None
    _scheduler = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchedulerService, cls).__new__(cls)
            cls._scheduler = BackgroundScheduler(timezone='Asia/Seoul')
            cls._scheduler.start()
            logger.info("테스트 스케줄러 서비스 초기화 완료")
        return cls._instance
    
    @property
    def scheduler(self):
        return self._scheduler
    
    def add_schedule(self, schedule_id, test_case_id, schedule_type, schedule_expression, 
                     environment='dev', execution_parameters=None, callback=None):
        """
        스케줄 추가
        
        Args:
            schedule_id: 스케줄 ID
            test_case_id: 테스트 케이스 ID
            schedule_type: 스케줄 타입 ('daily', 'weekly', 'monthly', 'cron')
            schedule_expression: 스케줄 표현식
            environment: 실행 환경
            execution_parameters: 실행 파라미터 (dict)
            callback: 실행 콜백 함수
        """
        job_id = f"test_schedule_{schedule_id}"
        
        try:
            # 스케줄 타입에 따라 트리거 생성
            if schedule_type == 'cron':
                # cron 표현식 파싱
                cron_parts = schedule_expression.split()
                if len(cron_parts) == 5:
                    trigger = CronTrigger(
                        minute=cron_parts[0],
                        hour=cron_parts[1],
                        day=cron_parts[2],
                        month=cron_parts[3],
                        day_of_week=cron_parts[4],
                        timezone='Asia/Seoul'
                    )
                else:
                    logger.error(f"잘못된 cron 표현식: {schedule_expression}")
                    return False
            elif schedule_type == 'daily':
                # 매일 실행 (기본값: 오전 9시)
                hour = 9
                minute = 0
                if schedule_expression:
                    try:
                        parts = schedule_expression.split(':')
                        if len(parts) == 2:
                            hour = int(parts[0])
                            minute = int(parts[1])
                    except:
                        pass
                trigger = CronTrigger(hour=hour, minute=minute, timezone='Asia/Seoul')
            elif schedule_type == 'weekly':
                # 매주 실행 (기본값: 월요일 오전 9시)
                day_of_week = 0  # 월요일
                hour = 9
                minute = 0
                if schedule_expression:
                    try:
                        parts = schedule_expression.split(',')
                        if len(parts) >= 1:
                            day_of_week = int(parts[0])
                        if len(parts) >= 2:
                            hour = int(parts[1])
                        if len(parts) >= 3:
                            minute = int(parts[2])
                    except:
                        pass
                trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute, timezone='Asia/Seoul')
            elif schedule_type == 'monthly':
                # 매월 실행 (기본값: 매월 1일 오전 9시)
                day = 1
                hour = 9
                minute = 0
                if schedule_expression:
                    try:
                        parts = schedule_expression.split(',')
                        if len(parts) >= 1:
                            day = int(parts[0])
                        if len(parts) >= 2:
                            hour = int(parts[1])
                        if len(parts) >= 3:
                            minute = int(parts[2])
                    except:
                        pass
                trigger = CronTrigger(day=day, hour=hour, minute=minute, timezone='Asia/Seoul')
            else:
                logger.error(f"지원하지 않는 스케줄 타입: {schedule_type}")
                return False
            
            # 작업 추가
            self._scheduler.add_job(
                callback,
                trigger=trigger,
                id=job_id,
                args=[schedule_id, test_case_id, environment, execution_parameters],
                replace_existing=True,
                max_instances=1
            )
            
            logger.info(f"스케줄 추가 완료: {job_id} (테스트 케이스 ID: {test_case_id})")
            return True
            
        except Exception as e:
            logger.error(f"스케줄 추가 실패: {str(e)}")
            return False
    
    def remove_schedule(self, schedule_id):
        """스케줄 제거"""
        job_id = f"test_schedule_{schedule_id}"
        try:
            self._scheduler.remove_job(job_id)
            logger.info(f"스케줄 제거 완료: {job_id}")
            return True
        except Exception as e:
            logger.error(f"스케줄 제거 실패: {str(e)}")
            return False
    
    def pause_schedule(self, schedule_id):
        """스케줄 일시 중지"""
        job_id = f"test_schedule_{schedule_id}"
        try:
            self._scheduler.pause_job(job_id)
            logger.info(f"스케줄 일시 중지: {job_id}")
            return True
        except Exception as e:
            logger.error(f"스케줄 일시 중지 실패: {str(e)}")
            return False
    
    def resume_schedule(self, schedule_id):
        """스케줄 재개"""
        job_id = f"test_schedule_{schedule_id}"
        try:
            self._scheduler.resume_job(job_id)
            logger.info(f"스케줄 재개: {job_id}")
            return True
        except Exception as e:
            logger.error(f"스케줄 재개 실패: {str(e)}")
            return False
    
    def get_next_run_time(self, schedule_type, schedule_expression):
        """다음 실행 시간 계산"""
        try:
            if schedule_type == 'cron':
                cron = croniter(schedule_expression, get_kst_now())
                return cron.get_next(datetime)
            elif schedule_type == 'daily':
                hour = 9
                minute = 0
                if schedule_expression:
                    try:
                        parts = schedule_expression.split(':')
                        if len(parts) == 2:
                            hour = int(parts[0])
                            minute = int(parts[1])
                    except:
                        pass
                next_run = get_kst_now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= get_kst_now():
                    next_run += timedelta(days=1)
                return next_run
            # 다른 타입들도 유사하게 처리
            return None
        except Exception as e:
            logger.error(f"다음 실행 시간 계산 실패: {str(e)}")
            return None
    
    def get_all_jobs(self):
        """모든 스케줄 작업 조회"""
        return self._scheduler.get_jobs()
    
    def shutdown(self):
        """스케줄러 종료"""
        if self._scheduler:
            self._scheduler.shutdown()
            logger.info("테스트 스케줄러 종료")

# 전역 스케줄러 서비스 인스턴스
scheduler_service = SchedulerService()

