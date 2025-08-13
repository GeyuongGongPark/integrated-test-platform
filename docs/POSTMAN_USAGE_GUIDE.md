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
python app.py
```

### 3. Postman 컬렉션 Import
- `postman_collection.json` 파일을 Postman에 Import
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
```json
{
  "status": "healthy",
  "message": "Test Platform Backend is running",
  "version": "2.0.1",
  "timestamp": "2025-08-13T10:33:30.382318",
  "environment": "development",
  "database": {
    "status": "connected",
    "url_set": "Yes"
  }
}
```

### 2. 폴더 관리 API

#### GET /folders
- **Method**: GET
- **URL**: `{{base_url}}/folders`
- **Description**: 모든 폴더 목록 조회
- **Expected Response**: 200 OK
```json
[
  {
    "id": 1,
    "folder_name": "DEV 환경",
    "folder_type": "environment",
    "environment": "dev",
    "deployment_date": null,
    "parent_folder_id": null,
    "project_id": null,
    "created_at": "2025-08-03 11:22:59"
  }
]
```

#### GET /folders/tree
- **Method**: GET
- **URL**: `{{base_url}}/folders/tree`
- **Description**: 계층적 폴더 구조 조회
- **Expected Response**: 200 OK
```json
[
  {
    "id": 1,
    "folder_name": "DEV 환경",
    "folder_type": "environment",
    "environment": "dev",
    "type": "environment",
    "children": [
      {
        "id": 4,
        "folder_name": "2025-08-13",
        "folder_type": "deployment_date",
        "type": "deployment_date",
        "children": []
      }
    ]
  }
]
```

#### POST /folders
- **Method**: POST
- **URL**: `{{base_url}}/folders`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "folder_name": "새 폴더",
  "folder_type": "feature",
  "environment": "dev",
  "parent_folder_id": 4,
  "deployment_date": "2025-08-13"
}
```

### 3. 테스트 케이스 API

#### GET /testcases
- **Method**: GET
- **URL**: `{{base_url}}/testcases`
- **Description**: 모든 테스트 케이스 조회
- **Expected Response**: 200 OK

#### POST /testcases
- **Method**: POST
- **URL**: `{{base_url}}/testcases`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "name": "로그인 테스트",
  "description": "사용자 로그인 기능 테스트",
  "main_category": "인증",
  "sub_category": "로그인",
  "detail_category": "정상 로그인",
  "pre_condition": "사용자가 등록되어 있어야 함",
  "expected_result": "로그인이 성공적으로 완료되어야 함",
  "folder_id": 7,
  "environment": "dev"
}
```

#### GET /testcases/{id}
- **Method**: GET
- **URL**: `{{base_url}}/testcases/1`
- **Description**: 특정 테스트 케이스 조회
- **Expected Response**: 200 OK

#### PUT /testcases/{id}
- **Method**: PUT
- **URL**: `{{base_url}}/testcases/1`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "name": "수정된 로그인 테스트",
  "description": "수정된 설명"
}
```

#### DELETE /testcases/{id}
- **Method**: DELETE
- **URL**: `{{base_url}}/testcases/1`
- **Description**: 테스트 케이스 삭제
- **Expected Response**: 200 OK

### 4. 테스트 케이스 확장 API

#### PUT /testcases/{id}/status
- **Method**: PUT
- **URL**: `{{base_url}}/testcases/1/status`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "status": "Pass"
}
```

#### POST /testcases/upload
- **Method**: POST
- **URL**: `{{base_url}}/testcases/upload`
- **Headers**: `Content-Type: multipart/form-data`
- **Body**: `form-data`
  - Key: `file`, Type: `File`, Value: Excel 파일 선택

#### GET /testcases/download
- **Method**: GET
- **URL**: `{{base_url}}/testcases/download`
- **Description**: 테스트 케이스를 Excel 파일로 다운로드
- **Expected Response**: 200 OK

#### POST /testcases/{id}/execute
- **Method**: POST
- **URL**: `{{base_url}}/testcases/1/execute`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "environment": "dev",
  "parameters": {
    "base_url": "http://localhost:3000",
    "username": "testuser"
  }
}
```

### 5. 성능 테스트 API

#### GET /performance-tests
- **Method**: GET
- **URL**: `{{base_url}}/performance-tests`
- **Description**: 성능 테스트 목록 조회

#### POST /performance-tests
- **Method**: POST
- **URL**: `{{base_url}}/performance-tests`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "name": "로그인 성능 테스트",
  "description": "로그인 기능의 성능을 테스트합니다",
  "k6_script_path": "/test-scripts/performance/login/login.js",
  "environment": "dev",
  "parameters": "{\"vus\": 10, \"duration\": \"30s\"}"
}
```

### 6. 자동화 테스트 API

#### GET /automation-tests
- **Method**: GET
- **URL**: `{{base_url}}/automation-tests`
- **Description**: 자동화 테스트 목록 조회

#### POST /automation-tests
- **Method**: POST
- **URL**: `{{base_url}}/automation-tests`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "name": "로그인 자동화 테스트",
  "description": "로그인 기능을 자동화로 테스트합니다",
  "test_type": "playwright",
  "script_path": "/test-scripts/automation/login.spec.js",
  "environment": "dev",
  "parameters": "{\"base_url\": \"http://localhost:3000\"}"
}
```

### 7. 대시보드 API

#### GET /dashboard-summaries
- **Method**: GET
- **URL**: `{{base_url}}/dashboard-summaries`
- **Description**: 대시보드 요약 정보 조회

#### GET /testcases/summary/all
- **Method**: GET
- **URL**: `{{base_url}}/testcases/summary/all`
- **Description**: 전체 테스트 케이스 통계 조회

#### GET /test-executions
- **Method**: GET
- **URL**: `{{base_url}}/test-executions`
- **Description**: 테스트 실행 기록 조회

#### GET /testresults/{testcase_id}
- **Method**: GET
- **URL**: `{{base_url}}/testresults/1`
- **Description**: 특정 테스트 케이스의 결과 조회

### 8. 사용자 관리 API

#### GET /users
- **Method**: GET
- **URL**: `{{base_url}}/users`
- **Description**: 사용자 목록 조회

#### GET /users/current
- **Method**: GET
- **URL**: `{{base_url}}/users/current`
- **Description**: 현재 로그인한 사용자 정보

### 9. 프로젝트 관리 API

#### GET /projects
- **Method**: GET
- **URL**: `{{base_url}}/projects`
- **Description**: 프로젝트 목록 조회

## 🧪 테스트 시나리오

### 1. 기본 워크플로우 테스트
1. **Health Check**: 서버 상태 확인
2. **폴더 생성**: 새 폴더 생성
3. **테스트 케이스 생성**: 새 테스트 케이스 추가
4. **테스트 케이스 조회**: 생성된 테스트 케이스 확인
5. **테스트 케이스 수정**: 정보 업데이트
6. **테스트 케이스 삭제**: 정리

### 2. 파일 업로드/다운로드 테스트
1. **Excel 업로드**: 테스트 케이스 일괄 등록
2. **Excel 다운로드**: 데이터 내보내기
3. **데이터 검증**: 업로드된 데이터 확인

### 3. 성능 테스트 워크플로우
1. **성능 테스트 생성**: 새 성능 테스트 등록
2. **테스트 실행**: 성능 테스트 실행
3. **결과 확인**: 실행 결과 조회

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
- **원인**: Vercel 인증 설정
- **해결책**: 
  - `VERCEL_AUTH_DISABLED=true` 환경 변수 설정
  - Vercel Dashboard에서 인증 설정 변경

#### 3. CORS 오류
- **원인**: 프론트엔드와 백엔드 도메인 불일치
- **해결책**: 
  - 백엔드 CORS 설정 확인
  - 올바른 API URL 사용

#### 4. 404 Not Found
- **원인**: 잘못된 URL 또는 존재하지 않는 리소스
- **해결책**: 
  - URL 경로 확인
  - 리소스 ID 확인

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

### 권한 테스트
```javascript
// 권한 확인
pm.test("User has required permissions", function () {
    const response = pm.response.json();
    if (pm.request.method === 'DELETE') {
        pm.expect(response.status).to.not.equal('forbidden');
    }
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

**마지막 업데이트**: 2025년 8월 13일
**가이드 버전**: 2.0.1
**상태**: 모든 API 엔드포인트 테스트 가능
