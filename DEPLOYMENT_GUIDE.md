# 🚀 클라우드 배포 가이드

## 📋 개요
이 가이드는 Integrated Test Platform을 클라우드 환경에 배포하는 방법을 설명합니다.

## 🗄️ 1. 데이터베이스 클라우드 설정

### PlanetScale (추천)
1. [PlanetScale](https://planetscale.com) 계정 생성
2. 새 데이터베이스 생성
3. 연결 정보 복사
4. 환경 변수 설정:
   ```bash
   DATABASE_URL=mysql://username:password@host:port/database_name
   ```

### AWS RDS
1. AWS 콘솔에서 RDS 인스턴스 생성
2. 보안 그룹 설정 (포트 3306)
3. 연결 정보 환경 변수 설정

## 🖥️ 2. 백엔드 배포

### Heroku 배포
1. Heroku CLI 설치
2. Heroku 앱 생성:
   ```bash
   heroku create your-app-name
   ```
3. 환경 변수 설정:
   ```bash
   heroku config:set DATABASE_URL=your-database-url
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set FLASK_ENV=production
   ```
4. 배포:
   ```bash
   git push heroku main
   ```

### Railway 배포
1. [Railway](https://railway.app) 계정 생성
2. GitHub 저장소 연결
3. 환경 변수 설정
4. 자동 배포 활성화

## 🌐 3. 프론트엔드 배포

### Vercel 배포 (추천)
1. [Vercel](https://vercel.com) 계정 생성
2. GitHub 저장소 연결
3. 환경 변수 설정:
   ```
   REACT_APP_API_URL=https://your-backend-url.com
   ```
4. 자동 배포 활성화

### Netlify 배포
1. [Netlify](https://netlify.com) 계정 생성
2. GitHub 저장소 연결
3. 빌드 설정:
   - Build command: `npm run build`
   - Publish directory: `build`
4. 환경 변수 설정

## 📁 4. 파일 저장소 설정

### AWS S3 설정
1. S3 버킷 생성
2. IAM 사용자 생성 및 권한 설정
3. 환경 변수 설정:
   ```bash
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_S3_BUCKET=your-bucket-name
   AWS_REGION=ap-northeast-2
   ```

### Cloudinary 설정
1. [Cloudinary](https://cloudinary.com) 계정 생성
2. 환경 변수 설정:
   ```bash
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

## 🔧 5. 환경 변수 설정

### 백엔드 환경 변수
```bash
# 데이터베이스
DATABASE_URL=mysql://username:password@host:port/database_name

# 보안
SECRET_KEY=your-secret-key-here

# 환경
FLASK_ENV=production

# CORS
CORS_ORIGINS=https://your-frontend-domain.com
```

### 프론트엔드 환경 변수
```bash
# API URL
REACT_APP_API_URL=https://your-backend-domain.com

# 업로드 URL
REACT_APP_UPLOAD_URL=https://your-backend-domain.com/uploads
```

## 🔄 6. CI/CD 설정

### GitHub Actions 예시
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: ${{ secrets.HEROKU_APP_NAME }}
          heroku_email: ${{ secrets.HEROKU_EMAIL }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## 🧪 7. 테스트 및 검증

### 배포 후 확인사항
1. 백엔드 API 엔드포인트 접근 확인
2. 프론트엔드 페이지 로딩 확인
3. 데이터베이스 연결 확인
4. 파일 업로드 기능 확인
5. CORS 설정 확인

## 🔒 8. 보안 설정

### SSL 인증서
- Heroku: 자동 SSL 제공
- Vercel: 자동 SSL 제공
- 커스텀 도메인: Let's Encrypt 사용

### 환경 변수 보안
- 민감한 정보는 환경 변수로 관리
- Git에 .env 파일 커밋 금지
- 프로덕션 환경에서만 실제 값 사용

## 📊 9. 모니터링 설정

### 로그 모니터링
- Heroku: `heroku logs --tail`
- Railway: 대시보드에서 확인
- Vercel: 대시보드에서 확인

### 성능 모니터링
- New Relic
- DataDog
- AWS CloudWatch

## 🚨 10. 문제 해결

### 일반적인 문제들
1. **CORS 오류**: 환경 변수 CORS_ORIGINS 확인
2. **데이터베이스 연결 오류**: DATABASE_URL 확인
3. **파일 업로드 오류**: S3 권한 설정 확인
4. **빌드 오류**: Node.js 버전 확인

### 디버깅 명령어
```bash
# Heroku 로그 확인
heroku logs --tail

# 환경 변수 확인
heroku config

# 데이터베이스 마이그레이션
heroku run flask db upgrade
``` 