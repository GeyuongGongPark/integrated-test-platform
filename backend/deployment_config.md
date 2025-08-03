# Neon 브랜치 분리 배포 설정

## 1. Neon 콘솔에서 브랜치 생성

### Development 브랜치 생성
1. Neon 콘솔 접속
2. 프로젝트 선택: `ep-flat-frog-a1tlnavw`
3. 브랜치 탭에서 "New Branch" 클릭
4. 브랜치명: `development`
5. 소스 브랜치: `main`

### Production 브랜치 (기본)
- 브랜치명: `main` (기본 브랜치)

## 2. 배포 환경별 환경변수 설정

### Vercel/Railway/Render 등에서 설정할 환경변수:

```bash
# Development 환경
DEV_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Production 환경  
PROD_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Flask 환경
FLASK_ENV=production

# CORS 설정
CORS_ORIGINS=https://your-frontend-domain.com

# Secret Key
SECRET_KEY=your-production-secret-key
```

## 3. 브랜치별 데이터 확인

### Development 브랜치 데이터:
- 프로젝트: "개발용 테스트 프로젝트"
- 성능 테스트: "개발용 CLM 테스트"

### Production 브랜치 데이터:
- 프로젝트: "운영용 테스트 프로젝트"  
- 성능 테스트: "운영용 CLM 테스트"

## 4. 배포 후 확인 방법

### API 엔드포인트 테스트:
```bash
# Development 환경
curl https://your-backend-domain.com/projects

# Production 환경  
curl https://your-backend-domain.com/projects
```

### 예상 결과:
- Development: 개발용 데이터 반환
- Production: 운영용 데이터 반환

## 5. 환경별 실행 명령어

### 로컬 개발:
```bash
# Development 환경
$env:FLASK_ENV="development"; python app.py

# Production 환경
$env:FLASK_ENV="production"; python app.py
```

### 배포 환경:
- 자동으로 `FLASK_ENV=production` 설정
- `DEV_DATABASE_URL`과 `PROD_DATABASE_URL` 환경변수 사용 