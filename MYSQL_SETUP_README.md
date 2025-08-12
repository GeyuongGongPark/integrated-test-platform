# MySQL 데이터베이스 설정 가이드

이 문서는 네온 서버에서 Docker MySQL로 데이터베이스를 이관하는 방법을 설명합니다.

## 📋 요구사항

- Docker 및 Docker Compose가 설치되어 있어야 합니다
- Python 3.7+ 및 pip가 설치되어 있어야 합니다

## 🚀 빠른 시작

### 1. MySQL 컨테이너 실행

```bash
# Docker Compose로 MySQL 컨테이너 실행
docker-compose up -d mysql

# 또는 개별 스크립트 실행
./docker-mysql-setup.sh
```

### 2. 데이터베이스 설정 및 마이그레이션

```bash
# 자동 설정 스크립트 실행
./setup-mysql-db.sh
```

### 3. 연결 테스트

```bash
# Python 스크립트로 연결 테스트
python test-mysql-connection.py
```

## ⚙️ 설정 정보

| 항목 | 값 |
|------|-----|
| 컨테이너 이름 | `test_management` |
| 계정 | `root` |
| 비밀번호 | `1q2w#E$R` |
| 포트 | `3306` |
| 도메인 | `localhost` (127.0.0.1) |
| 데이터베이스 | `test_management` |

## 🔧 수동 설정

### Docker Compose 사용

```bash
# MySQL 컨테이너 실행
docker-compose up -d mysql

# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs mysql
```

### 개별 Docker 명령어 사용

```bash
# MySQL 컨테이너 실행
docker run -d \
  --name test_management \
  -e MYSQL_ROOT_PASSWORD=1q2w#E$R \
  -e MYSQL_DATABASE=test_management \
  -p 3306:3306 \
  mysql:8.0

# 컨테이너 상태 확인
docker ps

# 데이터베이스 연결 테스트
docker exec test_management mysql -u root -p1q2w#E$R -e "SHOW DATABASES;"
```

## 🐍 Python 백엔드 설정

### 1. 필요한 패키지 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화

```bash
cd backend
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('데이터베이스 테이블이 생성되었습니다.')
"
```

### 3. 마이그레이션 실행

```bash
cd backend
flask db init
flask db migrate -m "Initial MySQL migration"
flask db upgrade
```

### 4. 백엔드 서버 실행

```bash
cd backend
python app.py
# 또는
flask run
```

## 🔍 문제 해결

### 일반적인 문제들

1. **포트 충돌**
   ```bash
   # 포트 3306 사용 중인 프로세스 확인
   lsof -i :3306
   
   # Docker 컨테이너 중지
   docker stop test_management
   ```

2. **권한 문제**
   ```bash
   # Docker 컨테이너 재시작
   docker restart test_management
   ```

3. **데이터베이스 연결 실패**
   ```bash
   # 컨테이너 로그 확인
   docker logs test_management
   
   # 컨테이너 내부에서 MySQL 상태 확인
   docker exec test_management mysql -u root -p1q2w#E$R -e "STATUS;"
   ```

### 로그 확인

```bash
# Docker Compose 로그
docker-compose logs mysql

# 개별 컨테이너 로그
docker logs test_management

# 실시간 로그 모니터링
docker-compose logs -f mysql
```

## 📁 파일 구조

```
integrated-test-platform/
├── docker-compose.yml          # Docker Compose 설정
├── docker-mysql-setup.sh       # MySQL 컨테이너 설정 스크립트
├── setup-mysql-db.sh          # 데이터베이스 설정 스크립트
├── test-mysql-connection.py   # 연결 테스트 스크립트
├── mysql-init/                 # MySQL 초기화 스크립트
│   └── 01-init.sql
├── backend/                    # Flask 백엔드
│   ├── app.py                 # 메인 애플리케이션
│   ├── requirements.txt       # Python 패키지 목록
│   └── migrations/            # 데이터베이스 마이그레이션
└── frontend/                   # React 프론트엔드
```

## 🔄 데이터 이관

기존 네온 서버의 데이터를 MySQL로 이관하려면:

1. **데이터 내보내기** (네온 서버에서)
   ```bash
   pg_dump -h [neon-host] -U [username] -d [database] > backup.sql
   ```

2. **데이터 가져오기** (MySQL에서)
   ```bash
   # PostgreSQL 형식을 MySQL 형식으로 변환 후
   mysql -u root -p1q2w#E$R test_management < converted_backup.sql
   ```

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. Docker 컨테이너가 실행 중인지
2. 포트 3306이 올바르게 매핑되었는지
3. 비밀번호가 정확한지
4. 방화벽 설정이 올바른지

## 📚 추가 리소스

- [Docker MySQL 공식 문서](https://hub.docker.com/_/mysql)
- [Flask-SQLAlchemy 문서](https://flask-sqlalchemy.palletsprojects.com/)
- [PyMySQL 문서](https://pymysql.readthedocs.io/)
