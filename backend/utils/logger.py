import logging
import os
from datetime import datetime

def setup_logger(name='integrated_test_platform'):
    """로거 설정 및 반환"""
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정되어 있으면 기존 로거 반환
    if logger.handlers:
        return logger
    
    # 로그 레벨 설정
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level))
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 파일 핸들러 (로컬 환경에서만)
    if not os.environ.get('VERCEL'):
        # logs 디렉토리 생성
        os.makedirs('logs', exist_ok=True)
        
        # 일별 로그 파일
        log_filename = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 파일 핸들러 포맷터
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # 콘솔 핸들러 포맷터
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name=None):
    """로거 인스턴스 반환"""
    if name:
        return logging.getLogger(f'integrated_test_platform.{name}')
    return logging.getLogger('integrated_test_platform')

# 환경별 로그 레벨 설정
def set_environment_log_level():
    """환경에 따른 로그 레벨 설정"""
    if os.environ.get('VERCEL'):
        # Vercel 환경에서는 INFO 레벨만
        logging.getLogger().setLevel(logging.INFO)
    else:
        # 로컬 환경에서는 DEBUG 레벨
        logging.getLogger().setLevel(logging.DEBUG)

# 로거 초기화
logger = setup_logger()
set_environment_log_level()
