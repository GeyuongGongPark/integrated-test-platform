# 🚂 Railway 백엔드 배포 가이드

## 📋 단계별 배포 방법

### 1. Railway 계정 생성
1. [Railway](https://railway.app) 접속
2. "Sign up" 클릭
3. GitHub 계정으로 로그인
4. 무료 플랜 선택

### 2. 프로젝트 생성
1. "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. GitHub 저장소 연결
4. 프로젝트 이름: `test-platform-backend`

### 3. 환경 변수 설정
Railway 대시보드에서 다음 환경 변수들을 설정:

```bash
# 데이터베이스 설정
DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-hidden-paper-a1iuh28r-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# 보안 설정
SECRET_KEY=your-production-secret-key-here

# 환경 설정
FLASK_ENV=production
FLASK_APP=app.py

# CORS 설정
CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:3000

# 파일 업로드 설정
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
```

### 4. 자동 배포 설정
1. GitHub 저장소와 연결
2. main 브랜치에 push하면 자동 배포
3. 배포 상태 확인

### 5. 도메인 설정
1. Railway에서 제공하는 도메인 확인
2. 커스텀 도메인 설정 (선택사항)

## 🔧 배포 확인

### 1. 배포 상태 확인
```bash
# Railway CLI 사용
railway status
```

### 2. 로그 확인
```bash
railway logs
```

### 3. API 테스트
```bash
# 배포된 URL로 API 테스트
curl https://your-railway-app.railway.app/projects
```

## 🚨 문제 해결

### 배포 실패 시
1. **로그 확인**: Railway 대시보드에서 로그 확인
2. **환경 변수 확인**: 모든 필수 환경 변수 설정
3. **의존성 확인**: requirements.txt 파일 확인

### 일반적인 오류
- `ModuleNotFoundError`: requirements.txt에 패키지 추가
- `Database connection failed`: DATABASE_URL 확인
- `CORS error`: CORS_ORIGINS 설정 확인

## 📊 모니터링

### 1. Railway 대시보드
- 배포 상태 모니터링
- 리소스 사용량 확인
- 로그 확인

### 2. 성능 모니터링
- 응답 시간 확인
- 에러율 모니터링
- 트래픽 확인

## 🔒 보안 설정

### 1. 환경 변수 보안
- 민감한 정보는 Railway 환경 변수로 관리
- Git에 커밋하지 않음
- 프로덕션에서는 강력한 SECRET_KEY 사용

### 2. CORS 설정
- 프론트엔드 도메인만 허용
- 개발 환경과 프로덕션 환경 분리

## 🚀 다음 단계

Railway 배포가 완료되면:
1. Vercel 프론트엔드 배포
2. Cloudinary 파일 저장소 설정
3. 전체 시스템 통합 테스트

## 💰 비용 정보

### Railway 무료 플랜
- **월 $5 크레딧** 제공
- **소규모 프로젝트**에 적합
- **자동 배포** 지원 