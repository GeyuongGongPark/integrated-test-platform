# 데이터베이스 설정 가이드

이 폴더에는 데이터베이스 설정 및 관리 관련 문서가 포함되어 있습니다.

## 📚 문서 목록

### 로컬 개발 환경 설정
- **LOCAL_DATABASE_SETUP.md** - 로컬 MySQL 데이터베이스 설정 가이드 (Windows)
- **LOCAL_DB_SETUP.md** - 로컬 데이터베이스 설정 가이드 (일반)
- **LOCAL_MYSQL_RESTORE.md** - 로컬 MySQL 데이터베이스 복구 가이드 (Docker 없이)

### MySQL 연결 및 관리
- **MYSQL_WORKBENCH_CONNECTION.md** - MySQL Workbench에서 Docker Ubuntu MySQL 연결 가이드
- **UBUNTU_MYSQL_SETUP.md** - Ubuntu MySQL 서버 Docker 설정 가이드

## 🚀 빠른 시작

### 로컬 MySQL 설정
```bash
# MySQL 서비스 시작
brew services start mysql  # macOS
# 또는
mysql.server start

# 데이터베이스 생성
mysql -u root -p -e "CREATE DATABASE test_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Docker를 사용한 MySQL 설정
```bash
# Docker Compose로 MySQL 실행
docker-compose up -d mysql

# 또는 Ubuntu MySQL 서버 실행
./start-ubuntu-mysql.sh
```

## 📖 상세 가이드

각 문서를 참조하여 환경에 맞는 설정 방법을 확인하세요.

