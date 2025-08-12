# Neon DB에서 MySQL로 마이그레이션 가이드

이 가이드는 기존 Neon PostgreSQL 데이터베이스에서 MySQL로 데이터를 마이그레이션하는 방법을 설명합니다.

## 🚀 마이그레이션 단계

### 1. 사전 준비

#### MySQL 컨테이너 실행
```bash
# MySQL Docker 컨테이너 실행
./docker-mysql-setup.sh
```

#### 마이그레이션 의존성 설치
```bash
# 마이그레이션에 필요한 패키지 설치
pip install -r requirements-migration.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 정보를 설정하세요:

```bash
# 기존 Neon DB 연결 정보
NEON_DATABASE_URL=postgresql://username:password@host:port/database

# 새로운 MySQL 연결 정보
DATABASE_URL=mysql+pymysql://root:1q2w#E$R@localhost:3306/test_management

# Flask 설정
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

**중요**: `NEON_DATABASE_URL`에는 실제 Neon DB의 연결 정보를 입력해야 합니다.

### 3. 마이그레이션 실행

```bash
# 마이그레이션 스크립트 실행
python neon_to_mysql_migration.py
```

### 4. 마이그레이션 후 설정

#### 백엔드 앱 재시작
```bash
cd backend
python app.py
```

#### Flask-Migrate로 스키마 동기화
```bash
cd backend
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📋 마이그레이션 대상 테이블

다음 테이블들이 마이그레이션됩니다:

1. **user** - 사용자 정보
2. **project** - 프로젝트 정보
3. **folder** - 폴더 구조
4. **test_case** - 테스트 케이스
5. **test_result** - 테스트 결과
6. **screenshot** - 스크린샷
7. **performance_test** - 성능 테스트
8. **performance_test_result** - 성능 테스트 결과
9. **automation_test** - 자동화 테스트
10. **automation_test_result** - 자동화 테스트 결과

## 🔍 마이그레이션 검증

마이그레이션이 완료되면 자동으로 다음을 검증합니다:

- 각 테이블의 레코드 수 확인
- 데이터 무결성 검사
- 외래 키 관계 확인

## ⚠️ 주의사항

1. **백업**: 마이그레이션 전에 기존 Neon DB 데이터를 백업하세요
2. **환경 변수**: `NEON_DATABASE_URL`이 올바르게 설정되었는지 확인하세요
3. **MySQL 실행**: MySQL 컨테이너가 실행 중인지 확인하세요
4. **권한**: MySQL에 대한 적절한 권한이 있는지 확인하세요

## 🆘 문제 해결

### Neon DB 연결 실패
- `NEON_DATABASE_URL` 환경 변수 확인
- 네트워크 연결 상태 확인
- Neon DB 서비스 상태 확인

### MySQL 연결 실패
- MySQL 컨테이너 실행 상태 확인
- 포트 3306 사용 가능 여부 확인
- 비밀번호 및 사용자명 확인

### 테이블 생성 실패
- MySQL 권한 확인
- 충분한 디스크 공간 확인
- 문자셋 설정 확인

## 📞 지원

마이그레이션 중 문제가 발생하면 다음을 확인하세요:

1. 로그 메시지 확인
2. 데이터베이스 연결 상태 확인
3. 환경 변수 설정 확인
4. 의존성 패키지 설치 상태 확인

## 🎯 마이그레이션 완료 후

마이그레이션이 성공적으로 완료되면:

1. 백엔드 앱이 MySQL을 사용하도록 설정됨
2. 모든 기존 데이터가 MySQL에 복사됨
3. 새로운 테스트 데이터는 MySQL에 저장됨
4. 기존 Neon DB는 더 이상 사용되지 않음

---

**마이그레이션은 되돌릴 수 없습니다. 실행 전에 반드시 백업을 수행하세요.**
