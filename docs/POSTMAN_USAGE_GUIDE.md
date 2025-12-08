# Postman API 테스트 가이드

## 🚀 개요

이 가이드는 통합 테스트 플랫폼의 API를 Postman으로 테스트하기 위한 상세한 가이드입니다.

## 📋 준비사항

### 1. Postman 설치
- [Postman 공식 사이트](https://www.postman.com/downloads/)에서 다운로드
- 계정 생성 (무료)

### 2. 백엔드 서버 실행
```bash
cd backend
source venv/bin/activate
python app.py
```

### 3. Postman 컬렉션 Import
- `docs/postman_collection_v2.5.0_complete.json` 파일을 Postman에 Import
- 또는 아래 가이드에 따라 수동으로 컬렉션 생성

## 🌐 환경 설정

### 로컬 개발 환경
```json
{
  "name": "Local Development",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "enabled": true
    },
    {
      "key": "environment",
      "value": "development",
      "enabled": true
    },
    {
      "key": "auth_token",
      "value": "",
      "enabled": true
    }
  ]
}
```

### Vercel 프로덕션 환경
```json
{
  "name": "Vercel Production",
  "values": [
    {
      "key": "base_url",
      "value": "https://backend-alpha-liard.vercel.app",
      "enabled": true
    },
    {
      "key": "environment",
      "value": "production",
      "enabled": true
    },
    {
      "key": "auth_token",
      "value": "",
      "enabled": true
    }
  ]
}
```

## 📚 API 엔드포인트 테스트

### 1. 헬스체크 API

#### GET /health
- **Method**: GET
- **URL**: `{{base_url}}/health`
- **Description**: 서버 상태 및 데이터베이스 연결 확인
- **Expected Response**: 200 OK

### 2. 협업 및 워크플로우 API

#### GET /comments
- **Method**: GET
- **URL**: `{{base_url}}/comments?entity_type=test_case&entity_id=1`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Description**: 댓글 목록 조회

#### POST /comments
- **Method**: POST
- **URL**: `{{base_url}}/comments`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{auth_token}}`
- **Body**:
```json
{
  "entity_type": "test_case",
  "entity_id": 1,
  "content": "이 테스트 케이스는 잘 작성되었습니다. @admin 확인 부탁드립니다."
}
```

#### GET /mentions
- **Method**: GET
- **URL**: `{{base_url}}/mentions`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Description**: 멘션 목록 조회

#### GET /workflows
- **Method**: GET
- **URL**: `{{base_url}}/workflows`
- **Description**: 워크플로우 목록 조회

### 3. 테스트 의존성 관리 API

#### GET /dependencies
- **Method**: GET
- **URL**: `{{base_url}}/dependencies?test_case_id=1`
- **Description**: 의존성 목록 조회

#### POST /dependencies
- **Method**: POST
- **URL**: `{{base_url}}/dependencies`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{auth_token}}`
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

#### GET /dependencies/graph
- **Method**: GET
- **URL**: `{{base_url}}/dependencies/graph?test_case_ids=1,2,3`
- **Description**: 의존성 그래프 조회

#### POST /dependencies/execution-order
- **Method**: POST
- **URL**: `{{base_url}}/dependencies/execution-order`
- **Body**:
```json
{
  "test_case_ids": [1, 2, 3]
}
```

### 4. 커스텀 리포트 API

#### GET /reports
- **Method**: GET
- **URL**: `{{base_url}}/reports`
- **Description**: 리포트 목록 조회

#### POST /reports
- **Method**: POST
- **URL**: `{{base_url}}/reports`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{auth_token}}`
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
  },
  "output_format": "html"
}
```

#### POST /reports/{id}/generate
- **Method**: POST
- **URL**: `{{base_url}}/reports/1/generate`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Body**:
```json
{
  "execution_params": {
    "include_charts": true
  }
}
```

### 5. 테스트 데이터 관리 API

#### GET /test-data/datasets
- **Method**: GET
- **URL**: `{{base_url}}/test-data/datasets?environment=dev`
- **Description**: 데이터 세트 목록 조회

#### POST /test-data/datasets
- **Method**: POST
- **URL**: `{{base_url}}/test-data/datasets`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{auth_token}}`
- **Body**:
```json
{
  "name": "로그인 테스트 데이터",
  "data": {
    "username": "testuser",
    "password": "testpass123"
  },
  "environment": "dev",
  "masking_enabled": true,
  "masking_rules": {
    "password": {
      "type": "mask",
      "mask_char": "*"
    }
  }
}
```

#### POST /test-data/generate
- **Method**: POST
- **URL**: `{{base_url}}/test-data/generate`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Body**:
```json
{
  "schema": {
    "username": {
      "type": "string",
      "length": 10
    },
    "email": {
      "type": "email"
    }
  },
  "count": 5
}
```

### 6. 알림 시스템 API

#### GET /notifications
- **Method**: GET
- **URL**: `{{base_url}}/notifications?unread_only=true`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Description**: 알림 목록 조회

#### POST /notifications/{id}/read
- **Method**: POST
- **URL**: `{{base_url}}/notifications/1/read`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Description**: 알림 읽음 처리

#### GET /notifications/settings
- **Method**: GET
- **URL**: `{{base_url}}/notifications/settings`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Description**: 알림 설정 조회

### 7. 스케줄 관리 API

#### GET /schedules
- **Method**: GET
- **URL**: `{{base_url}}/schedules`
- **Description**: 스케줄 목록 조회

#### POST /schedules
- **Method**: POST
- **URL**: `{{base_url}}/schedules`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{auth_token}}`
- **Body**:
```json
{
  "test_case_id": 1,
  "name": "매일 오전 9시 테스트",
  "schedule_type": "daily",
  "schedule_expression": "9:0",
  "environment": "dev"
}
```

#### POST /schedules/{id}/run-now
- **Method**: POST
- **URL**: `{{base_url}}/schedules/1/run-now`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Description**: 스케줄 즉시 실행

### 8. 큐 관리 API

#### POST /queue/testcases/{id}/execute
- **Method**: POST
- **URL**: `{{base_url}}/queue/testcases/1/execute`
- **Headers**: `Authorization: Bearer {{auth_token}}`
- **Body**:
```json
{
  "environment": "dev",
  "execution_parameters": {}
}
```

#### GET /queue/tasks/{task_id}
- **Method**: GET
- **URL**: `{{base_url}}/queue/tasks/abc123`
- **Description**: 작업 상태 조회

#### GET /queue/stats
- **Method**: GET
- **URL**: `{{base_url}}/queue/stats`
- **Description**: 큐 통계 조회

### 9. 분석 및 트렌드 API

#### GET /analytics/trends
- **Method**: GET
- **URL**: `{{base_url}}/analytics/trends?days=30`
- **Description**: 트렌드 분석

#### GET /analytics/flaky-tests
- **Method**: GET
- **URL**: `{{base_url}}/analytics/flaky-tests`
- **Description**: Flaky 테스트 감지

#### GET /analytics/test-health
- **Method**: GET
- **URL**: `{{base_url}}/analytics/test-health`
- **Description**: 테스트 헬스 분석

### 10. CI/CD 통합 API

#### GET /cicd/integrations
- **Method**: GET
- **URL**: `{{base_url}}/cicd/integrations`
- **Description**: CI/CD 통합 목록 조회

#### POST /cicd/integrations
- **Method**: POST
- **URL**: `{{base_url}}/cicd/integrations`
- **Headers**: 
  - `Content-Type: application/json`
  - `Authorization: Bearer {{auth_token}}`
- **Body**:
```json
{
  "integration_type": "github",
  "name": "GitHub Actions 통합",
  "config": {
    "repository": "owner/repo",
    "github_token": "ghp_xxx"
  }
}
```

## 🧪 테스트 시나리오

### 1. 협업 워크플로우 테스트
1. **댓글 생성**: 테스트 케이스에 댓글 추가
2. **멘션 확인**: 멘션된 사용자에게 알림 확인
3. **워크플로우 적용**: 테스트 케이스에 워크플로우 적용
4. **상태 전환**: 워크플로우 상태 전환

### 2. 의존성 관리 테스트
1. **의존성 생성**: 테스트 케이스 간 의존성 정의
2. **의존성 그래프 조회**: 의존성 관계 시각화
3. **실행 순서 계산**: 의존성 기반 실행 순서 확인
4. **의존성 조건 확인**: 실행 가능 여부 확인

### 3. 리포트 생성 테스트
1. **리포트 생성**: 커스텀 리포트 정의
2. **리포트 실행**: 리포트 생성 및 실행
3. **리포트 다운로드**: 생성된 리포트 다운로드

## 🔧 Postman 고급 기능 활용

### 1. Pre-request Scripts
```javascript
// 환경 변수 설정
pm.environment.set("timestamp", new Date().toISOString());

// 동적 값 생성
pm.environment.set("random_id", Math.floor(Math.random() * 1000));
```

### 2. Tests Scripts
```javascript
// 응답 상태 코드 확인
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// 응답 시간 확인
pm.test("Response time is less than 2000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});

// 응답 데이터 구조 확인
pm.test("Response has required fields", function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('status');
    pm.expect(response).to.have.property('message');
});

// 환경 변수에 값 저장
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.id) {
        pm.environment.set("testcase_id", response.id);
    }
}
```

### 3. Collection Variables
```json
{
  "name": "Collection Variables",
  "variables": [
    {
      "key": "auth_token",
      "value": "",
      "type": "string"
    },
    {
      "key": "test_folder_id",
      "value": "1",
      "type": "string"
    }
  ]
}
```

## 🚨 문제 해결

### 일반적인 오류

#### 1. 500 Internal Server Error
- **원인**: 서버 내부 오류, 데이터베이스 연결 문제
- **해결책**: 
  - 백엔드 로그 확인
  - 데이터베이스 연결 상태 확인
  - 환경 변수 설정 확인

#### 2. 401 Authentication Required
- **원인**: JWT 토큰이 없거나 만료됨
- **해결책**: 
  - 로그인하여 새 토큰 획득
  - Authorization 헤더에 토큰 포함

#### 3. CORS 오류
- **원인**: 프론트엔드와 백엔드 도메인 불일치
- **해결책**: 
  - 백엔드 CORS 설정 확인
  - 올바른 API URL 사용

### 디버깅 방법

#### 1. Postman Console 확인
- **View** → **Show Postman Console**
- 요청/응답 상세 정보 확인
- 에러 메시지 및 스택 트레이스 확인

#### 2. 네트워크 탭 확인
- **Network** 탭에서 요청/응답 헤더 확인
- 상태 코드 및 응답 시간 확인

#### 3. 환경 변수 확인
- **Environment** 드롭다운에서 현재 환경 확인
- 변수 값이 올바르게 설정되었는지 확인

## 📊 성능 테스트

### 응답 시간 측정
```javascript
// Tests 탭에 추가
pm.test("Response time is acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});
```

### 부하 테스트
- **Postman Runner** 사용
- **Iterations**: 반복 횟수 설정
- **Delay**: 요청 간 지연 시간 설정

## 🔒 보안 테스트

### 인증 테스트
```javascript
// 인증 토큰 검증
pm.test("Authentication token is valid", function () {
    const response = pm.response.json();
    pm.expect(response).to.not.have.property('error');
    pm.expect(response.status).to.not.equal('unauthorized');
});
```

## 📚 추가 리소스

### Postman 학습 자료
- [Postman Learning Center](https://learning.postman.com/)
- [Postman YouTube Channel](https://www.youtube.com/c/Postman)
- [Postman Community](https://community.postman.com/)

### API 테스팅 모범 사례
- [REST API Testing Best Practices](https://www.postman.com/collection/rest-api-testing-best-practices)
- [API Testing Strategy](https://www.postman.com/collection/api-testing-strategy)

---

**마지막 업데이트**: 2025년 1월 9일
**가이드 버전**: 2.5.0
**상태**: 모든 API 엔드포인트 테스트 가능
