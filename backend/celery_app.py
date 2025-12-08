"""
Celery 애플리케이션 설정
"""
from celery import Celery
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Redis URL 설정
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Celery 앱 생성
celery_app = Celery(
    'test_executor',
    broker=redis_url,
    backend=redis_url,
    include=['tasks']
)

# Celery 설정
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1시간 타임아웃
    task_soft_time_limit=3300,  # 55분 소프트 타임아웃
    worker_prefetch_multiplier=4,  # 워커가 한 번에 가져올 태스크 수
    worker_max_tasks_per_child=50,  # 워커 재시작 전 최대 태스크 수
    task_acks_late=True,  # 태스크 완료 후 ACK
    task_reject_on_worker_lost=True,  # 워커 손실 시 태스크 거부
    broker_connection_retry_on_startup=True,
    result_expires=3600,  # 결과 만료 시간 (1시간)
)

# 큐 설정
celery_app.conf.task_routes = {
    'tasks.execute_test_case': {'queue': 'test_execution'},
    'tasks.execute_test_case_batch': {'queue': 'test_execution'},
    'tasks.execute_automation_test': {'queue': 'automation'},
    'tasks.execute_performance_test': {'queue': 'performance'},
}

