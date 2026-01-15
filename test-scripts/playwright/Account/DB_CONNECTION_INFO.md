# DB 접속 정보 (MySQL)

## MySQL 설정

### 1. 환경변수 설정 (.env)

프로젝트 루트에 `.env` 파일을 생성하고 다음 정보를 입력하세요:

```env
# MySQL 연결 정보
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=lfbz_accounts
```

### 2. MySQL 데이터베이스 생성

MySQL에 접속하여 데이터베이스를 생성하세요:

```sql
CREATE DATABASE IF NOT EXISTS lfbz_accounts 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

### 3. 패키지 설치

```bash
npm install
```

`mysql2` 패키지가 자동으로 설치됩니다.

### 4. DB 초기화 및 마이그레이션

```bash
npm run migrate:accounts
```

또는

```bash
node Account/migrate_json_to_db.js
```

## 접속 정보

### 기본값

- **호스트**: `localhost`
- **포트**: `3306`
- **사용자**: `root`
- **비밀번호**: 환경변수에서 설정
- **데이터베이스**: `lfbz_accounts`

### 환경변수로 설정

`.env` 파일에서 다음 변수들을 설정할 수 있습니다:

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `DB_HOST` | `localhost` | MySQL 서버 호스트 |
| `DB_PORT` | `3306` | MySQL 서버 포트 |
| `DB_USER` | `root` | MySQL 사용자명 |
| `DB_PASSWORD` | `''` | MySQL 비밀번호 |
| `DB_NAME` | `lfbz_accounts` | 데이터베이스 이름 |

## 코드에서 사용

```javascript
import { getDatabase, initializeDatabase } from './Account/db.js';

// DB 초기화 (한 번만 실행)
await initializeDatabase();

// DB 연결 풀 가져오기
const pool = getDatabase();

// 쿼리 실행 예시
const [rows] = await pool.execute('SELECT * FROM accounts LIMIT 5');
console.log(rows);
```

## 테이블 구조

### accounts 테이블

```sql
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_key VARCHAR(100) NOT NULL,
    env ENUM('DEV', 'PROD') NOT NULL,
    role VARCHAR(50) NOT NULL,
    base_url TEXT,
    user_id VARCHAR(255),
    password VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_account_env_role (account_key, env, role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 클라우드 MySQL 사용 시

### 예시: AWS RDS, Google Cloud SQL 등

`.env` 파일에 클라우드 MySQL 정보를 입력하세요:

```env
DB_HOST=your-cloud-mysql-host.rds.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=your_secure_password
DB_NAME=lfbz_accounts
```

### SSL 연결 (선택사항)

SSL이 필요한 경우 `Account/db.js`의 `_createConnectionPool()` 함수를 수정하세요:

```javascript
const config = {
    // ... 기존 설정 ...
    ssl: {
        rejectUnauthorized: false  // 또는 인증서 설정
    }
};
```

## 연결 풀 설정

현재 연결 풀 설정:

- `connectionLimit`: 10 (최대 동시 연결 수)
- `queueLimit`: 0 (무제한 대기)
- `enableKeepAlive`: true (연결 유지)

필요시 `Account/db.js`에서 수정 가능합니다.

## 문제 해결

### 연결 오류

```
Error: connect ECONNREFUSED 127.0.0.1:3306
```

**해결 방법:**
1. MySQL 서버가 실행 중인지 확인: `mysql.server start` (macOS)
2. `.env` 파일의 접속 정보 확인
3. MySQL 사용자 권한 확인

### 데이터베이스 없음 오류

```
Error: Unknown database 'lfbz_accounts'
```

**해결 방법:**
```sql
CREATE DATABASE lfbz_accounts CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 인증 오류

```
Error: Access denied for user 'root'@'localhost'
```

**해결 방법:**
1. MySQL 비밀번호 확인
2. 사용자 권한 확인:
   ```sql
   GRANT ALL PRIVILEGES ON lfbz_accounts.* TO 'root'@'localhost';
   FLUSH PRIVILEGES;
   ```

## 보안 주의사항

1. **`.env` 파일**: `.gitignore`에 추가되어 Git에 커밋되지 않음
2. **비밀번호**: 강력한 비밀번호 사용
3. **접근 제어**: MySQL 사용자 권한 최소화
4. **SSL**: 프로덕션 환경에서는 SSL 연결 권장

## 로컬 MySQL 설치 (macOS)

```bash
# Homebrew로 설치
brew install mysql

# MySQL 시작
brew services start mysql

# 보안 설정 (비밀번호 설정)
mysql_secure_installation
```

## 로컬 MySQL 설치 (Linux)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install mysql-server

# 시작
sudo systemctl start mysql
sudo systemctl enable mysql

# 보안 설정
sudo mysql_secure_installation
```
