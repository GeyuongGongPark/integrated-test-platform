# 로컬 MySQL 데이터베이스 설정 가이드

## 🗄️ 로컬 MySQL 설치 및 설정

### 1. MySQL 설치 (Windows)

**방법 1: MySQL 공식 웹사이트에서 다운로드**
1. https://dev.mysql.com/downloads/mysql/ 접속
2. MySQL Community Server 다운로드
3. 설치 시 root 비밀번호 설정: `1q2w#E$R`

**방법 2: Chocolatey 사용**
```powershell
choco install mysql
```

### 2. 데이터베이스 생성

MySQL에 접속 후 다음 명령어 실행:

```sql
-- 데이터베이스 생성
CREATE DATABASE test_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 사용자 생성 (선택사항)
CREATE USER 'test_user'@'localhost' IDENTIFIED BY '1q2w#E$R';
GRANT ALL PRIVILEGES ON test_management.* TO 'test_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 백업된 데이터 복원

AWS RDS에서 백업한 .sql 파일이 있다면:

```bash
# MySQL 명령줄에서 실행
mysql -u root -p test_management < backup_file.sql
```

### 4. 연결 테스트

Python에서 연결 테스트:

```python
import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='1q2w#E$R',
        database='test_management',
        charset='utf8mb4'
    )
    print("✅ MySQL 연결 성공!")
    connection.close()
except Exception as e:
    print(f"❌ MySQL 연결 실패: {e}")
```

## 🔧 환경 변수 설정

### .env 파일 생성

프로젝트 루트에 `.env` 파일 생성:

```bash
# 데이터베이스 설정
DATABASE_URL=mysql+pymysql://root:1q2w#E$R@localhost:3306/test_management

# Flask 설정
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# JWT 설정
JWT_SECRET_KEY=your-jwt-secret-key-here
```

## 🚀 애플리케이션 실행

### 백엔드 실행
```bash
cd integrated-test-platform/backend
python app.py
```

### 프론트엔드 실행
```bash
cd integrated-test-platform/frontend
npm start
```

## 📋 확인사항

- [ ] MySQL 서비스 실행 중
- [ ] 데이터베이스 `test_management` 생성됨
- [ ] 백업 데이터 복원 완료 (있는 경우)
- [ ] .env 파일 설정 완료
- [ ] 애플리케이션 정상 실행

## 🆘 문제 해결

### 연결 오류 시
1. MySQL 서비스 상태 확인
2. 방화벽 설정 확인
3. 포트 3306 열려있는지 확인
4. 사용자 권한 확인

### 데이터베이스 오류 시
1. 테이블 존재 여부 확인
2. 마이그레이션 실행: `flask db upgrade`
3. 로그 파일 확인
