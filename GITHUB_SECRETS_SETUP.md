# GitHub Secrets 설정 가이드

## 🔑 필요한 GitHub Secrets

GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음 secrets를 설정해야 합니다:

### 1. 데이터베이스 연결 정보
```
DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
DEV_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
PROD_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### 2. Vercel 설정 정보

#### Vercel Token 생성:
1. https://vercel.com/account/tokens 접속
2. "Create Token" 클릭
3. Token 이름: `github-actions-deploy`
4. Scope: Full Account 선택
5. 생성된 토큰을 복사

```
VERCEL_TOKEN=your_vercel_token_here
```

#### Vercel Organization ID 확인:
1. Vercel 대시보드 접속
2. Settings > General
3. Organization ID 복사

```
VERCEL_ORG_ID=your_org_id_here
```

#### Vercel Project ID 확인:

**백엔드 프로젝트 ID:**
1. Vercel에서 백엔드 프로젝트 생성
2. Project Settings > General
3. Project ID 복사

```
VERCEL_BACKEND_PROJECT_ID=your_backend_project_id_here
```

**프론트엔드 프로젝트 ID:**
1. Vercel에서 프론트엔드 프로젝트 생성
2. Project Settings > General
3. Project ID 복사

```
VERCEL_FRONTEND_PROJECT_ID=your_frontend_project_id_here
```

## 🚀 설정 단계

### 1. Vercel 프로젝트 생성

**백엔드 프로젝트:**
1. Vercel 대시보드에서 "New Project" 클릭
2. GitHub 저장소 연결
3. Framework Preset: Other
4. Root Directory: `backend`
5. Build Command: `pip install -r requirements.txt`
6. Output Directory: `.`
7. Install Command: `pip install -r requirements.txt`
8. 프로젝트 생성

**프론트엔드 프로젝트:**
1. Vercel 대시보드에서 "New Project" 클릭
2. GitHub 저장소 연결
3. Framework Preset: Create React App
4. Root Directory: `frontend`
5. Build Command: `npm run build`
6. Output Directory: `build`
7. 프로젝트 생성

### 2. 환경변수 설정

**백엔드 프로젝트 환경변수:**
```
FLASK_ENV=production
FLASK_APP=app.py
DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
DEV_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
PROD_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
SECRET_KEY=your-production-secret-key-here-2025
CORS_ORIGINS=https://integrated-test-platform-frontend.vercel.app
```

**프론트엔드 프로젝트 환경변수:**
```
REACT_APP_API_URL=https://integrated-test-platform-backend.vercel.app
```

### 3. GitHub Secrets 설정

GitHub 저장소의 Settings > Secrets and variables > Actions에서:

1. "New repository secret" 클릭
2. 각 secret 추가:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_BACKEND_PROJECT_ID`
   - `VERCEL_FRONTEND_PROJECT_ID`
   - `DATABASE_URL`
   - `DEV_DATABASE_URL`
   - `PROD_DATABASE_URL`

## ✅ 완료 후 확인

1. **GitHub Actions 실행:**
   - main 브랜치에 push하면 자동으로 실행
   - Actions 탭에서 진행 상황 확인

2. **배포 확인:**
   - 백엔드: `https://integrated-test-platform-backend.vercel.app`
   - 프론트엔드: `https://integrated-test-platform-frontend.vercel.app`

3. **API 테스트:**
   ```bash
   curl https://integrated-test-platform-backend.vercel.app/health
   ```

## 🔧 문제 해결

**배포 실패 시:**
1. GitHub Actions 로그 확인
2. Vercel 프로젝트 설정 확인
3. 환경변수 설정 확인
4. Neon 데이터베이스 연결 확인 