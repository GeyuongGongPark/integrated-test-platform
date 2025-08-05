# Integrated Test Platform 사용법 가이드

## 🚀 빠른 시작

### 1. 백엔드 실행
```bash
cd integrated-test-platform/backend
source venv/bin/activate
python app.py
```

### 2. 프론트엔드 실행
```bash
cd integrated-test-platform/frontend
npm install
npm start
```

### 3. 웹 브라우저에서 접속
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000

## 📋 주요 기능

### 웹 애플리케이션 테스트 관리

#### 프로젝트 관리
1. **프로젝트 생성**: 기본적으로 "테스트 프로젝트"가 자동 생성됩니다
2. **프로젝트 조회**: 프로젝트 목록을 확인할 수 있습니다

#### 테스트 케이스 관리
1. **테스트 케이스 생성**:
   - 프로젝트 선택
   - 대분류, 중분류, 소분류 입력
   - 전제 조건 입력
   - 설명 (기대 결과) 입력
   - 비고 입력

2. **테스트 케이스 조회**: 생성된 모든 테스트 케이스를 목록으로 확인

3. **테스트 케이스 상태 관리**:
   - N/T (Not Tested): 테스트하지 않음
   - Pass: 테스트 통과
   - Fail: 테스트 실패
   - N/A (Not Applicable): 해당 없음
   - Block: 차단됨

4. **테스트 케이스 삭제**: 불필요한 테스트 케이스 삭제

#### 폴더 관리
1. **폴더 생성**: 테스트 케이스를 체계적으로 관리하기 위한 폴더 생성
2. **폴더 구조**: 메인/서브/상세 카테고리로 체계적 관리
3. **폴더별 테스트 케이스**: 폴더별로 테스트 케이스 정리

#### 테스트 결과 관리
1. **테스트 결과 추가**: 특정 테스트 케이스에 대한 실행 결과 기록
2. **테스트 결과 조회**: 이전 실행 결과들을 확인
3. **노트 작성**: 테스트 실행 시 추가적인 메모 기록

### 성능 테스트 자동화

#### k6 성능 테스트 실행
```bash
cd integrated-test-platform/test-scripts/performance

# 로그인 테스트
k6 run login/login_to_dashboard.js

# CLM 테스트 (신규 계약)
k6 run -e DRAFT_TYPE=new clm/nomerl/clm_draft.js

# CLM 테스트 (변경 계약)
k6 run -e DRAFT_TYPE=change clm/nomerl/clm_draft.js

# 법률 자문 테스트
k6 run advice/advice_draft.js

# 송무 테스트
k6 run litigation/litigation_draft.js
```

#### 환경별 테스트 실행
```bash
# 개발 환경
k6 run -e NAME=alpha login/login_to_dashboard.js

# 프로덕션 환경
k6 run -e NAME=prod login/login_to_dashboard.js

# 다중 사용자 환경
k6 run -e NAME=multi1 login/login_to_dashboard.js
```

## 🎯 사용 시나리오

### 시나리오 1: 웹 애플리케이션 테스트
1. 웹 페이지에서 "Add Test Case" 섹션으로 이동
2. 프로젝트 선택 (기본 프로젝트 사용)
3. 분류 정보 입력:
   - Main Category: "로그인"
   - Sub Category: "사용자 인증"
   - Detail Category: "정상 로그인"
4. 전제 조건 입력: "사용자가 등록되어 있음"
5. 설명 입력: "올바른 아이디/비밀번호로 로그인 성공"
6. 비고 입력: "기본 테스트 케이스"
7. "Add Test Case" 버튼 클릭

### 시나리오 2: 성능 테스트 실행
1. 로그인 테스트 실행:
   ```bash
   cd test-scripts/performance
   k6 run login/login_to_dashboard.js
   ```

2. CLM 신규 계약 테스트 실행:
   ```bash
   k6 run -e DRAFT_TYPE=new -e EDITOR_USE=use clm/nomerl/clm_draft.js
   ```

3. 테스트 결과 확인:
   - `Result/` 폴더에서 HTML 리포트 확인
   - `screenshots/` 폴더에서 스크린샷 확인

### 시나리오 3: 환경별 테스트
1. 개발 환경 테스트:
   ```bash
   k6 run -e NAME=alpha login/login_to_dashboard.js
   ```

2. 프로덕션 환경 테스트:
   ```bash
   k6 run -e NAME=prod login/login_to_dashboard.js
   ```

### 시나리오 4: 대시보드 활용
1. **통합 대시보드**: 전체 테스트 현황 한눈에 확인
2. **성능 테스트 대시보드**: 성능 테스트 결과 시각화
3. **설정 관리**: 계정, 프로젝트, 폴더 설정 관리

## 🔧 환경 설정

### 환경 변수 설정
`test-scripts/performance/url/env_data.json`에서 환경별 설정을 관리합니다:

```json
[
  {
    "name": "prod",
    "base_url": "https://business.lawform.io",
    "email": "user@example.com",
    "password": "password"
  },
  {
    "name": "alpha",
    "base_url": "https://alpha.business.lfdev.io",
    "email": "user@example.com",
    "password": "password"
  }
]
```

### URL 설정
`test-scripts/performance/url/base.js`에서 API 엔드포인트를 관리합니다:

```javascript
export const URLS = {
    LOGIN: {
        HOME: `${BASE_URL}`,
        LOGIN: `${BASE_URL}/login`,
        DASHBOARD: `${BASE_URL}/dashboard`
    },
    CLM: {
        DRAFT: `${BASE_URL}/clm/draft`,
        REVIEW: `${BASE_URL}/clm/review`
    }
};
```

### 셀렉터 설정
`test-scripts/performance/url/config.js`에서 UI 요소 셀렉터를 관리합니다:

```javascript
export const SELECTORS = {
    LOGIN: {
        EMAIL_INPUT: 'input[type="email"]',
        PASSWORD_INPUT: 'input[type="password"]',
        SUBMIT_BUTTON: 'button[type="submit"]'
    }
};
```

## 🔧 문제 해결

### 서버가 시작되지 않는 경우
```bash
# 포트 확인
lsof -i :8000  # 백엔드 포트
lsof -i :3000  # 프론트엔드 포트

# 프로세스 종료
kill -9 [PID]
```

### 데이터베이스 오류가 발생하는 경우
```bash
cd backend
rm -f test_management.db
source venv/bin/activate
python app.py
```

### 가상환경 오류가 발생하는 경우
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### k6 테스트 실행 오류
```bash
# k6 설치 확인
k6 version

# 브라우저 설치 확인
k6 run --browser login/login_to_dashboard.js
```

## 📊 API 테스트

### 프로젝트 조회
```bash
curl http://localhost:8000/projects
```

### 테스트 케이스 생성
```bash
curl -X POST http://localhost:8000/testcases \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "main_category": "로그인",
    "sub_category": "사용자 인증",
    "detail_category": "정상 로그인",
    "pre_condition": "사용자가 등록되어 있음",
    "description": "올바른 아이디/비밀번호로 로그인 성공",
    "result_status": "N/T",
    "remark": "기본 테스트 케이스"
  }'
```

### 테스트 케이스 조회
```bash
curl http://localhost:8000/testcases
```

### 폴더 관리
```bash
# 폴더 생성
curl -X POST http://localhost:8000/folders \
  -H "Content-Type: application/json" \
  -d '{
    "name": "로그인 테스트",
    "description": "로그인 관련 테스트 케이스"
  }'

# 폴더 조회
curl http://localhost:8000/folders
```

## 🎨 UI 특징

### 웹 애플리케이션
- **반응형 디자인**: 다양한 화면 크기에 대응
- **직관적인 인터페이스**: 드래그 앤 드롭, 드롭다운 메뉴
- **실시간 업데이트**: 상태 변경 시 즉시 반영
- **색상 코딩**: 테스트 결과에 따른 색상 구분
  - Pass: 초록색
  - Fail: 빨간색
  - Block: 노란색
  - N/T, N/A: 회색

### 대시보드 기능
- **통합 대시보드**: 전체 테스트 현황 시각화
- **성능 지표**: 응답 시간, 처리량, 에러율 표시
- **실시간 모니터링**: 테스트 실행 상태 실시간 확인
- **설정 관리**: 계정, 프로젝트, 폴더 설정

### 성능 테스트 결과
- **HTML 리포트**: 상세한 테스트 결과 리포트
- **스크린샷 자동 저장**: 각 단계별 스크린샷 저장
- **타임스탬프**: 정확한 실행 시간 기록
- **환경 정보**: 테스트 실행 환경 정보 포함

## 📈 향후 개선 사항

### 웹 애플리케이션
1. **사용자 인증**: 로그인/회원가입 시스템
2. **고급 권한 관리**: 역할 기반 접근 제어
3. **실시간 알림**: 테스트 완료/실패 알림
4. **보고서 생성**: 테스트 결과를 PDF/Excel로 내보내기
5. **JIRA 연동**: 버그 추적 시스템과 연동

### 성능 테스트
1. **병렬 실행**: 여러 테스트를 동시에 실행
2. **부하 테스트**: 대용량 트래픽 테스트
3. **모니터링**: 실시간 성능 모니터링
4. **알림 시스템**: 테스트 실패 시 알림
5. **CI/CD 연동**: 자동화된 테스트 파이프라인

### 자동화 기능
1. **테스트 스케줄링**: 정기적인 테스트 자동 실행
2. **API 문서 자동 생성**: 테스트 결과 기반 문서 생성
3. **모바일 앱**: 모바일 환경 지원

## 📚 추가 문서

- [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md): 통합 계획 문서
- [LFBZ_performance_README.md](LFBZ_performance_README.md): 성능 테스트 상세 가이드
- [DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md): 배포 성공 가이드 