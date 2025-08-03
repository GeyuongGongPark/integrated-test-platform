# 배포 환경 환경변수 설정

## Vercel 배포 시 환경변수 설정

### 필수 환경변수:
```
DEV_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
PROD_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-here
CORS_ORIGINS=https://your-frontend-domain.com
```

## Railway 배포 시 환경변수 설정

### Railway 대시보드에서 설정:
1. 프로젝트 선택
2. Variables 탭 클릭
3. 다음 환경변수 추가:

```
DEV_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
PROD_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-here
CORS_ORIGINS=https://your-frontend-domain.com
```

## Render 배포 시 환경변수 설정

### Render 대시보드에서 설정:
1. 서비스 선택
2. Environment 탭 클릭
3. 다음 환경변수 추가:

```
DEV_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
PROD_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-here
CORS_ORIGINS=https://your-frontend-domain.com
```

## 배포 후 확인 방법

### 1. 헬스체크:
```bash
curl https://your-backend-domain.com/health
```

### 2. 프로젝트 데이터 확인:
```bash
curl https://your-backend-domain.com/projects
```

### 3. 성능 테스트 데이터 확인:
```bash
curl https://your-backend-domain.com/performance-tests
```

## 예상 결과

### Production 환경에서 반환될 데이터:
```json
{
  "projects": [
    {
      "id": 1,
      "name": "운영용 테스트 프로젝트",
      "description": "Production 환경 테스트 케이스 관리 시스템"
    }
  ],
  "performance_tests": [
    {
      "id": 1,
      "name": "운영용 CLM 테스트",
      "description": "Production 환경 LFBZ CLM 시스템 테스트",
      "environment": "prod"
    }
  ]
}
```

## 문제 해결

### 1. 데이터베이스 연결 오류:
- Neon 콘솔에서 브랜치가 올바르게 생성되었는지 확인
- 환경변수 URL이 올바른지 확인

### 2. CORS 오류:
- CORS_ORIGINS 환경변수가 프론트엔드 도메인과 일치하는지 확인

### 3. 401 오류:
- SECRET_KEY가 설정되었는지 확인
- FLASK_ENV가 production으로 설정되었는지 확인 