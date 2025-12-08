# 스크립트 파일

이 폴더에는 프로젝트 실행 및 관리에 필요한 스크립트 파일들이 포함되어 있습니다.

## 📚 스크립트 목록

### 애플리케이션 실행 스크립트
- **restart-all.sh** - 전체 애플리케이션 재시작 (백엔드 + 프론트엔드)
- **restart-backend.sh** - 백엔드 서버 재시작
- **restart-mock-jira.sh** - Mock JIRA 서버 재시작

### 데이터베이스 관련 스크립트
- **restore_database.sh** - 데이터베이스 복구 스크립트
- **restore_local_mysql.sh** - 로컬 MySQL 데이터베이스 복구
- **start-ubuntu-mysql.sh** - Ubuntu MySQL 서버 시작
- **setup-ngrok-mysql.sh** - ngrok을 통한 MySQL 터널 설정
- **mysql-tunnel.sh** - MySQL 터널 설정

### 데이터베이스 유틸리티 (Python)
- **restore_database.py** - 데이터베이스 복구 Python 스크립트
- **test_db_connection.py** - 데이터베이스 연결 테스트

### 백업 및 복구
- **download_s3_backup.py** - S3에서 백업 파일 다운로드

## 🚀 사용 방법

### 애플리케이션 재시작
```bash
# 전체 재시작
./scripts/restart-all.sh

# 백엔드만 재시작
./scripts/restart-backend.sh

# Mock JIRA 서버 재시작
./scripts/restart-mock-jira.sh
```

### 데이터베이스 복구
```bash
# 로컬 MySQL 복구
./scripts/restore_local_mysql.sh

# 또는 Python 스크립트 사용
python scripts/restore_database.py
```

### MySQL 서버 시작
```bash
# Ubuntu MySQL 서버 시작
./scripts/start-ubuntu-mysql.sh
```

### 데이터베이스 연결 테스트
```bash
python scripts/test_db_connection.py
```

## 📖 상세 가이드

각 스크립트의 상세 사용법은 [데이터베이스 설정 가이드](../docs/database/README.md)를 참조하세요.

