"""
캐싱 서비스
Redis 기반 캐싱, 캐시 무효화, TTL 관리
"""
import redis
import json
import os
from functools import wraps
from utils.logger import get_logger

logger = get_logger(__name__)

class CacheService:
    """캐싱 서비스"""
    
    def __init__(self):
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()  # 연결 테스트
            self.enabled = True
            logger.info("Redis 캐시 서비스 초기화 완료")
        except Exception as e:
            logger.warning(f"Redis 연결 실패, 캐싱 비활성화: {str(e)}")
            self.redis_client = None
            self.enabled = False
    
    def get(self, key):
        """캐시에서 값 가져오기"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"캐시 조회 오류: {str(e)}")
            return None
    
    def set(self, key, value, ttl=3600):
        """캐시에 값 저장"""
        if not self.enabled:
            return False
        
        try:
            value_str = json.dumps(value, ensure_ascii=False)
            self.redis_client.setex(key, ttl, value_str)
            return True
        except Exception as e:
            logger.error(f"캐시 저장 오류: {str(e)}")
            return False
    
    def delete(self, key):
        """캐시에서 값 삭제"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"캐시 삭제 오류: {str(e)}")
            return False
    
    def delete_pattern(self, pattern):
        """패턴에 맞는 모든 캐시 키 삭제"""
        if not self.enabled:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"패턴 캐시 삭제 오류: {str(e)}")
            return False
    
    def clear(self):
        """모든 캐시 삭제"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"캐시 전체 삭제 오류: {str(e)}")
            return False
    
    def invalidate_entity(self, entity_type, entity_id):
        """특정 엔티티 관련 캐시 무효화"""
        patterns = [
            f"{entity_type}:{entity_id}:*",
            f"{entity_type}_list:*",
            f"dashboard:*",
            f"summary:*"
        ]
        
        for pattern in patterns:
            self.delete_pattern(pattern)
        
        logger.info(f"엔티티 캐시 무효화: {entity_type}:{entity_id}")

# 전역 캐시 서비스 인스턴스
cache_service = CacheService()

def cached(ttl=3600, key_prefix='', key_func=None):
    """
    함수 결과 캐싱 데코레이터
    
    Args:
        ttl: 캐시 TTL (초)
        key_prefix: 캐시 키 접두사
        key_func: 캐시 키 생성 함수
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 캐시에서 조회
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 캐시에 저장
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

