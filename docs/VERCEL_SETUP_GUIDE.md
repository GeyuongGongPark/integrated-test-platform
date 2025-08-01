# Vercel 배포 설정 가이드

## 1단계: Vercel 계정 설정

### 1.1 Vercel 계정 생성
1. https://vercel.com 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭

### 1.2 백엔드 프로젝트 생성
1. **Import Git Repository** 선택
2. `GeyuongGongPark/integrated-test-platform` 선택
3. **Framework Preset**: `Other`
4. **Root Directory**: `backend`
5. **Build Command**: `pip install -r requirements.txt`
6. **Output Directory**: `(비워두기)`
7. **Install Command**: `(비워두기)`

### 1.3 프론트엔드 프로젝트 생성
1. **Import Git Repository** 선택 (같은 레포)
2. **Framework Preset**: `Create React App`
3. **Root Directory**: `frontend`
4. **Build Command**: `npm run build`
5. **Output Directory**: `build`
6. **Install Command**: `npm install`

## 2단계: 환경 변수 설정

### 2.1 백엔드 환경 변수
Vercel 대시보드 → Settings → Environment Variables에서 설정:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-hidden-paper-a1iuh28r-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require` |
| `FLASK_ENV` | `production` |
| `FLASK_APP` | `app.py` |

### 2.2 프론트엔드 환경 변수
| Variable | Value |
|----------|-------|
| `REACT_APP_API_URL` | `https://your-backend-domain.vercel.app` |

## 3단계: GitHub Secrets 설정

GitHub 레포지토리 → Settings → Secrets and variables → Actions에서 설정:

### 3.1 Vercel 토큰 생성
1. Vercel 대시보드 → Settings → Tokens
2. "Create Token" 클릭
3. 토큰 이름: `GitHub Actions`
4. 토큰 복사

### 3.2 GitHub Secrets 추가
| Secret Name | Value |
|-------------|-------|
| `VERCEL_TOKEN` | Vercel에서 생성한 토큰 |
| `VERCEL_ORG_ID` | Vercel 조직 ID (Settings → General에서 확인) |
| `VERCEL_PROJECT_ID_BACKEND` | 백엔드 프로젝트 ID (프로젝트 설정에서 확인) |
| `VERCEL_PROJECT_ID_FRONTEND` | 프론트엔드 프로젝트 ID (프로젝트 설정에서 확인) |
| `DATABASE_URL` | Neon PostgreSQL 연결 문자열 |

## 4단계: 도메인 설정

### 4.1 백엔드 도메인 확인
- Vercel 대시보드에서 백엔드 프로젝트의 도메인 확인
- 예: `https://test-platform-backend-xxx.vercel.app`

### 4.2 프론트엔드 환경 변수 업데이트
- `REACT_APP_API_URL`을 실제 백엔드 도메인으로 업데이트

## 5단계: 배포 테스트

### 5.1 수동 배포 테스트
1. GitHub에서 코드 푸시
2. GitHub Actions에서 워크플로우 실행 확인
3. Vercel 대시보드에서 배포 상태 확인

### 5.2 API 테스트
```bash
# 백엔드 헬스체크
curl https://your-backend-domain.vercel.app/health

# 프론트엔드 접속
open https://your-frontend-domain.vercel.app
```

## 6단계: 자동 배포 확인

### 6.1 GitHub Actions 워크플로우
- main 브랜치에 푸시할 때마다 자동 배포
- 테스트 → 백엔드 배포 → 프론트엔드 배포 순서

### 6.2 배포 로그 확인
- GitHub Actions 탭에서 워크플로우 실행 로그 확인
- Vercel 대시보드에서 배포 로그 확인

## 문제 해결

### 일반적인 문제들:
1. **빌드 실패**: requirements.txt 확인
2. **환경 변수 오류**: Vercel 환경 변수 설정 확인
3. **도메인 연결 오류**: CORS 설정 확인
4. **데이터베이스 연결 오류**: DATABASE_URL 확인

### 로그 확인 방법:
- Vercel 대시보드 → Functions → 로그 확인
- GitHub Actions → 워크플로우 → 로그 확인 