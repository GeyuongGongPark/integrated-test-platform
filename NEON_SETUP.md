# 🗄️ Neon PostgreSQL 데이터베이스 설정 가이드

## 📋 단계별 설정 방법

### 1. Neon 계정 생성
1. [Neon](https://neon.tech) 접속
2. "Sign up" 클릭
3. GitHub 계정으로 로그인
4. 무료 플랜 선택 (Hobby)

### 2. 데이터베이스 생성
1. "Create a project" 클릭
2. 프로젝트 정보 입력:
   - **Name**: `test-platform-db`
   - **Region**: `Seoul (ap-northeast-2)` 또는 가까운 지역
   - **Compute**: `Free tier`
3. "Create project" 클릭

### 3. 연결 정보 확인
1. 프로젝트 생성 후 "Connection Details" 확인
2. "Connection string" 복사 (예시):
   ```
   postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database?sslmode=require
   ```

### 4. 로컬 환경 설정
1. `integrated-test-platform/backend/.env` 파일 열기
2. `DATABASE_URL` 값을 Neon 연결 문자열로 변경:
   ```bash
   DATABASE_URL=postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database?sslmode=require
   ```

### 5. 연결 테스트
```bash
cd integrated-test-platform/backend
python test_neon_connection.py
```

## 🔧 문제 해결

### 연결 오류가 발생하는 경우
1. **SSL 설정 확인**: `?sslmode=require` 파라미터 포함
2. **방화벽 확인**: 포트 5432가 차단되지 않았는지 확인
3. **연결 문자열 형식 확인**: PostgreSQL 형식 사용

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

### 2. Neon으로 마이그레이션
```bash
# Flask-Migrate 사용
flask db upgrade
```

### 3. 테이블 생성 확인
```sql
-- Neon 대시보드에서 실행
\dt
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

### 1. Neon 대시보드
- 연결 수 모니터링
- 쿼리 성능 확인
- 저장 공간 사용량 확인

### 2. 로그 확인
```bash
# 애플리케이션 로그에서 데이터베이스 연결 확인
tail -f app.log | grep "database"
```

## 🚀 다음 단계

Neon 설정이 완료되면 다음 단계로 진행:
1. Railway 백엔드 배포
2. Vercel 프론트엔드 배포
3. Cloudinary 파일 저장소 설정

## 💰 비용 정보

### Neon 무료 플랜 (Hobby)
- **저장소**: 월 3GB
- **연결**: 무제한
- **데이터베이스**: 무제한
- **백업**: 자동 백업
- **SSL**: 무료 SSL 인증서 