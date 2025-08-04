# GitHub Secrets 설정 가이드

## 🔐 필요한 GitHub Secrets

GitHub Actions가 Vercel에 배포하려면 다음 Secrets가 필요합니다:

### 1. Vercel 관련 Secrets

#### VERCEL_TOKEN
- Vercel 대시보드 → Settings → Tokens에서 생성
- 또는 CLI로 생성: `vercel token create`

#### VERCEL_ORG_ID
- Vercel CLI로 확인: `vercel org ls`
- 또는 Vercel 대시보드에서 확인

#### VERCEL_BACKEND_PROJECT_ID
- 백엔드 프로젝트 ID: `backend-alpha-amber-90`
- Vercel CLI로 확인: `vercel project ls`

#### VERCEL_FRONTEND_PROJECT_ID
- 프론트엔드 프로젝트 ID: `frontend-alpha-jade-15`
- Vercel CLI로 확인: `vercel project ls`

### 2. 데이터베이스 관련 Secrets

#### DATABASE_URL
- 프로덕션 데이터베이스 URL
- Neon PostgreSQL 또는 다른 데이터베이스

#### DEV_DATABASE_URL
- 개발용 데이터베이스 URL

#### PROD_DATABASE_URL
- 프로덕션용 데이터베이스 URL

## 🚀 설정 방법

### 1. GitHub Secrets 설정
1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. 위의 각 Secret을 추가

### 2. Vercel CLI로 정보 확인
```bash
# Vercel 로그인
vercel login

# 조직 ID 확인
vercel org ls

# 프로젝트 목록 확인
vercel project ls

# 토큰 생성
vercel token create
```

## 📋 현재 프로젝트 정보

- **Backend URL**: https://backend-alpha-amber-90.vercel.app
- **Frontend URL**: https://frontend-alpha-jade-15.vercel.app
- **Integrated Platform URL**: https://integrated-test-platform-m1mrr7don-gyeonggong-parks-projects.vercel.app

## ✅ 배포 확인

GitHub Actions가 성공적으로 실행되면:
1. 모든 테스트 통과
2. 백엔드 자동 배포
3. 프론트엔드 자동 배포
4. 배포 상태 메시지 출력

## 🔧 문제 해결

### Secrets 오류
- 모든 필수 Secrets가 설정되어 있는지 확인
- Vercel 토큰이 유효한지 확인

### 배포 실패
- Vercel 프로젝트 ID가 올바른지 확인
- 조직 ID가 올바른지 확인 