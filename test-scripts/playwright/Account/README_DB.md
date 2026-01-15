# 계정 정보 DB 관리 가이드

## 개요

기존 JSON 파일로 관리하던 계정 정보를 SQLite 데이터베이스로 이전하여 보안을 강화했습니다.

## 설치

```bash
npm install
```

`better-sqlite3` 패키지가 자동으로 설치됩니다.

## 초기 설정

### 1. DB 초기화 및 마이그레이션

기존 JSON 파일의 데이터를 DB로 마이그레이션합니다:

```bash
node Account/migrate_json_to_db.js
```

이 스크립트는 다음 작업을 수행합니다:
- `Account/Account_JSON/` 디렉토리의 모든 JSON 파일
- `Base_Code/samsung/beta/account/samsung.json`
- `harim/harim_account_all.json`

모든 계정 정보를 `Account/db/accounts.db`에 저장합니다.

## DB 구조

### accounts 테이블

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| id | INTEGER | 기본 키 (자동 증가) |
| account_key | TEXT | 계정 키 (예: blue, samsung, harim) |
| env | TEXT | 환경 (DEV/PROD) |
| role | TEXT | 역할 (master, approver, legal_advisor, legal, user 등) |
| base_url | TEXT | 기본 URL |
| user_id | TEXT | 사용자 ID |
| password | TEXT | 비밀번호 |
| created_at | DATETIME | 생성 시간 |
| updated_at | DATETIME | 수정 시간 |

### 제약조건

- `(account_key, env, role)` 조합은 유일해야 함 (UNIQUE)
- `env`는 'DEV' 또는 'PROD'만 허용

## 사용 방법

### 코드에서 계정 정보 로드

기존 `Account_env.js`의 사용법과 동일합니다:

```javascript
import { loadAccountEnv } from './Account/Account_env.js';

// .env 파일의 ACCOUNT, ENV, ROLE 사용
const accountData = await loadAccountEnv();

// 또는 직접 지정
const accountData = await loadAccountEnv('blue', 'DEV', 'master');
```

### DB 직접 접근

```javascript
import { getAccount, getAccountsByEnv, saveAccount } from './Account/db.js';
import { initializeDatabase } from './Account/db.js';

// DB 초기화 (한 번만 실행)
initializeDatabase();

// 계정 정보 조회
const account = getAccount('blue', 'DEV', 'master');

// 환경별 모든 계정 조회
const accounts = getAccountsByEnv('blue', 'DEV');

// 계정 정보 저장
saveAccount('blue', 'DEV', 'master', {
    base_url: 'https://example.com',
    id: 'user@example.com',
    password: 'password123'
});
```

## 보안 고려사항

1. **DB 파일 위치**: `Account/db/accounts.db`는 `.gitignore`에 추가되어 Git에 커밋되지 않습니다.
2. **비밀번호 암호화**: 현재는 평문 저장이지만, 향후 암호화 기능 추가 예정입니다.
3. **접근 제어**: DB 파일에 대한 파일 시스템 권한을 적절히 설정하세요.

## 클라우드 DB 이전

로컬 DB 검토 후 클라우드 DB로 이전할 때:

1. `Account/db.js`의 `getDatabase()` 함수를 클라우드 DB 연결로 변경
2. SQL 쿼리 문법이 다른 경우 (예: PostgreSQL) 적절히 수정
3. 연결 정보는 환경변수로 관리

## 마이그레이션 스크립트

`Account/migrate_json_to_db.js`는 필요시 다시 실행할 수 있습니다.
기존 데이터는 `ON CONFLICT` 처리로 업데이트됩니다.

## 문제 해결

### DB 파일이 생성되지 않는 경우

```bash
mkdir -p Account/db
node Account/migrate_json_to_db.js
```

### 패키지 설치 오류

```bash
npm install better-sqlite3 --save
```

### DB 초기화 오류

DB 파일을 삭제하고 다시 마이그레이션:

```bash
rm Account/db/accounts.db
node Account/migrate_json_to_db.js
```

