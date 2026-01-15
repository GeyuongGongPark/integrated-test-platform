# LFBZ_auto
LFBZ 자동화 테스트 레포

## Node.js 설정 및 JavaScript 파일 실행 방법

### 1. Node.js 설치 확인
```bash
node --version
npm --version
```

### 2. 의존성 설치
```bash
npm install
```

### 3. JavaScript 파일 실행 방법

#### 방법 1: Node.js로 직접 실행 (일반 JS 파일)
```bash
# ES modules 형식으로 실행
node 파일명.js

# 예시
node Account/Account_env.js
```

#### 방법 2: Playwright 테스트 실행
```bash
# 모든 테스트 실행
npm test
# 또는
npx playwright test

# 헤드리스 모드로 브라우저 보이게 실행
npm run test:headed

# UI 모드로 실행
npm run test:ui

# 디버그 모드로 실행
npm run test:debug

# 특정 테스트 파일만 실행
npx playwright test Test_Code/CLM/clm_draft.test.js
```

#### 방법 3: 특정 디렉토리의 테스트 실행
```bash
npx playwright test Test_Code/
```

### 4. 환경변수 설정
`.env` 파일을 프로젝트 루트에 생성하고 필요한 환경변수를 설정하세요:
```bash
ACCOUNT=blue
SLACK_WEBHOOK_URL=your_webhook_url
```

## Python venv 설정 방법

### 1. 가상환경 생성
```bash
# 프로젝트 루트 디렉토리에서 실행
python3 -m venv venv
```

### 2. 가상환경 활성화
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. Playwright 브라우저 설치
```bash
playwright install
```

### 5. 가상환경 비활성화 (작업 완료 후)
```bash
deactivate
```

## 의존성 패키지
- `playwright`: 브라우저 자동화
- `pytest`: 테스트 프레임워크
- `pytest-playwright`: Playwright와 pytest 통합
- `python-slugify`: 문자열 변환 유틸리티
- `python-dotenv`: 환경변수 관리
