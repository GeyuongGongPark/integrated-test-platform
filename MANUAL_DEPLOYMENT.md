# Vercel 수동 배포 가이드

## 현재 상태
- ✅ GitHub Actions: 테스트 자동화 완료
- 🔄 Vercel 배포: 수동 설정 필요

## Vercel 수동 배포 방법

### 1단계: Vercel 계정 설정
1. https://vercel.com 접속
2. GitHub 계정으로 로그인

### 2단계: 백엔드 프로젝트 생성
1. **New Project** 클릭
2. **Import Git Repository** 선택
3. `GeyuongGongPark/integrated-test-platform` 선택
4. **Framework Preset**: `Other`
5. **Root Directory**: `backend`
6. **Build Command**: `pip install -r requirements.txt`
7. **Output Directory**: `(비워두기)`
8. **Install Command**: `(비워두기)`

### 3단계: 프론트엔드 프로젝트 생성
1. **New Project** 클릭
2. **Import Git Repository** 선택 (같은 레포)
3. **Framework Preset**: `Create React App`
4. **Root Directory**: `frontend`
5. **Build Command**: `npm run build`
6. **Output Directory**: `build`
7. **Install Command**: `npm install`

### 4단계: 환경 변수 설정

#### 백엔드 환경 변수
- `DATABASE_URL`: `sqlite:///test_management.db`
- `FLASK_ENV`: `production`
- `FLASK_APP`: `app.py`

#### 프론트엔드 환경 변수
- `REACT_APP_API_URL`: `https://your-backend-domain.vercel.app`

### 5단계: 배포 확인
1. **백엔드 헬스체크**: `https://your-backend-domain.vercel.app/health`
2. **프론트엔드 접속**: `https://your-frontend-domain.vercel.app`

## 자동화된 워크플로우
- **코드 푸시** → **GitHub Actions 테스트** → **Vercel 자동 배포**
- 테스트 통과 시 Vercel에서 자동으로 새 버전 배포

## 문제 해결
- **배포 실패**: Vercel 대시보드에서 로그 확인
- **환경 변수**: Settings → Environment Variables에서 확인
- **도메인**: 배포 후 자동 생성된 도메인 확인 