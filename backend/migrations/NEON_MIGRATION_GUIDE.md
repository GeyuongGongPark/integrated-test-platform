# Neon Production DB를 Development DB로 마이그레이션 가이드

## 📋 사전 준비사항

### 1. 환경 변수 설정
백엔드 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# Development Database (Neon)
DEV_DATABASE_URL=postgresql://username:password@ep-dev-123456.us-east-1.aws.neon.tech/testmanager_dev?sslmode=require

# Production Database (Neon)
PROD_DATABASE_URL=postgresql://username:password@ep-prod-123456.us-east-1.aws.neon.tech/testmanager_prod?sslmode=require

# Legacy support (기존 DATABASE_URL)
DATABASE_URL=postgresql://username:password@ep-dev-123456.us-east-1.aws.neon.tech/testmanager_dev?sslmode=require

# Flask Environment
FLASK_ENV=development

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Secret Key
SECRET_KEY=your-secret-key-here
```

### 2. 실제 Neon DB URL로 교체
위의 예시 URL을 실제 Neon 데이터베이스 URL로 교체하세요:

- `username`: Neon DB 사용자명
- `password`: Neon DB 비밀번호
- `ep-dev-123456.us-east-1.aws.neon.tech`: Development DB 호스트
- `ep-prod-123456.us-east-1.aws.neon.tech`: Production DB 호스트
- `testmanager_dev`: Development DB 이름
- `testmanager_prod`: Production DB 이름

## 🚀 마이그레이션 실행

### 1. 백엔드 디렉토리로 이동
```bash
cd integrated-test-platform/backend
```

### 2. 가상환경 활성화 (선택사항)
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 마이그레이션 스크립트 실행
```bash
python migrate_neon_prod_to_dev.py
```

## 📊 마이그레이션 과정

1. **환경 변수 확인**: PROD_DATABASE_URL과 DEV_DATABASE_URL이 설정되어 있는지 확인
2. **데이터베이스 연결 테스트**: Production과 Development DB에 연결 가능한지 테스트
3. **테이블 목록 확인**: Production DB의 모든 테이블 목록 표시
4. **마이그레이션 옵션 선택**:
   - 모든 테이블 마이그레이션
   - 특정 테이블만 마이그레이션
   - 테이블별 개별 선택
5. **데이터 마이그레이션**: 선택된 테이블의 데이터를 Development DB로 복사
6. **로그 생성**: 마이그레이션 결과를 JSON 파일로 저장

## ⚠️ 주의사항

- **데이터 덮어쓰기**: Development DB의 기존 데이터가 Production DB 데이터로 덮어써집니다
- **백업 권장**: 마이그레이션 전에 Development DB의 중요 데이터를 백업하세요
- **네트워크 연결**: 안정적인 인터넷 연결이 필요합니다
- **권한 확인**: Neon DB에 대한 읽기/쓰기 권한이 있어야 합니다

## 🔍 마이그레이션 후 확인사항

1. **로그 파일 확인**: `migration_log_YYYYMMDD_HHMMSS.json` 파일에서 마이그레이션 결과 확인
2. **데이터 검증**: Development DB에서 테이블과 데이터가 정상적으로 복사되었는지 확인
3. **애플리케이션 테스트**: 프론트엔드에서 Development DB 연결이 정상적으로 작동하는지 확인

## 🛠️ 문제 해결

### 연결 오류
- Neon DB URL이 올바른지 확인
- 네트워크 연결 상태 확인
- Neon DB 서비스 상태 확인

### 권한 오류
- Neon DB 사용자 권한 확인
- SSL 모드 설정 확인 (`sslmode=require`)

### 데이터 오류
- 테이블 구조 호환성 확인
- 데이터 타입 불일치 확인

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 마이그레이션 로그 파일
2. 콘솔 출력 메시지
3. Neon DB 관리 콘솔에서 연결 상태 