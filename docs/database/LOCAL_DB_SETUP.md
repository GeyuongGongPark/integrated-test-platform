# 로컬 데이터베이스 설정 가이드

## 🚀 빠른 시작 (SQLite - 가장 간단)

SQLite는 별도 설치 없이 바로 사용할 수 있습니다.

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일 생성:

```bash
# .env 파일 복사
cp .env.example .env
```

또는 직접 생성:

```env
DB_TYPE=sqlite
DB_PATH=local.db
SECRET_KEY=local-dev-secret-key
JWT_SECRET_KEY=local-jwt-secret-key
```

### 2. 애플리케이션 실행

```bash
# 백엔드 실행
cd backend
python app.py
```

데이터베이스 파일(`local.db`)이 프로젝트 루트에 자동 생성됩니다.

---

## 🐳 Docker Compose를 사용한 MySQL 설정

### 1. Docker Compose로 MySQL 실행

```bash
# MySQL 컨테이너 시작
docker-compose up -d mysql

# 상태 확인
docker-compose ps
```

### 2. 환경 변수 설정

`.env` 파일:

```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=1q2w#E$R
DB_NAME=test_management
SECRET_KEY=local-dev-secret-key
JWT_SECRET_KEY=local-jwt-secret-key
```

### 3. 데이터베이스 초기화

```bash
# 백엔드 실행 후
curl http://localhost:8000/init-db
```

---

## 💻 로컬 MySQL 직접 설치

### macOS (Homebrew)

```bash
# MySQL 설치
brew install mysql

# MySQL 시작
brew services start mysql

# MySQL 접속
mysql -u root -p
```

### 데이터베이스 생성

```sql
CREATE DATABASE test_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 환경 변수 설정

`.env` 파일:

```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=test_management
SECRET_KEY=local-dev-secret-key
JWT_SECRET_KEY=local-jwt-secret-key
```

---

## 📋 환경 변수 옵션

### 옵션 1: SQLite (기본값, 가장 간단)

```env
DB_TYPE=sqlite
DB_PATH=local.db  # 또는 절대 경로: /path/to/database.db
```

### 옵션 2: MySQL (개별 설정)

```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=test_management
```

### 옵션 3: 직접 DATABASE_URL 지정

```env
DATABASE_URL=mysql+pymysql://user:password@host:port/database
# 또는
DATABASE_URL=sqlite:///path/to/database.db
```

**우선순위**: `DATABASE_URL` > `DB_TYPE` 설정 > 기본값(SQLite)

---

## 🔍 데이터베이스 확인

### SQLite

```bash
# SQLite 데이터베이스 파일 확인
ls -lh local.db

# SQLite CLI로 확인
sqlite3 local.db
.tables
```

### MySQL

```bash
# MySQL 접속
mysql -u root -p test_management

# 테이블 확인
SHOW TABLES;
```

---

## 🆘 문제 해결

### SQLite 사용 시

- **파일 권한 오류**: `DB_PATH`를 쓰기 가능한 디렉토리로 설정
- **파일이 생성되지 않음**: 프로젝트 루트 디렉토리 확인

### MySQL 사용 시

- **연결 실패**: MySQL 서비스 실행 상태 확인
  ```bash
  # macOS
  brew services list
  
  # Docker
  docker-compose ps
  ```
- **포트 충돌**: `DB_PORT` 환경 변수로 다른 포트 사용
- **인증 오류**: MySQL 사용자 비밀번호 확인

### 일반적인 문제

1. **환경 변수가 적용되지 않음**
   - `.env` 파일이 프로젝트 루트에 있는지 확인
   - 애플리케이션 재시작

2. **데이터베이스 초기화 필요**
   ```bash
   curl http://localhost:8000/init-db
   ```

3. **마이그레이션 필요**
   ```bash
   cd backend
   flask db upgrade
   ```

---

## 📝 권장 설정

### 개발 환경
- **SQLite**: 빠른 개발 및 테스트용
- 설정 간단, 별도 서버 불필요

### 프로덕션/스테이징 환경
- **MySQL**: 성능 및 동시성 요구사항
- Docker Compose 또는 클라우드 DB 사용

