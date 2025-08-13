# Integrated Test Platform

## 프로젝트 개요
통합 테스트 플랫폼으로, 성능 테스트, 자동화 테스트, 테스트 케이스 관리 등을 제공합니다.

## 환경 변수 설정

### Vercel 환경에서 필요한 환경 변수

백엔드가 Vercel에서 정상 작동하려면 다음 환경 변수들을 설정해야 합니다:

```bash
# Flask 설정
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# 데이터베이스 설정 (Vercel 환경)
DATABASE_URL=mysql+pymysql://username:password@host:port/database_name?ssl_mode=VERIFY_IDENTITY

# CORS 설정 (Vercel 환경)
CORS_ORIGINS=https://frontend-alpha-ten-pi.vercel.app,https://frontend-alpha-jade-15.vercel.app

# Vercel 환경 변수 (자동 설정됨)
VERCEL=1
VERCEL_URL=https://your-backend.vercel.app
```

### 로컬 개발 환경
로컬에서는 기본 설정을 사용하며, 별도 환경 변수 설정이 필요하지 않습니다.

## CORS 문제 해결

### 문제 상황
프론트엔드에서 백엔드 API 호출 시 CORS 정책 위반 오류가 발생하는 경우:

```
Access to XMLHttpRequest at 'https://backend-alpha-liard.vercel.app/health' 
from origin 'https://frontend-alpha-ten-pi.vercel.app' has been blocked by CORS policy
```

### 해결 방법

1. **환경 변수 확인**: Vercel 대시보드에서 `DATABASE_URL`과 `CORS_ORIGINS` 설정
2. **백엔드 재배포**: 환경 변수 변경 후 백엔드 재배포
3. **CORS 설정 확인**: `utils/cors.py`의 `setup_cors` 함수가 Vercel 환경에서만 실행되는지 확인

## 배포 가이드

### 백엔드 배포 (Vercel)
1. 환경 변수 설정
2. `vercel.json` 설정 확인
3. Git push로 자동 배포

### 프론트엔드 배포 (Vercel)
1. `config.js`에서 API URL 확인
2. Git push로 자동 배포

## 개발 환경 실행

### 백엔드 (로컬)
```bash
cd backend
python app.py
```

### 프론트엔드 (로컬)
```bash
cd frontend
npm start
```

## 문제 해결

### 데이터를 불러올 수 없는 경우
1. 백엔드 헬스체크: `/health` 엔드포인트 접근 확인
2. CORS 설정: 브라우저 개발자 도구에서 CORS 오류 확인
3. 환경 변수: Vercel 환경 변수 설정 확인
4. 로그 확인: Vercel 함수 로그에서 오류 메시지 확인 