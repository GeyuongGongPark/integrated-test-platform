# .env 파일 설정 가이드

## MySQL 연결 정보 추가

`.env` 파일에 다음 MySQL 설정을 추가하세요:

```env
# MySQL 데이터베이스 연결 정보
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=lfbz_accounts
```

## 전체 .env 파일 예시

기존 설정과 함께 다음과 같이 구성하세요:

```env
# MySQL 데이터베이스 연결 정보
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=lfbz_accounts

# 계정 정보 (기존 설정)
ACCOUNT=blue
ENV=DEV
ROLE=master
```

## 설정 확인

다음 명령어로 설정이 제대로 로드되는지 확인할 수 있습니다:

```bash
node -e "require('dotenv').config(); console.log('DB_HOST:', process.env.DB_HOST); console.log('DB_NAME:', process.env.DB_NAME);"
```

## 중요 사항

1. **비밀번호**: `DB_PASSWORD`에 실제 MySQL 비밀번호를 입력하세요
2. **보안**: `.env` 파일은 `.gitignore`에 포함되어 Git에 커밋되지 않습니다
3. **로컬 vs 클라우드**: 로컬 MySQL을 사용하는 경우 `DB_HOST=localhost`, 클라우드 MySQL을 사용하는 경우 해당 호스트 주소를 입력하세요

## 다음 단계

.env 파일 설정 후:

```bash
npm run migrate:accounts
```

를 실행하여 데이터베이스에 계정 정보를 마이그레이션하세요.

