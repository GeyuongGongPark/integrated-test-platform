# 통합 테스트 플랫폼 테스팅 가이드

## 🚀 개요

이 문서는 통합 테스트 플랫폼의 다양한 테스트 방법과 절차를 설명합니다.

## 📋 테스트 유형별 가이드

### 1. API 테스트

#### Postman을 사용한 API 테스트
- **가이드**: [POSTMAN_USAGE_GUIDE.md](../POSTMAN_USAGE_GUIDE.md)
- **환경 설정**: 로컬 개발 환경 및 Vercel 프로덕션 환경
- **주요 API**: 폴더 관리, 테스트 케이스, 성능 테스트, 자동화 테스트

#### API 테스트 자동화
```bash
# 전체 API 테스트 스크립트 실행
cd test-scripts
./test-api-endpoints.sh

# 특정 API 테스트
./test-folders-api.sh
```

### 2. 성능 테스트 (K6)

#### K6 설치 및 설정
```bash
# macOS
brew install k6

# Windows
choco install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A364D5988D9F8E3FDC85C4C65
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

#### 성능 테스트 스크립트 구조
```
test-scripts/performance/
├── _ENV.js                    # 환경 설정
├── advice/                    # 법률 자문 관련 테스트
│   ├── advice_draft.js       # 자문 초안 테스트
│   ├── advice_lagel.js       # 자문 법률 검토 테스트
│   └── advice_process.js     # 자문 프로세스 테스트
├── clm/                      # CLM 관련 테스트
│   ├── multi/                # 계열사 테스트
│   │   ├── clm_draft_multi.js
│   │   ├── clm_esign_multi.js
│   │   └── clm_final_multi.js
│   └── nomerl/               # 단일 그룹 테스트
│       ├── clm_draft.js
│       ├── clm_esign.js
│       └── clm_final.js
├── litigation/               # 송무 관련 테스트
│   ├── litigation_draft.js   # 송무 초안 테스트
│   └── litigation_schedule.js # 송무 일정 테스트
├── dashboard/                # 대시보드 테스트
│   └── dashboard_setting.js  # 대시보드 설정 테스트
├── login/                    # 로그인 테스트
│   └── login_to_dashboard.js # 로그인 후 대시보드 이동 테스트
└── python/                   # Python 기반 K6 GUI
    ├── k6_gui.py            # K6 GUI 실행
    └── k6_options.py        # K6 옵션 설정
```

#### 성능 테스트 실행
```bash
# 기본 성능 테스트
k6 run test-scripts/performance/clm/nomerl/clm_draft.js

# 환경 변수와 함께 실행
k6 run -e BASE_URL=http://localhost:3000 test-scripts/performance/clm/nomerl/clm_draft.js

# 부하 테스트 (100명 동시 사용자, 30초)
k6 run --vus 100 --duration 30s test-scripts/performance/clm/nomerl/clm_draft.js
```

#### 성능 테스트 결과 분석
```bash
# JSON 형태로 결과 저장
k6 run --out json=results.json test-scripts/performance/clm/nomerl/clm_draft.js

# InfluxDB에 결과 저장
k6 run --out influxdb=http://localhost:8086/k6 test-scripts/performance/clm/nomerl/clm_draft.js
```

### 3. 자동화 테스트 (Playwright)

#### Playwright 설치 및 설정
```bash
# 프로젝트 디렉토리에서
npm init playwright@latest

# 또는 기존 프로젝트에 추가
npm install -D @playwright/test
npx playwright install
```

#### Playwright 테스트 구조
```
test-scripts/playwright/
├── sample-login.spec.js      # 샘플 로그인 테스트
├── e2e/                      # End-to-End 테스트
│   ├── login.spec.js         # 로그인 플로우 테스트
│   ├── dashboard.spec.js     # 대시보드 테스트
│   └── testcase.spec.js      # 테스트 케이스 관리 테스트
├── api/                      # API 테스트
│   ├── folders.spec.js       # 폴더 API 테스트
│   └── testcases.spec.js     # 테스트 케이스 API 테스트
└── visual/                   # 시각적 회귀 테스트
    └── screenshots.spec.js   # 스크린샷 비교 테스트
```

#### Playwright 테스트 실행
```bash
# 모든 테스트 실행
npx playwright test

# 특정 테스트 실행
npx playwright test sample-login.spec.js

# UI 모드로 실행
npx playwright test --ui

# 디버그 모드로 실행
npx playwright test --debug
```

#### Playwright 설정 파일 (playwright.config.js)
```javascript
const { defineConfig, devices } = require('k6/http');

module.exports = defineConfig({
  testDir: './test-scripts/playwright',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
```

### 4. 단위 테스트

#### Python 백엔드 테스트
```bash
# 테스트 실행
cd backend
python -m pytest tests/

# 특정 테스트 실행
python -m pytest tests/test_folders.py

# 커버리지와 함께 실행
python -m pytest --cov=. tests/
```

#### React 프론트엔드 테스트
```bash
# 테스트 실행
cd frontend
npm test

# 커버리지와 함께 실행
npm test -- --coverage

# 특정 테스트 실행
npm test -- TestCaseAPP.test.js
```

## 🔧 테스트 환경 설정

### 1. 로컬 개발 환경

#### 데이터베이스 설정
```bash
# MySQL Docker 컨테이너 실행
docker-compose up -d mysql

# 데이터베이스 초기화
docker exec -it test_management mysql -u root -p1q2w#E$R
source /docker-entrypoint-initdb.d/01-init.sql
source /docker-entrypoint-initdb.d/02-external-access.sql
```

#### 백엔드 서버 실행
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### 프론트엔드 서버 실행
```bash
cd frontend
npm install
npm start
```

### 2. Vercel 프로덕션 환경

#### 환경 변수 설정
```bash
# Vercel Dashboard에서 설정
DATABASE_URL=your-production-database-url
SECRET_KEY=your-production-secret-key
FLASK_ENV=production
VERCEL_AUTH_DISABLED=true
```

#### 배포 및 테스트
```bash
# 백엔드 배포
cd backend
vercel --prod

# API 테스트
curl https://your-backend-url.vercel.app/health
```

## 📊 테스트 결과 분석

### 1. 성능 테스트 결과

#### K6 결과 해석
```javascript
// K6 테스트 스크립트에 추가
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 }, // 2분간 100명까지 증가
    { duration: '5m', target: 100 }, // 5분간 100명 유지
    { duration: '2m', target: 0 },   // 2분간 0명까지 감소
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95%가 500ms 이내
    http_req_failed: ['rate<0.01'],   // 실패율 1% 미만
  },
};

export default function () {
  const response = http.get('http://localhost:3000');
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
}
```

#### 성능 메트릭
- **Response Time**: 응답 시간 (평균, 중간값, 95th percentile)
- **Throughput**: 초당 요청 수 (RPS)
- **Error Rate**: 오류율
- **Resource Usage**: CPU, 메모리 사용량

### 2. 자동화 테스트 결과

#### Playwright 결과 해석
```bash
# HTML 리포트 생성
npx playwright show-report

# JUnit XML 리포트
npx playwright test --reporter=junit

# JSON 리포트
npx playwright test --reporter=json
```

#### 테스트 메트릭
- **Test Duration**: 테스트 실행 시간
- **Success Rate**: 성공률
- **Screenshot Comparison**: 시각적 회귀 테스트 결과
- **Video Recording**: 테스트 실행 과정 녹화

## 🚨 문제 해결

### 1. 일반적인 테스트 문제

#### API 테스트 오류
- **500 Internal Server Error**: 백엔드 로그 확인, 데이터베이스 연결 상태 확인
- **401 Authentication Required**: Vercel 인증 설정 확인
- **CORS 오류**: 백엔드 CORS 설정 확인

#### 성능 테스트 오류
- **Connection Refused**: 대상 서버 실행 상태 확인
- **Timeout**: 네트워크 설정 및 서버 성능 확인
- **Memory Issues**: K6 메모리 설정 조정

#### 자동화 테스트 오류
- **Element Not Found**: 페이지 로딩 대기 시간 조정
- **Screenshot Mismatch**: 기준 이미지 업데이트
- **Browser Issues**: Playwright 브라우저 재설치

### 2. 디버깅 방법

#### 로그 확인
```bash
# 백엔드 로그
cd backend
python app.py

# Docker 로그
docker logs test_management

# K6 상세 로그
k6 run --verbose test-scripts/performance/clm/nomerl/clm_draft.js
```

#### 브라우저 디버깅
```bash
# Playwright 디버그 모드
npx playwright test --debug

# 브라우저 개발자 도구 활용
# Network 탭에서 API 요청/응답 확인
# Console 탭에서 JavaScript 오류 확인
```

## 📈 테스트 자동화

### 1. CI/CD 파이프라인

#### GitHub Actions 설정
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run API tests
      run: |
        cd backend
        python -m pytest tests/
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm install
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm test -- --passWithNoTests
```

### 2. 테스트 스케줄링

#### 정기 테스트 실행
```bash
# cron 작업 설정 (Linux/macOS)
# 매일 새벽 2시에 테스트 실행
0 2 * * * cd /path/to/project && ./run-daily-tests.sh

# Windows Task Scheduler
# 스케줄러에서 정기 작업 설정
```

## 📚 추가 리소스

### 학습 자료
- [K6 공식 문서](https://k6.io/docs/)
- [Playwright 공식 문서](https://playwright.dev/)
- [Postman 학습 센터](https://learning.postman.com/)

### 테스트 도구
- **API 테스트**: Postman, Insomnia, curl
- **성능 테스트**: K6, Apache JMeter, Gatling
- **자동화 테스트**: Playwright, Selenium, Cypress
- **모니터링**: Grafana, InfluxDB, Prometheus

---

**마지막 업데이트**: 2025년 8월 13일
**가이드 버전**: 2.0.1
**상태**: 모든 테스트 유형 지원 및 문서화 완료
