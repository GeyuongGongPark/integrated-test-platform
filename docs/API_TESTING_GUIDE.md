# API 테스팅 가이드

## 🚀 현재 API 상태

### ✅ 정상 작동하는 API 엔드포인트

#### 기본 API
- **헬스체크**: `/health` - 서버 상태 및 데이터베이스 연결 확인
- **폴더 관리**: `/folders`, `/folders/tree` - 계층적 폴더 구조 관리
- **테스트 케이스**: `/testcases` - 테스트 케이스 CRUD 작업
- **성능 테스트**: `/performance-tests` - 성능 테스트 결과 관리
- **자동화 테스트**: `/automation-tests` - 자동화 테스트 관리
- **프로젝트**: `/projects` - 프로젝트 정보 관리
- **사용자**: `/users` - 사용자 인증 및 권한 관리

#### 고급 기능 API (v2.5.0)

**협업 및 워크플로우** (`/collaboration`)
- `GET /comments` - 댓글 목록 조회
- `POST /comments` - 댓글 생성
- `PUT /comments/{id}` - 댓글 수정
- `DELETE /comments/{id}` - 댓글 삭제
- `GET /mentions` - 멘션 목록 조회
- `POST /mentions/{id}/read` - 멘션 읽음 처리
- `GET /workflows` - 워크플로우 목록 조회
- `POST /workflows` - 워크플로우 생성
- `POST /workflows/{id}/apply` - 워크플로우 적용
- `POST /workflows/transition` - 워크플로우 상태 전환

**테스트 의존성 관리** (`/dependencies`)
- `GET /dependencies` - 의존성 목록 조회
- `POST /dependencies` - 의존성 생성
- `GET /dependencies/graph` - 의존성 그래프 조회
- `POST /dependencies/execution-order` - 실행 순서 계산
- `GET /dependencies/testcases/{id}/check` - 의존성 조건 확인

**커스텀 리포트** (`/reports`)
- `GET /reports` - 리포트 목록 조회
- `POST /reports` - 리포트 생성
- `POST /reports/{id}/generate` - 리포트 생성 및 실행
- `GET /reports/executions/{id}/download` - 리포트 다운로드

**테스트 데이터 관리** (`/test-data`)
- `GET /test-data/datasets` - 데이터 세트 목록 조회
- `POST /test-data/datasets` - 데이터 세트 생성
- `POST /test-data/datasets/{id}/versions` - 버전 생성
- `GET /test-data/mappings` - 매핑 목록 조회
- `POST /test-data/generate` - 동적 데이터 생성

**알림 시스템** (`/notifications`)
- `GET /notifications` - 알림 목록 조회
- `POST /notifications/{id}/read` - 알림 읽음 처리
- `GET /notifications/settings` - 알림 설정 조회
- `PUT /notifications/settings` - 알림 설정 업데이트

**스케줄 관리** (`/schedules`)
- `GET /schedules` - 스케줄 목록 조회
- `POST /schedules` - 스케줄 생성
- `POST /schedules/{id}/run-now` - 즉시 실행
- `POST /schedules/{id}/toggle` - 활성화/비활성화

**큐 관리** (`/queue`)
- `POST /queue/testcases/{id}/execute` - 테스트 케이스 큐에 추가
- `GET /queue/tasks/{task_id}` - 작업 상태 조회
- `GET /queue/stats` - 큐 통계 조회
- `GET /queue/workers` - 워커 상태 조회

**분석 및 트렌드** (`/analytics`)
- `GET /analytics/trends` - 트렌드 분석
- `GET /analytics/flaky-tests` - Flaky 테스트 감지
- `GET /analytics/regression-detection` - 회귀 감지
- `GET /analytics/test-health` - 테스트 헬스 분석

**CI/CD 통합** (`/cicd`)
- `GET /cicd/integrations` - 통합 목록 조회
- `POST /cicd/integrations` - 통합 생성
- `POST /cicd/webhook/github` - GitHub 웹훅
- `POST /cicd/webhook/jenkins` - Jenkins 웹훅

## 📋 API 테스트 방법

### 1. 로컬 환경 테스트

#### 백엔드 서버 실행
```bash
cd backend
source venv/bin/activate
python app.py
```

#### API 테스트
```bash
# 헬스체크
curl http://localhost:8000/health

# 폴더 목록 조회
curl http://localhost:8000/folders

# 테스트 케이스 목록
curl http://localhost:8000/testcases

# 댓글 목록 조회
curl "http://localhost:8000/comments?entity_type=test_case&entity_id=1"

# 알림 목록 조회 (인증 필요)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/notifications
```

### 2. Vercel 배포 환경 테스트

#### 백엔드 API 테스트
```bash
# 헬스체크
curl https://backend-alpha-liard.vercel.app/health

# 폴더 목록 조회
curl https://backend-alpha-liard.vercel.app/folders
```

## 🔍 API 응답 형식

### 댓글 API 응답 예시

#### GET /comments?entity_type=test_case&entity_id=1
```json
[
  {
    "id": 1,
    "entity_type": "test_case",
    "entity_id": 1,
    "content": "이 테스트 케이스는 잘 작성되었습니다.",
    "author_id": 1,
    "author_name": "admin",
    "created_at": "2025-01-09T10:00:00",
    "replies": []
  }
]
```

### 의존성 그래프 API 응답 예시

#### GET /dependencies/graph?test_case_ids=1,2,3
```json
{
  "forward": {
    "1": [
      {
        "id": 1,
        "depends_on": 2,
        "type": "required",
        "priority": 1
      }
    ]
  },
  "reverse": {
    "2": [
      {
        "id": 1,
        "test_case": 1,
        "type": "required"
      }
    ]
  }
}
```

### 리포트 생성 API 응답 예시

#### POST /reports/{id}/generate
```json
{
  "message": "리포트 생성이 시작되었습니다",
  "execution": {
    "id": 1,
    "report_id": 1,
    "status": "running",
    "started_at": "2025-01-09T10:00:00"
  }
}
```

## 🧪 Postman 컬렉션

### 환경 설정
1. **로컬 환경**
   - `base_url`: `http://localhost:8000`
   - `database`: `MySQL (Docker)`

2. **Vercel 환경**
   - `base_url`: `https://backend-alpha-liard.vercel.app`
   - `database`: `SQLite (Fallback)`

### 테스트 케이스

#### 1. 헬스체크
- **Method**: GET
- **URL**: `{{base_url}}/health`
- **Expected**: 200 OK, 서버 상태 정보

#### 2. 댓글 생성
- **Method**: POST
- **URL**: `{{base_url}}/comments`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Body**:
```json
{
  "entity_type": "test_case",
  "entity_id": 1,
  "content": "이 테스트 케이스는 잘 작성되었습니다. @admin 확인 부탁드립니다."
}
```

#### 3. 의존성 생성
- **Method**: POST
- **URL**: `{{base_url}}/dependencies`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Body**:
```json
{
  "test_case_id": 1,
  "depends_on_test_case_id": 2,
  "dependency_type": "required",
  "condition": {
    "result": "Pass"
  }
}
```

#### 4. 리포트 생성
- **Method**: POST
- **URL**: `{{base_url}}/reports`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Body**:
```json
{
  "name": "테스트 실행 리포트",
  "report_type": "test_execution",
  "config": {
    "include_summary": true,
    "include_details": true
  },
  "filters": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-09"
  }
}
```

#### 5. 알림 조회
- **Method**: GET
- **URL**: `{{base_url}}/notifications`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Query Parameters**: `unread_only=true`

## 🔧 문제 해결 가이드

### 일반적인 오류

#### 1. 500 Internal Server Error
**증상**: API 호출 시 500 오류
**원인**: 서버 내부 오류, 데이터베이스 연결 문제
**해결책**:
- 백엔드 로그 확인
- 데이터베이스 연결 상태 확인
- 환경 변수 설정 확인

#### 2. 401 Authentication Required
**증상**: 인증이 필요한 API에서 401 오류
**원인**: JWT 토큰이 없거나 만료됨
**해결책**:
- 로그인하여 새 토큰 획득
- Authorization 헤더에 토큰 포함
- 토큰 만료 시간 확인

#### 3. CORS 오류
**증상**: 브라우저에서 CORS 오류
**원인**: 프론트엔드와 백엔드 도메인 불일치
**해결책**:
- 백엔드 CORS 설정 확인
- 올바른 API URL 사용

### 디버깅 방법

#### 1. 백엔드 로그 확인
```bash
# 로컬 환경
cd backend
python app.py

# 로그에서 오류 메시지 확인
```

#### 2. API 응답 상세 확인
```bash
# 상세 응답 정보 확인
curl -v http://localhost:8000/health

# JSON 응답 확인
curl -s http://localhost:8000/folders | jq
```

#### 3. 브라우저 개발자 도구
- Network 탭에서 API 요청/응답 확인
- Console 탭에서 JavaScript 오류 확인

## 📊 API 성능 모니터링

### 응답 시간 측정
```bash
# 응답 시간 측정
time curl -s http://localhost:8000/health

# 상세 성능 정보
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/folders
```

### curl-format.txt
```
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
```

## 🚀 자동화 테스트

### 스크립트 기반 테스트
```bash
# 전체 API 테스트 스크립트
cd test-scripts
./test-api-endpoints.sh

# 특정 API 테스트
./test-collaboration-api.sh
```

### CI/CD 파이프라인
- GitHub Actions를 통한 자동 API 테스트
- 배포 전 API 엔드포인트 검증
- 성능 테스트 자동화

## 📚 추가 리소스

### 관련 문서
- [README.md](../README.md) - 프로젝트 개요
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 프로젝트 구조
- [POSTMAN_USAGE_GUIDE.md](POSTMAN_USAGE_GUIDE.md) - Postman 사용 가이드
- [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) - 배포 현황

### 외부 도구
- **Postman**: API 테스트 및 문서화
- **Insomnia**: REST API 클라이언트
- **curl**: 명령줄 HTTP 클라이언트
- **jq**: JSON 데이터 처리

---

**마지막 업데이트**: 2025년 1월 9일
**API 버전**: 2.5.0
**상태**: 모든 API 엔드포인트 정상 작동
