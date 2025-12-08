# 로컬 MySQL 데이터베이스 복구 가이드 (Docker 없이)

## 📋 사전 준비

### 1. MySQL 설치 확인

**macOS에서 MySQL 설치:**

```bash
# Homebrew로 설치 (권장)
brew install mysql

# MySQL 서비스 시작
brew services start mysql

# 또는 수동 시작
mysql.server start
```

**MySQL 설치 확인:**
```bash
mysql --version
```

### 2. MySQL 서비스 실행 확인

```bash
# 서비스 상태 확인
brew services list | grep mysql

# 또는 직접 확인
mysql -u root -p -e "SELECT 1"
```

## 🚀 복구 방법

### 방법 1: 자동 스크립트 사용 (권장)

```bash
# 스크립트 실행 권한 부여
chmod +x scripts/restore_local_mysql.sh

# 복구 실행
./scripts/restore_local_mysql.sh
```

### 방법 2: 수동 복구

**1. MySQL 서비스 시작:**
```bash
# Homebrew 사용 시
brew services start mysql

# 또는 수동 시작
mysql.server start
```

**2. 데이터베이스 생성:**
```bash
mysql -u root -p1q2w#E$R -e "CREATE DATABASE IF NOT EXISTS test_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

**3. 백업 파일 복구:**
```bash
mysql -u root -p1q2w#E$R test_management < mysql-backup/local_backup.sql
```

**4. 복구 확인:**
```bash
mysql -u root -p1q2w#E$R test_management -e "SHOW TABLES;"
```

### 방법 3: Python 스크립트 사용

```bash
# Python 스크립트 실행
python scripts/restore_database.py
```

## ⚙️ 환경 변수 설정

`.env` 파일에 MySQL 설정 추가:

```env
# MySQL 설정
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=1q2w#E$R
DB_NAME=test_management
```

또는 직접 DATABASE_URL 지정:

```env
DATABASE_URL=mysql+pymysql://root:1q2w#E$R@localhost:3306/test_management
```

## 🔍 문제 해결

### MySQL 서비스가 시작되지 않음

```bash
# Homebrew MySQL 재시작
brew services restart mysql

# 로그 확인
tail -f /usr/local/var/mysql/*.err
```

### 비밀번호 오류

```bash
# MySQL 비밀번호 재설정
mysql_secure_installation

# 또는 root 비밀번호 없이 접속 시도
mysql -u root
```

### 포트 충돌

```bash
# MySQL 포트 확인
lsof -i :3306

# 다른 포트 사용 시 .env 파일 수정
DB_PORT=3307
```

### 권한 오류

```bash
# MySQL 사용자 권한 확인
mysql -u root -p -e "SHOW GRANTS FOR 'root'@'localhost';"

# 권한 부여
mysql -u root -p -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;"
mysql -u root -p -e "FLUSH PRIVILEGES;"
```

## 📝 복구 후 확인

### 1. 데이터베이스 연결 확인

```bash
# 백엔드 애플리케이션 실행
cd backend
python app.py

# 다른 터미널에서 헬스 체크
curl http://localhost:8000/health
```

### 2. 테이블 확인

```bash
mysql -u root -p1q2w#E$R test_management -e "SHOW TABLES;"
```

### 3. 데이터 확인

```bash
# 사용자 테이블 확인
mysql -u root -p1q2w#E$R test_management -e "SELECT COUNT(*) FROM Users;"

# 테스트 케이스 확인
mysql -u root -p1q2w#E$R test_management -e "SELECT COUNT(*) FROM TestCases;"
```

## 🔄 기존 데이터 백업 (복구 전)

복구 전에 현재 데이터를 백업하려면:

```bash
# 현재 데이터베이스 백업
mysqldump -u root -p1q2w#E$R test_management > mysql-backup/before_restore_$(date +%Y%m%d_%H%M%S).sql
```

## 📚 관련 문서

- [로컬 DB 설정 가이드](./LOCAL_DB_SETUP.md)
- [MySQL Workbench 연결 가이드](./MYSQL_WORKBENCH_CONNECTION.md)

