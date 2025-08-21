# Vercel 배포 가이드 - Docker Ubuntu MySQL 연결

## 🎯 목표
Docker Ubuntu MySQL 서버와 연결하여 Vercel에 성공적으로 배포하기

## 🔧 필수 환경변수 설정

### 1. DATABASE_URL (가장 중요!)
```
DATABASE_URL=mysql+pymysql://vercel_user:vercel_secure_pass_2025@localhost:3308/test_management
```

**설명:**
- `vercel_user`: Ubuntu MySQL 사용자명
- `vercel_secure_pass_2025`: Ubuntu MySQL 비밀번호
- `localhost:3308`: Docker 포트 매핑 (호스트 3308 → 컨테이너 3306)
- `test_management`: 데이터베이스명

### 2. SECRET_KEY
```
SECRET_KEY=your-super-secret-key-change-in-production-2025
```

**설명:**
- Flask 앱의 비밀키
- JWT 토큰 서명에 사용
- 프로덕션에서는 강력한 랜덤 키 사용 권장

### 3. JWT_SECRET_KEY
```
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production-2025
```

**설명:**
- JWT 토큰 암호화에 사용
- SECRET_KEY와 다른 값 사용 권장

## 📋 Vercel 환경변수 설정 방법

### 방법 1: Vercel 대시보드 (권장)
1. **Vercel 대시보드** 접속
2. **프로젝트 선택** → **Settings** → **Environment Variables**
3. **Add New** 클릭
4. 각 환경변수 추가:
   - **Name**: `DATABASE_URL`
   - **Value**: `mysql+pymysql://vercel_user:vercel_secure_pass_2025@localhost:3308/test_management`
   - **Environment**: Production, Preview, Development 모두 체크
5. **Save** 클릭

### 방법 2: vercel.json 설정
```json
{
  "env": {
    "DATABASE_URL": "mysql+pymysql://vercel_user:vercel_secure_pass_2025@localhost:3308/test_management",
    "SECRET_KEY": "your-super-secret-key-change-in-production-2025",
    "JWT_SECRET_KEY": "your-jwt-secret-key-change-in-production-2025"
  }
}
```

## 🚀 배포 단계

### 1단계: 환경변수 설정
위의 환경변수들을 Vercel에 설정

### 2단계: Docker Ubuntu MySQL 서버 실행 확인
```bash
# 컨테이너 상태 확인
docker ps | grep ubuntu-mysql-server

# MySQL 연결 테스트
mysql -h 127.0.0.1 -P 3308 -u vercel_user -pvercel_secure_pass_2025 -e "SELECT 1;"
```

### 3단계: Vercel 배포
```bash
# Vercel CLI로 배포
vercel --prod

# 또는 Git 푸시로 자동 배포
git push origin main
```

## 🔍 배포 후 확인사항

### 1. 배포 로그 확인
- Vercel 대시보드 → **Deployments** → **Functions** 로그 확인
- 데이터베이스 연결 오류 메시지 확인

### 2. API 엔드포인트 테스트
```bash
# 헬스체크
curl https://your-project.vercel.app/health

# 데이터베이스 연결 테스트
curl https://your-project.vercel.app/api/test-connection
```

### 3. 데이터베이스 연결 상태 확인
- Vercel 함수 로그에서 "🔗 Database URL" 메시지 확인
- "✅ MySQL 연결 성공" 메시지 확인

## ⚠️ 주의사항

### 1. 포트 충돌 방지
- 로컬 MySQL: 포트 3306
- Docker Ubuntu MySQL: 포트 3308
- 포트가 겹치지 않도록 주의

### 2. 보안 고려사항
- 강력한 비밀번호 사용
- 프로덕션에서는 환경변수 노출 주의
- 정기적인 비밀번호 변경

### 3. 네트워크 설정
- Docker 컨테이너가 실행 중이어야 함
- 방화벽에서 포트 3308 허용
- 로컬 네트워크 접근 권한 확인

## 🔧 문제 해결

### 오류: "Can't connect to MySQL server"
1. **Docker 컨테이너 상태 확인**
   ```bash
   docker ps | grep ubuntu-mysql-server
   ```

2. **포트 매핑 확인**
   ```bash
   docker port ubuntu-mysql-server
   ```

3. **MySQL 서비스 상태 확인**
   ```bash
   docker exec ubuntu-mysql-server service mysql status
   ```

### 오류: "Access denied for user"
1. **사용자 권한 확인**
   ```bash
   docker exec ubuntu-mysql-server mysql -u root -e "SHOW GRANTS FOR 'vercel_user'@'%';"
   ```

2. **비밀번호 재설정**
   ```bash
   docker exec ubuntu-mysql-server mysql -u root -e "ALTER USER 'vercel_user'@'%' IDENTIFIED BY 'vercel_secure_pass_2025';"
   ```

### 오류: "Connection timeout"
1. **네트워크 설정 확인**
2. **방화벽 설정 확인**
3. **Docker 네트워크 설정 확인**

## 📊 모니터링

### 1. Vercel 대시보드
- **Functions** 로그 모니터링
- **Performance** 메트릭 확인
- **Errors** 알림 설정

### 2. 데이터베이스 모니터링
```bash
# 연결 상태 확인
docker exec ubuntu-mysql-server mysql -u root -e "SHOW PROCESSLIST;"

# 성능 상태 확인
docker exec ubuntu-mysql-server mysql -u root -e "SHOW STATUS LIKE 'Connections';"
```

## 🎉 성공적인 배포 후

1. **API 엔드포인트 정상 동작 확인**
2. **데이터베이스 CRUD 작업 테스트**
3. **사용자 인증/인가 테스트**
4. **성능 및 응답 시간 모니터링**

## 📝 체크리스트

- [ ] Docker Ubuntu MySQL 서버 실행
- [ ] DATABASE_URL 환경변수 설정
- [ ] SECRET_KEY 환경변수 설정
- [ ] JWT_SECRET_KEY 환경변수 설정
- [ ] 로컬 연결 테스트 완료
- [ ] Vercel 배포 실행
- [ ] 배포 후 연결 테스트 완료
- [ ] API 엔드포인트 정상 동작 확인
