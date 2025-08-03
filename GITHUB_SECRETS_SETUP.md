# GitHub Secrets 설정 가이드

## 필수 GitHub Secrets 설정

GitHub Actions에서 Vercel 배포를 위해 다음 Secrets를 설정해야 합니다:

### 1. Vercel 토큰 생성
1. [Vercel Dashboard](https://vercel.com/account/tokens)에서 새 토큰 생성
2. 토큰 이름: `github-actions-deploy`
3. 토큰을 복사하여 GitHub Secrets에 저장

### 2. Vercel Organization ID 찾기
1. [Vercel Dashboard](https://vercel.com/account)에서 Organization ID 확인
2. 또는 터미널에서: `vercel whoami` 실행

### 3. Vercel 프로젝트 생성 및 ID 찾기

#### 백엔드 프로젝트:
1. Vercel Dashboard에서 새 프로젝트 생성
2. 프로젝트 이름: `integrated-test-platform-backend`
3. Framework Preset: `Other`
4. Root Directory: `backend`
5. Build Command: `pip install -r requirements.txt`
6. Output Directory: `(비워두기)`
7. Install Command: `(비워두기)`

#### 프론트엔드 프로젝트:
1. Vercel Dashboard에서 새 프로젝트 생성
2. 프로젝트 이름: `integrated-test-platform-frontend`
3. Framework Preset: `Create React App`
4. Root Directory: `frontend`
5. Build Command: `npm run build`
6. Output Directory: `build`
7. Install Command: `npm install`

### 4. GitHub Secrets 설정

GitHub 저장소 → Settings → Secrets and variables → Actions에서 다음 Secrets 추가:

```
VERCEL_TOKEN = [Vercel 토큰]
VERCEL_ORG_ID = [Organization ID]
VERCEL_BACKEND_PROJECT_ID = [백엔드 프로젝트 ID]
VERCEL_FRONTEND_PROJECT_ID = [프론트엔드 프로젝트 ID]
DATABASE_URL = [Neon PostgreSQL URL]
DEV_DATABASE_URL = [Neon Development URL]
PROD_DATABASE_URL = [Neon Production URL]
```

### 5. 프로젝트 ID 확인 방법

각 Vercel 프로젝트의 Settings → General에서 Project ID를 확인할 수 있습니다.

### 6. 환경 변수 설정

각 Vercel 프로젝트의 Settings → Environment Variables에서 다음 설정:

#### 백엔드 프로젝트:
```
DATABASE_URL = [Neon PostgreSQL URL]
DEV_DATABASE_URL = [Neon Development URL]
PROD_DATABASE_URL = [Neon Production URL]
FLASK_ENV = production
```

#### 프론트엔드 프로젝트:
```
REACT_APP_API_URL = https://[백엔드-프로젝트-URL].vercel.app
```

### 7. 배포 확인

모든 설정이 완료되면:
1. GitHub에 코드 푸시
2. GitHub Actions에서 배포 진행 상황 확인
3. Vercel Dashboard에서 배포 상태 확인

### 문제 해결

만약 `VERCEL_PROJECT_ID` 오류가 발생하면:
1. GitHub Secrets에서 `VERCEL_FRONTEND_PROJECT_ID`가 올바르게 설정되었는지 확인
2. Vercel 프로젝트가 올바르게 생성되었는지 확인
3. 프로젝트 ID가 정확한지 확인 