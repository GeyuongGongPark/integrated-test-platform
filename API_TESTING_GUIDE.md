# 통합 테스트 플랫폼 API 테스트 가이드

## 개요
이 문서는 통합 테스트 플랫폼의 API를 Postman으로 테스트하기 위한 가이드입니다.

## 준비사항

### 1. 백엔드 서버 실행
```bash
cd backend
python app.py
```

### 2. Postman 컬렉션 import
1. Postman을 실행합니다
2. `Import` 버튼을 클릭합니다
3. `postman_collection.json` 파일을 선택하여 import합니다

### 3. 환경 변수 설정
- `base_url`: `http://localhost:8000` (기본값)
- 프로덕션 환경의 경우: `https://your-domain.com`

## API 엔드포인트 목록

### 1. Health Check
- **GET** `/health`
- 서버 상태 확인

### 2. 사용자 관리 (Users)

#### 2.1 사용자 목록 조회
- **GET** `/users`
- 모든 사용자 정보 조회

#### 2.2 사용자 생성
- **POST** `/users`
- 새 사용자 생성
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "role": "User",
  "password": "1q2w#E$R"
}
```

#### 2.3 사용자 정보 수정
- **PUT** `/users/{user_id}`
- 사용자 정보 업데이트
```json
{
  "username": "updateduser",
  "email": "updated@example.com",
  "role": "Administrator"
}
```

#### 2.4 사용자 삭제
- **DELETE** `/users/{user_id}`
- 사용자 삭제

#### 2.5 현재 사용자 조회
- **GET** `/users/current`
- 현재 로그인한 사용자 정보

#### 2.6 비밀번호 변경
- **PUT** `/users/{user_id}/change-password`
- 사용자 비밀번호 변경
```json
{
  "current_password": "1q2w#E$R",
  "new_password": "newpassword123"
}
```

### 3. 프로젝트 관리 (Projects)

#### 3.1 프로젝트 목록 조회
- **GET** `/projects`
- 모든 프로젝트 조회

#### 3.2 프로젝트 생성
- **POST** `/projects`
- 새 프로젝트 생성
```json
{
  "name": "새 프로젝트",
  "description": "새로운 테스트 프로젝트입니다."
}
```

### 4. 테스트 케이스 관리 (Test Cases)

#### 4.1 테스트 케이스 목록 조회
- **GET** `/testcases`
- 모든 테스트 케이스 조회

#### 4.2 특정 테스트 케이스 조회
- **GET** `/testcases/{id}`
- ID로 특정 테스트 케이스 조회

#### 4.3 테스트 케이스 생성
- **POST** `/testcases`
- 새 테스트 케이스 생성
```json
{
  "project_id": 1,
  "main_category": "로그인",
  "sub_category": "일반 로그인",
  "detail_category": "정상 로그인",
  "pre_condition": "사용자가 등록되어 있어야 함",
  "expected_result": "로그인이 성공적으로 완료되어야 함",
  "result_status": "N/T",
  "remark": "테스트 케이스 예시",
  "folder_id": 1,
  "automation_code_path": "/test-scripts/login/login.js",
  "automation_code_type": "k6",
  "environment": "dev"
}
```

#### 4.4 테스트 케이스 수정
- **PUT** `/testcases/{id}`
- 테스트 케이스 정보 업데이트

#### 4.5 테스트 케이스 상태 변경
- **PUT** `/testcases/{id}/status`
- 테스트 케이스 상태만 변경
```json
{
  "result_status": "Pass"
}
```

#### 4.6 테스트 케이스 삭제
- **DELETE** `/testcases/{id}`
- 테스트 케이스 삭제

#### 4.7 Excel 파일 업로드
- **POST** `/testcases/upload`
- Excel 파일로 테스트 케이스 일괄 업로드
- Content-Type: `multipart/form-data`
- 파일 필드명: `file`

#### 4.8 Excel 파일 다운로드
- **GET** `/testcases/download`
- 테스트 케이스를 Excel 파일로 다운로드

#### 4.9 자동화 코드 실행
- **POST** `/testcases/{id}/execute`
- 테스트 케이스의 자동화 코드 실행
```json
{
  "environment": "dev",
  "parameters": {
    "base_url": "http://localhost:3000",
    "username": "testuser",
    "password": "testpass"
  }
}
```

#### 4.10 테스트 결과 조회
- **GET** `/testresults/{test_case_id}`
- 특정 테스트 케이스의 결과 조회

#### 4.11 테스트 결과 생성
- **POST** `/testresults`
- 테스트 결과 생성
```json
{
  "test_case_id": 1,
  "result": "Pass",
  "execution_time": 5.2,
  "environment": "dev",
  "executed_by": "testuser",
  "notes": "테스트 성공"
}
```

#### 4.12 스크린샷 조회
- **GET** `/testcases/{id}/screenshots`
- 테스트 케이스의 스크린샷 목록 조회

### 5. 성능 테스트 관리 (Performance Tests)

#### 5.1 성능 테스트 목록 조회
- **GET** `/performance-tests`
- 모든 성능 테스트 조회

#### 5.2 특정 성능 테스트 조회
- **GET** `/performance-tests/{id}`
- ID로 특정 성능 테스트 조회

#### 5.3 성능 테스트 생성
- **POST** `/performance-tests`
- 새 성능 테스트 생성
```json
{
  "name": "로그인 성능 테스트",
  "description": "로그인 기능의 성능을 테스트합니다.",
  "k6_script_path": "/test-scripts/performance/login/login.js",
  "environment": "prod",
  "parameters": {
    "vus": 10,
    "duration": "30s",
    "base_url": "https://example.com"
  }
}
```

#### 5.4 성능 테스트 수정
- **PUT** `/performance-tests/{id}`
- 성능 테스트 정보 업데이트

#### 5.5 성능 테스트 삭제
- **DELETE** `/performance-tests/{id}`
- 성능 테스트 삭제

#### 5.6 성능 테스트 실행
- **POST** `/performance-tests/{id}/execute`
- 성능 테스트 실행
```json
{
  "environment_vars": {
    "BASE_URL": "https://example.com",
    "VUS": 10,
    "DURATION": "30s"
  }
}
```

#### 5.7 성능 테스트 결과 조회
- **GET** `/performance-tests/{id}/results`
- 성능 테스트 결과 조회

#### 5.8 테스트 실행 기록 조회
- **GET** `/test-executions`
- 모든 테스트 실행 기록 조회

#### 5.9 테스트 실행 기록 생성
- **POST** `/test-executions`
- 테스트 실행 기록 생성
```json
{
  "test_type": "performance",
  "test_id": 1,
  "environment": "prod",
  "executed_by": "testuser",
  "status": "completed",
  "result_summary": {
    "total_requests": 1000,
    "success_rate": 95.5,
    "avg_response_time": 250
  }
}
```

### 6. 자동화 테스트 관리 (Automation Tests)

#### 6.1 자동화 테스트 목록 조회
- **GET** `/automation-tests`
- 모든 자동화 테스트 조회

#### 6.2 특정 자동화 테스트 조회
- **GET** `/automation-tests/{id}`
- ID로 특정 자동화 테스트 조회

#### 6.3 자동화 테스트 생성
- **POST** `/automation-tests`
- 새 자동화 테스트 생성
```json
{
  "name": "로그인 자동화 테스트",
  "description": "로그인 기능을 자동화로 테스트합니다.",
  "test_type": "playwright",
  "script_path": "/test-scripts/automation/login.spec.js",
  "environment": "dev",
  "parameters": "{\"base_url\": \"http://localhost:3000\", \"username\": \"testuser\", \"password\": \"testpass\"}"
}
```

#### 6.4 자동화 테스트 수정
- **PUT** `/automation-tests/{id}`
- 자동화 테스트 정보 업데이트

#### 6.5 자동화 테스트 삭제
- **DELETE** `/automation-tests/{id}`
- 자동화 테스트 삭제

#### 6.6 자동화 테스트 실행
- **POST** `/automation-tests/{id}/execute`
- 자동화 테스트 실행
```json
{
  "environment": "dev",
  "parameters": {
    "base_url": "http://localhost:3000",
    "username": "testuser",
    "password": "testpass"
  }
}
```

#### 6.7 자동화 테스트 결과 조회
- **GET** `/automation-tests/{id}/results`
- 자동화 테스트 결과 조회

#### 6.8 자동화 테스트 결과 상세 조회
- **GET** `/automation-tests/{id}/results/{result_id}`
- 특정 자동화 테스트 결과 상세 조회

### 7. 폴더 관리 (Folders)

#### 7.1 폴더 목록 조회
- **GET** `/folders`
- 모든 폴더 조회

#### 7.2 특정 폴더 조회
- **GET** `/folders/{id}`
- ID로 특정 폴더 조회

#### 7.3 폴더 생성
- **POST** `/folders`
- 새 폴더 생성
```json
{
  "folder_name": "개발 환경",
  "parent_folder_id": null,
  "folder_type": "environment",
  "environment": "dev",
  "deployment_date": "2025-01-15"
}
```

#### 7.4 폴더 수정
- **PUT** `/folders/{id}`
- 폴더 정보 업데이트

#### 7.5 폴더 삭제
- **DELETE** `/folders/{id}`
- 폴더 삭제

#### 7.6 폴더 트리 조회
- **GET** `/folders/tree`
- 폴더 계층 구조 조회

### 8. 대시보드 (Dashboard)

#### 8.1 대시보드 요약 목록 조회
- **GET** `/dashboard-summaries`
- 모든 대시보드 요약 조회

#### 8.2 대시보드 요약 생성
- **POST** `/dashboard-summaries`
- 새 대시보드 요약 생성
```json
{
  "environment": "dev",
  "total_tests": 100,
  "passed_tests": 85,
  "failed_tests": 10,
  "skipped_tests": 5,
  "pass_rate": 85.0
}
```

#### 8.3 대시보드 요약 수정
- **PUT** `/dashboard-summaries/{id}`
- 대시보드 요약 업데이트

#### 8.4 대시보드 요약 삭제
- **DELETE** `/dashboard-summaries/{id}`
- 대시보드 요약 삭제

#### 8.5 환경별 테스트 결과 요약
- **GET** `/test-results/summary/{environment}`
- 특정 환경의 테스트 결과 요약

#### 8.6 환경별 테스트 케이스 요약
- **GET** `/testcases/summary/{environment}`
- 특정 환경의 테스트 케이스 상태 요약

#### 8.7 전체 테스트 케이스 요약
- **GET** `/testcases/summary/all`
- 모든 환경의 테스트 케이스 상태 요약

## 테스트 시나리오

### 1. 기본 워크플로우 테스트
1. Health Check로 서버 상태 확인
2. 프로젝트 생성
3. 폴더 생성
4. 테스트 케이스 생성
5. 테스트 케이스 실행
6. 결과 확인

### 2. 성능 테스트 워크플로우
1. 성능 테스트 생성
2. 성능 테스트 실행
3. 결과 확인

### 3. 자동화 테스트 워크플로우
1. 자동화 테스트 생성
2. 자동화 테스트 실행
3. 결과 확인

## 응답 코드

- `200`: 성공
- `201`: 생성 성공
- `400`: 잘못된 요청
- `404`: 리소스를 찾을 수 없음
- `500`: 서버 내부 오류

## 주의사항

1. **CORS 설정**: 모든 API는 CORS가 설정되어 있어 브라우저에서도 호출 가능합니다.
2. **인증**: 현재 버전에서는 인증이 간소화되어 있습니다.
3. **파일 업로드**: Excel 파일 업로드 시 파일 형식을 확인하세요.
4. **환경 변수**: `base_url` 변수를 적절히 설정하세요.

## 문제 해결

### 서버 연결 오류
- 백엔드 서버가 실행 중인지 확인
- 포트 8000이 사용 가능한지 확인
- 방화벽 설정 확인

### 데이터베이스 오류
- PostgreSQL 데이터베이스 연결 확인
- 환경 변수 설정 확인
- 데이터베이스 마이그레이션 실행

### 파일 업로드 오류
- 파일 형식이 Excel인지 확인
- 파일 크기 제한 확인
- 파일 경로 권한 확인
