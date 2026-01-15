# Vercel 배포 가이드

## 🚀 배포 전 준비사항

### 1. 환경변수 설정
Vercel 대시보드에서 다음 환경변수들을 설정해야 합니다:

#### 필수 환경변수
```bash
# 데이터베이스 연결
DATABASE_URL=mysql://username:password@host:port/database_name

# JWT 설정
JWT_SECRET_KEY=your-super-secret-jwt-key-here
SECRET_KEY=your-super-secret-flask-key-here

# Vercel 환경 감지
VERCEL=1
```

#### 선택 환경변수 (Slack 알림)
```bash
# Slack Webhook URL (선택사항)
# 설정하면 테스트 실패/완료 등의 알림이 Slack으로 전송됩니다
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### DATABASE_URL 형식 예시
```bash
# MySQL (PlanetScale, Railway, AWS RDS 등)
DATABASE_URL=mysql://username:password@host:port/database_name

# 예시: PlanetScale
DATABASE_URL=mysql://abc123:xyz789@aws.connect.psdb.cloud/test_management?ssl-mode=REQUIRED

# 예시: Railway
DATABASE_URL=mysql://root:password@containers-us-west-1.railway.app:1234/railway
```

### 2. 데이터베이스 요구사항
- MySQL 8.0 이상 지원
- SSL 연결 지원
- 외부 연결 허용 (Vercel IP에서 접근 가능)
- UTF8MB4 문자셋 지원

### 3. 테이블 스키마
다음 테이블들이 자동으로 생성됩니다:
- Users (사용자 관리)
- Folders (폴더 구조)
- TestCases (테스트 케이스)
- TestResults (테스트 결과)
- PerformanceTests (성능 테스트)
- AutomationTests (자동화 테스트)

## 🔧 배포 후 문제 해결

### 1. 데이터베이스 연결 오류
```bash
# 연결 상태 확인
curl https://your-app.vercel.app/db-status

# 데이터베이스 초기화
curl -X POST https://your-app.vercel.app/init-db
```

### 2. CORS 오류
```bash
# CORS 테스트
curl https://your-app.vercel.app/cors-test
```

### 3. 일반적인 오류들
- **500 Internal Server Error**: 데이터베이스 연결 실패
- **Database initialization failed**: 테이블 생성 실패
- **Can't connect to MySQL server**: 네트워크 연결 문제

## 📊 모니터링

### 1. 헬스 체크
```bash
curl https://your-app.vercel.app/health
```

### 2. 로그 확인
Vercel 대시보드 > Functions > app.py > Logs

### 3. 성능 모니터링
Vercel 대시보드 > Analytics

## 🚨 주의사항

1. **데이터베이스 연결 제한**: Vercel의 serverless 함수는 연결 시간 제한이 있습니다
2. **Cold Start**: 첫 요청 시 지연이 발생할 수 있습니다
3. **환경변수**: 민감한 정보는 반드시 Vercel 환경변수로 설정하세요
4. **SSL 설정**: MySQL 연결 시 SSL 설정이 필요할 수 있습니다

## 🔄 업데이트 배포

```bash
# 코드 변경 후 자동 배포
git push origin main

# 수동 배포
vercel --prod
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 환경변수 설정 상태
2. 데이터베이스 연결 상태
3. Vercel 로그
4. 데이터베이스 서버 상태
