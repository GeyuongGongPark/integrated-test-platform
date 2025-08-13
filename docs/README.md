# 📚 Documentation & Configuration

이 폴더는 프로젝트의 문서와 설정 파일들을 포함합니다.

## 📁 파일 구조

### 📋 문서
- **README.md** - 이 파일
- **API_TESTING_GUIDE.md** - API 테스트 가이드
- **POSTMAN_USAGE_GUIDE.md** - Postman 사용법 상세 가이드
- **PROJECT_STRUCTURE.md** - 프로젝트 구조 상세 설명
- **DEPLOYMENT_SUMMARY.md** - 배포 상태 및 문제 해결 요약

### 🛠️ 설정 파일
- **postman_collection.json** - Postman API 컬렉션
- **postman_environment.json** - Postman 환경 설정
- **docker-compose.yml** - Docker 컨테이너 설정
- **env.example** - 환경 변수 예시

### 🗄️ 데이터베이스
- **mysql-init/** - MySQL 초기화 스크립트
  - `01-init.sql` - 데이터베이스 및 테이블 생성
  - `02-external-access.sql` - 외부 접근 권한 설정

## 🚀 빠른 시작

### 1. Postman 설정
1. `postman_collection.json`을 Postman에 Import
2. `postman_environment.json`을 Postman에 Import
3. 환경을 "Integrated Test Platform Environment"로 설정

### 2. Docker 실행
```bash
# MySQL 데이터베이스 실행
docker-compose up -d mysql

# 상태 확인
docker-compose ps
```

### 3. 환경 변수 설정
```bash
# .env 파일 생성
cp env.example .env

# 필요한 값으로 수정
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/test_management
SECRET_KEY=your-secret-key
FLASK_ENV=development
```

## 📖 문서 가이드

### API 테스트
- **Postman Collection**: 모든 API 엔드포인트를 포함한 테스트 컬렉션
- **API 가이드**: 각 API의 사용법과 예시
- **테스트 시나리오**: 일반적인 테스트 워크플로우

### 배포 및 운영
- **배포 요약**: 현재 배포 상태와 해결된 문제들
- **프로젝트 구조**: 전체 시스템 아키텍처 설명
- **Docker 설정**: 로컬 개발 환경 구성

## 🔧 유지보수

### 문서 업데이트
- API 변경 시 관련 문서 동시 업데이트
- 새로운 기능 추가 시 사용법 문서 작성
- 문제 해결 후 DEPLOYMENT_SUMMARY.md 업데이트

### 설정 파일 관리
- 환경별 설정 파일 분리 (dev, staging, prod)
- 민감한 정보는 .env 파일에 저장
- Git에 커밋하지 않을 파일은 .gitignore에 추가

---

**마지막 업데이트**: 2025년 8월 13일  
**문서 버전**: 2.0.1 