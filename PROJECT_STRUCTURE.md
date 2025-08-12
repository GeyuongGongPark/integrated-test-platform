# 프로젝트 구조 가이드

Integrated Test Platform의 전체 프로젝트 구조와 각 디렉토리의 역할을 설명합니다.

## 📁 루트 디렉토리

```
integrated-test-platform/
├── 📁 backend/                 # Flask 백엔드 API
├── 📁 frontend/                # React 프론트엔드
├── 📁 test-scripts/            # 테스트 스크립트 모음
├── 📁 docs/                    # 프로젝트 문서
├── 📁 mysql-init/              # MySQL 초기화 스크립트
├── 📄 README.md                # 메인 프로젝트 설명
├── 📄 .gitignore               # Git 제외 파일 목록
├── 📄 docker-compose.yml       # Docker 설정
├── 📄 env.example              # 환경 변수 예시
└── 📄 requirements-migration.txt # 마이그레이션 의존성
```

## 🐍 Backend (Flask)

### 주요 파일
- **`app.py`**: 메인 Flask 애플리케이션
- **`requirements.txt`**: Python 의존성 목록

### 디렉토리 구조
```
backend/
├── 📁 engines/                 # 테스트 엔진
│   ├── __init__.py
│   └── k6_engine.py           # K6 성능 테스트 엔진
├── 📁 routes/                  # API 라우트
│   ├── __init__.py
│   ├── automation.py           # 자동화 테스트 API
│   ├── dashboard.py            # 대시보드 API
│   ├── folders.py              # 폴더 관리 API
│   ├── performance.py          # 성능 테스트 API
│   ├── testcases.py            # 테스트 케이스 API
│   └── users.py                # 사용자 관리 API
├── 📁 utils/                   # 유틸리티 함수
│   ├── __init__.py
│   ├── auth.py                 # 인증 관련
│   └── cors.py                 # CORS 설정
└── 📁 migrations/              # 데이터베이스 마이그레이션
    ├── alembic.ini
    ├── env.py
    └── versions/
```

## ⚛️ Frontend (React)

### 주요 파일
- **`package.json`**: Node.js 의존성 및 스크립트
- **`src/App.js`**: 메인 React 컴포넌트

### 디렉토리 구조
```
frontend/src/
├── 📁 components/              # React 컴포넌트
│   ├── 📁 automation/          # 자동화 테스트 컴포넌트
│   ├── 📁 dashboard/           # 대시보드 컴포넌트
│   ├── 📁 performance/         # 성능 테스트 컴포넌트
│   ├── 📁 settings/            # 설정 컴포넌트
│   ├── 📁 testcases/           # 테스트 케이스 컴포넌트
│   └── 📁 utils/               # 유틸리티 컴포넌트
├── 📄 App.js                   # 메인 애플리케이션
├── 📄 App.css                  # 메인 스타일
├── 📄 index.js                 # 진입점
└── 📄 config.js                # 설정 파일
```

## 🧪 Test Scripts

### 성능 테스트 (K6)
```
test-scripts/performance/
├── 📁 clm/                     # CLM 관련 테스트
│   ├── 📁 multi/               # 다중 사용자 테스트
│   └── 📁 nomerl/              # 단일 사용자 테스트
├── 📁 advice/                   # 조언 관련 테스트
├── 📁 litigation/               # 소송 관련 테스트
├── 📁 login/                    # 로그인 테스트
├── 📁 dashboard/                # 대시보드 테스트
├── 📁 common/                   # 공통 유틸리티
├── 📁 python/                   # Python 스크립트
└── 📁 url/                      # URL 설정
```

### 자동화 테스트 (Playwright)
```
test-scripts/playwright/
└── 📄 sample-login.spec.js     # 샘플 로그인 테스트
```

## 📚 Documentation

```
docs/
├── 📄 README.md                # 문서 목록 및 가이드
├── 📄 USAGE.md                 # 사용법 가이드
├── 📄 DEPLOYMENT_SUCCESS.md    # 배포 성공 가이드
├── 📄 VERCEL_QUICK_DEPLOY.md  # Vercel 빠른 배포
├── 📄 VERCEL_FRONTEND_DEPLOY.md # Vercel 프론트엔드 배포
├── 📄 FRONTEND_DEPLOYMENT_FIX.md # 배포 문제 해결
├── 📄 WHITE_SCREEN_FIX.md      # 화이트 스크린 해결
├── 📄 FREE_HOSTING_OPTIONS.md  # 호스팅 옵션 비교
├── 📄 INTEGRATION_PLAN.md      # 통합 계획
├── 📄 NEON_SETUP.md            # Neon DB 설정
└── 📄 LFBZ_performance_README.md # 성능 테스트 가이드
```

## 🗄️ Database

### MySQL 초기화
```
mysql-init/
└── 📄 01-init.sql              # 데이터베이스 초기화 스크립트
```

### 마이그레이션 도구
- **`neon_to_mysql_migration.py`**: Neon에서 MySQL로 데이터 마이그레이션
- **`interactive_migration.py`**: 대화형 마이그레이션 도구
- **`test-mysql-connection.py`**: MySQL 연결 테스트

## 🐳 Docker

- **`docker-compose.yml`**: MySQL 및 애플리케이션 컨테이너 설정
- **`docker-mysql-setup.sh`**: MySQL Docker 설정 스크립트
- **`setup-mysql-db.sh`**: MySQL 데이터베이스 설정

## 🔧 설정 파일

- **`.gitignore`**: Git에서 제외할 파일 목록
- **`env.example`**: 환경 변수 설정 예시
- **`postman_collection.json`**: Postman API 테스트 컬렉션

## 📊 프로젝트 특징

### 아키텍처
- **백엔드**: Flask 기반 RESTful API
- **프론트엔드**: React 기반 SPA
- **데이터베이스**: MySQL (Neon에서 마이그레이션)
- **테스트**: K6 (성능), Playwright (자동화)

### 배포
- **프론트엔드**: Vercel
- **백엔드**: Vercel
- **데이터베이스**: MySQL (로컬 또는 클라우드)

### 개발 환경
- **Python**: 3.8+
- **Node.js**: 16+
- **패키지 관리**: pip, npm
- **버전 관리**: Git

## 🚀 빠른 시작

1. **백엔드 실행**: `cd backend && python app.py`
2. **프론트엔드 실행**: `cd frontend && npm start`
3. **데이터베이스**: `docker-compose up -d`
4. **테스트 실행**: `cd test-scripts && k6 run performance/...`

## 📝 유지보수 가이드

### 정기 정리 항목
- [ ] 불필요한 파일 삭제 (.DS_Store, __pycache__, node_modules)
- [ ] 문서 최신화
- [ ] 의존성 업데이트
- [ ] 테스트 스크립트 정리

### 코드 품질
- [ ] Python: PEP 8 준수
- [ ] JavaScript: ESLint 규칙 준수
- [ ] 테스트 커버리지 유지
- [ ] 문서 주석 업데이트
