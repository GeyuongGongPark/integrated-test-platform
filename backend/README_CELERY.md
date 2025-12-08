# Celery 워커 실행 가이드

## 개요
Celery를 사용하여 테스트 실행을 비동기로 처리합니다.

## 필수 요구사항
- Redis 서버 실행 중이어야 합니다
- Redis URL이 환경 변수에 설정되어 있어야 합니다

## Redis 설치 및 실행

### macOS
```bash
brew install redis
brew services start redis
```

### Linux
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### Docker
```bash
docker run -d -p 6379:6379 redis:latest
```

## 환경 변수 설정

`.env` 파일에 다음을 추가:
```
REDIS_URL=redis://localhost:6379/0
```

## Celery 워커 실행

### 개발 환경
```bash
cd backend
celery -A celery_app worker --loglevel=info --concurrency=4
```

### 프로덕션 환경
```bash
celery -A celery_app worker --loglevel=info --concurrency=4 --logfile=logs/celery.log
```

## 큐별 워커 실행

특정 큐만 처리하는 워커:
```bash
# 테스트 실행 큐만 처리
celery -A celery_app worker -Q test_execution --loglevel=info

# 자동화 테스트 큐만 처리
celery -A celery_app worker -Q automation --loglevel=info

# 성능 테스트 큐만 처리
celery -A celery_app worker -Q performance --loglevel=info
```

## 여러 큐 처리
```bash
celery -A celery_app worker -Q test_execution,automation,performance --loglevel=info
```

## Celery 모니터링

### Flower (웹 기반 모니터링 도구)
```bash
pip install flower
celery -A celery_app flower
```

Flower는 기본적으로 http://localhost:5555 에서 실행됩니다.

## API 사용 예시

### 테스트 케이스 비동기 실행
```bash
POST /queue/testcases/1/execute
{
  "environment": "dev",
  "execution_parameters": {}
}
```

### 배치 병렬 실행
```bash
POST /queue/testcases/batch-execute
{
  "test_case_ids": [1, 2, 3, 4, 5],
  "environment": "dev",
  "max_workers": 5
}
```

### 태스크 상태 조회
```bash
GET /queue/tasks/{task_id}
```

### 큐 통계 조회
```bash
GET /queue/stats
```

## 문제 해결

### Redis 연결 오류
- Redis 서버가 실행 중인지 확인
- REDIS_URL 환경 변수가 올바른지 확인

### 워커가 태스크를 처리하지 않음
- 워커가 실행 중인지 확인
- 큐 이름이 올바른지 확인
- 로그를 확인하여 오류 메시지 확인

