# MySQL Workbench - Docker Ubuntu MySQL 연결 가이드

## 🎯 목표
MySQL Workbench에서 Docker로 실행 중인 Ubuntu MySQL 서버에 연결하여 데이터베이스를 조회하고 관리하기

## 🔗 연결 정보
```
Hostname: 127.0.0.1 (또는 localhost)
Port: 3308
Username: vercel_user
Password: vercel_secure_pass_2025
Database: test_management
```

## 📋 단계별 연결 방법

### 1단계: MySQL Workbench 실행
- MySQL Workbench 애플리케이션 실행

### 2단계: 새 연결 생성
- **Database** 메뉴 → **New Connection** 클릭
- 또는 홈 화면에서 **+** 버튼 클릭

### 3단계: 연결 정보 입력
```
Connection Name: Docker Ubuntu MySQL
Connection Method: Standard (TCP/IP)
Hostname: 127.0.0.1
Port: 3308
Username: vercel_user
Password: vercel_secure_pass_2025
```

### 4단계: 고급 설정 (선택사항)
**Advanced** 탭에서:
- **Use Compressed Protocol**: 체크 해제
- **Use SSL**: 체크 해제 (로컬 환경)

### 5단계: 연결 테스트
- **Test Connection** 버튼 클릭
- **"Successfully made the MySQL connection"** 메시지 확인

### 6단계: 연결 저장 및 실행
- **OK** 클릭하여 연결 저장
- 연결 목록에서 **Docker Ubuntu MySQL** 더블클릭

## 🗄️ 데이터베이스 조회

### 테이블 목록 확인
```sql
USE test_management;
SHOW TABLES;
```

### 테이블 구조 확인
```sql
DESCRIBE TestCases;
DESCRIBE Users;
DESCRIBE Folders;
```

### 데이터 샘플 조회
```sql
SELECT * FROM Users LIMIT 5;
SELECT * FROM TestCases LIMIT 5;
SELECT * FROM Folders LIMIT 5;
```

## 🔍 문제 해결

### 연결 실패 시 확인사항

#### 1. Docker 컨테이너 상태 확인
```bash
docker ps | grep ubuntu-mysql-server
```

#### 2. 포트 매핑 확인
```bash
docker port ubuntu-mysql-server
```

#### 3. MySQL 서비스 상태 확인
```bash
docker exec ubuntu-mysql-server service mysql status
```

#### 4. 방화벽/포트 확인
```bash
lsof -i :3308
```

### 일반적인 오류 및 해결방법

#### 오류: "Can't connect to MySQL server"
- Docker 컨테이너가 실행 중인지 확인
- 포트 3308이 올바르게 매핑되었는지 확인

#### 오류: "Access denied for user"
- 사용자명과 비밀번호 확인
- `vercel_user`가 올바르게 생성되었는지 확인

#### 오류: "Connection refused"
- MySQL 서비스가 실행 중인지 확인
- 컨테이너 내부에서 MySQL 재시작

## 🚀 고급 기능

### 1. 스키마 디자인
- **Database** → **Reverse Engineer MySQL Create Script**
- 기존 데이터베이스 구조를 시각적으로 확인

### 2. 데이터 내보내기/가져오기
- **Server** → **Data Export**
- **Server** → **Data Import**

### 3. 쿼리 실행 및 결과 분석
- SQL 에디터에서 복잡한 쿼리 작성
- 결과를 CSV/JSON으로 내보내기

## 📊 모니터링

### 연결 상태 확인
- 연결 목록에서 연결 상태 표시 확인
- **Information** 탭에서 서버 정보 확인

### 성능 모니터링
- **Performance Reports** 탭에서 쿼리 성능 분석
- **Client Connections** 확인

## 🔒 보안 고려사항

1. **강력한 비밀번호 사용**: 프로덕션에서는 더 강력한 비밀번호 사용
2. **네트워크 접근 제한**: 필요한 IP에서만 접근 허용
3. **사용자 권한 최소화**: 필요한 권한만 부여
4. **정기적인 비밀번호 변경**: 보안을 위한 정기적인 비밀번호 업데이트

## 📝 참고사항

- Docker 컨테이너가 실행 중이어야 연결 가능
- 포트 3308은 Docker 포트 매핑 (호스트 3308 → 컨테이너 3306)
- 로컬 환경이므로 SSL 연결 불필요
- 연결 후 `test_management` 데이터베이스 선택 필요
