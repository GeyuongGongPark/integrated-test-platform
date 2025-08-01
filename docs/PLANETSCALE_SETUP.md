# 🗄️ PlanetScale 데이터베이스 설정 가이드

## 📋 단계별 설정 방법

### 1. PlanetScale 계정 생성
1. [PlanetScale](https://planetscale.com) 접속
2. "Sign up" 클릭
3. GitHub 계정으로 로그인
4. 무료 플랜 선택

### 2. 데이터베이스 생성
1. "New Database" 클릭
2. 데이터베이스 정보 입력:
   - **Name**: `test-platform-db`
   - **Region**: `Seoul (ap-northeast-2)`
   - **Plan**: `Hobby (Free)`
3. "Create database" 클릭

### 3. 연결 정보 확인
1. 생성된 데이터베이스 클릭
2. "Connect" 버튼 클릭
3. "Connect with MySQL" 선택
4. 연결 문자열 복사 (예시):
   ```
   mysql://username:password@aws.connect.psdb.cloud/test-platform-db?sslaccept=strict
   ```

### 4. 로컬 환경 설정
1. `integrated-test-platform/backend/.env` 파일 열기
2. `DATABASE_URL` 값을 PlanetScale 연결 문자열로 변경:
   ```bash
   DATABASE_URL=mysql://your-username:your-password@aws.connect.psdb.cloud/test-platform-db?sslaccept=strict
   ```

### 5. 연결 테스트
```bash
cd integrated-test-platform/backend
python test_planetscale_connection.py
```

## 🔧 문제 해결

### 연결 오류가 발생하는 경우
1. **SSL 설정 확인**: PlanetScale은 SSL 연결이 필수입니다
2. **방화벽 확인**: 포트 3306이 차단되지 않았는지 확인
3. **연결 문자열 형식 확인**: `?sslaccept=strict` 파라미터 포함

### 일반적인 오류 메시지
- `Access denied`: 사용자명/비밀번호 확인
- `Connection timeout`: 네트워크 연결 확인
- `SSL required`: SSL 설정 확인

## 📊 데이터베이스 스키마 마이그레이션

### 1. 기존 데이터베이스 백업 (선택사항)
```bash
# 로컬 MySQL에서 백업
mysqldump -u root testmanager > backup.sql
```

### 2. PlanetScale로 마이그레이션
```bash
# Flask-Migrate 사용
flask db upgrade
```

### 3. 테이블 생성 확인
```sql
-- PlanetScale 대시보드에서 실행
SHOW TABLES;
```

## 🔒 보안 설정

### 1. 데이터베이스 비밀번호 관리
- 환경 변수로 관리
- Git에 커밋하지 않음
- 프로덕션에서는 강력한 비밀번호 사용

### 2. 접근 권한 설정
- 읽기/쓰기 권한만 부여
- 필요시 읽기 전용 사용자 생성

## 📈 모니터링

### 1. PlanetScale 대시보드
- 연결 수 모니터링
- 쿼리 성능 확인
- 저장 공간 사용량 확인

### 2. 로그 확인
```bash
# 애플리케이션 로그에서 데이터베이스 연결 확인
tail -f app.log | grep "database"
```

## 🚀 다음 단계

PlanetScale 설정이 완료되면 다음 단계로 진행:
1. Railway 백엔드 배포
2. Vercel 프론트엔드 배포
3. Cloudinary 파일 저장소 설정 