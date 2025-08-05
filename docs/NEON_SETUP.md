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
   - **Name**: `integrated-test-platform-db`
   - **Region**: `Singapore (ap-southeast-1)` 또는 가까운 지역
   - **Compute**: `Free tier`
3. "Create project" 클릭

### 3. 연결 정보 확인
1. 프로젝트 생성 후 "Connection Details" 확인
2. "Connection string" 복사 (예시):
   ```
   postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   ```

### 4. 로컬 환경 설정
1. `integrated-test-platform/backend/.env` 파일 열기
2. `DATABASE_URL` 값을 Neon 연결 문자열로 변경:
   ```bash
   DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   DEV_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   TEST_DATABASE_URL=sqlite:///:memory:
   ```

### 5. 연결 테스트
```bash
cd integrated-test-platform/backend
python -c "
from app import app, db
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('✅ Neon PostgreSQL 연결 성공!')
    except Exception as e:
        print(f'❌ 연결 실패: {e}')
"
```

## 🔧 문제 해결

### 연결 오류가 발생하는 경우
1. **SSL 설정 확인**: `?sslmode=require&channel_binding=require` 파라미터 포함
2. **방화벽 확인**: 포트 5432가 차단되지 않았는지 확인
3. **연결 문자열 형식 확인**: PostgreSQL 형식 사용
4. **환경 변수 확인**: `.env` 파일이 올바르게 로드되는지 확인

### 일반적인 오류 메시지
- `Access denied`: 사용자명/비밀번호 확인
- `Connection timeout`: 네트워크 연결 확인
- `SSL required`: SSL 설정 확인
- `Database does not exist`: 데이터베이스 이름 확인

## 📊 데이터베이스 스키마 마이그레이션

### 1. 기존 데이터베이스 백업 (선택사항)
```bash
# 로컬 SQLite에서 백업
cp integrated-test-platform/backend/test_management.db backup.db
```

### 2. Neon으로 마이그레이션
```bash
cd integrated-test-platform/backend
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 3. 테이블 생성 확인
```sql
-- Neon 대시보드에서 실행
\dt

-- 또는 Python에서 확인
python -c "
from app import app, db
with app.app_context():
    tables = db.engine.execute('SELECT tablename FROM pg_tables WHERE schemaname = \'public\'')
    for table in tables:
        print(table[0])
"
```

## 🔒 보안 설정

### 1. 데이터베이스 비밀번호 관리
- 환경 변수로 관리
- Git에 커밋하지 않음
- 프로덕션에서는 강력한 비밀번호 사용

### 2. 접근 권한 설정
- 읽기/쓰기 권한만 부여
- 필요시 읽기 전용 사용자 생성

### 3. 환경별 데이터베이스 설정
```bash
# 개발 환경
DEV_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# 테스트 환경
TEST_DATABASE_URL=sqlite:///:memory:

# 프로덕션 환경
DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

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

### 3. 헬스체크 확인
```bash
# 백엔드 헬스체크
curl https://integrated-test-platform.vercel.app/health
```

## 🚀 배포 설정

### 1. Vercel 환경 변수 설정
Vercel 대시보드에서 다음 환경 변수 설정:
```
DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here
```

### 2. GitHub Secrets 설정
GitHub 저장소 설정에서 다음 Secrets 추가:
```
DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

## 🎯 현재 상태

### ✅ 완료된 작업
- [x] Neon PostgreSQL 데이터베이스 생성
- [x] 연결 문자열 설정
- [x] 데이터베이스 스키마 마이그레이션
- [x] Vercel 배포 환경 변수 설정
- [x] GitHub Actions CI/CD 설정
- [x] 연결 테스트 완료

### 🔄 현재 실행 중인 서비스
- **데이터베이스**: Neon PostgreSQL (프로덕션)
- **백엔드**: Vercel (https://integrated-test-platform.vercel.app)
- **프론트엔드**: Vercel (https://integrated-test-platform-fe-gyeonggong-parks-projects.vercel.app)

## 💰 비용 정보

### Neon 무료 플랜 (Hobby)
- **저장소**: 월 3GB
- **연결**: 무제한
- **데이터베이스**: 무제한
- **백업**: 자동 백업
- **SSL**: 무료 SSL 인증서
- **지역**: 글로벌 배포 지원

## 📊 성능 최적화

### 1. 연결 풀 설정
```python
# app.py에서 연결 풀 설정
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_timeout': 20,
    'pool_recycle': 3600,
}
```

### 2. 쿼리 최적화
- 인덱스 생성
- 불필요한 쿼리 제거
- 페이지네이션 구현

### 3. 캐싱 전략
- Redis 캐싱 (선택사항)
- 애플리케이션 레벨 캐싱
- CDN 활용 