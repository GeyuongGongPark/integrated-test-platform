# 프로젝트 구조 상세 가이드

## 📁 전체 프로젝트 구조

```
integrated-test-platform/
├── 📁 backend/                    # Flask 백엔드 API 서버
│   ├── 📄 app.py                  # 메인 Flask 애플리케이션 (최신화됨)
│   ├── 📄 vercel.json             # Vercel 배포 설정
│   ├── 📄 requirements.txt        # Python 의존성 (최적화됨)
│   ├── 📄 Dockerfile              # Docker 컨테이너 설정
│   ├── 📁 engines/                # 테스트 엔진 모듈
│   │   ├── 📄 __init__.py
│   │   └── 📄 k6_engine.py        # K6 성능 테스트 엔진
│   ├── 📁 routes/                 # API 라우트 모듈
│   │   ├── 📄 __init__.py
│   │   ├── 📄 folders.py          # 폴더 관리 API (최신화됨)
│   │   ├── 📄 testcases.py        # 테스트 케이스 API
│   │   ├── 📄 performance.py      # 성능 테스트 API
│   │   ├── 📄 automation.py       # 자동화 테스트 API
│   │   ├── 📄 dashboard.py        # 대시보드 API
│   │   └── 📄 users.py            # 사용자 관리 API
│   ├── 📁 utils/                  # 유틸리티 모듈
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth.py             # 인증 관련 유틸리티
│   │   └── 📄 cors.py             # CORS 설정
│   ├── 📁 migrations/             # 데이터베이스 마이그레이션
│   │   ├── 📄 alembic.ini
│   │   ├── 📄 env.py
│   │   └── 📁 versions/           # 마이그레이션 버전 파일들
│   ├── 📁 instance/               # 인스턴스별 설정
│   └── 📁 venv/                   # Python 가상환경
├── 📁 frontend/                   # React 프론트엔드 애플리케이션
│   ├── 📄 package.json            # Node.js 의존성
│   ├── 📄 vercel.json             # Vercel 프론트엔드 배포 설정
│   ├── 📁 src/                    # 소스 코드
│   │   ├── 📄 App.js              # 메인 React 컴포넌트
│   │   ├── 📄 index.js            # 애플리케이션 진입점
│   │   ├── 📄 config.js           # 환경별 API 설정 (최신화됨)
│   │   ├── 📁 components/         # React 컴포넌트들
│   │   │   ├── 📁 dashboard/      # 대시보드 관련 컴포넌트
│   │   │   │   ├── 📄 UnifiedDashboard.js    # 통합 대시보드
│   │   │   │   ├── 📄 FolderManager.js        # 폴더 관리 (최신화됨)
│   │   │   │   └── 📄 index.js
│   │   │   ├── 📁 testcases/      # 테스트 케이스 관리
│   │   │   │   ├── 📄 TestCaseAPP.js          # 메인 테스트 케이스 앱 (최신화됨)
│   │   │   │   ├── 📄 TestCaseAPP.css
│   │   │   │   └── 📄 index.js
│   │   │   ├── 📁 performance/    # 성능 테스트 관리
│   │   │   │   ├── 📄 PerformanceTestManager.js
│   │   │   │   └── 📄 index.js
│   │   │   ├── 📁 automation/     # 자동화 테스트 관리
│   │   │   │   ├── 📄 AutomationTestManager.js
│   │   │   │   └── 📄 index.js
│   │   │   ├── 📁 settings/       # 설정 관리
│   │   │   │   ├── 📄 FolderManager.js        # 폴더 설정 (최신화됨)
│   │   │   │   ├── 📄 AccountManager.js       # 계정 관리
│   │   │   │   ├── 📄 ProjectManager.js       # 프로젝트 관리
│   │   │   │   └── 📄 Settings.js             # 메인 설정
│   │   │   └── 📁 utils/          # 유틸리티 컴포넌트
│   │   │       ├── 📄 ErrorBoundary.js
│   │   │       └── 📄 index.js
│   │   ├── 📁 tests/              # 테스트 파일들
│   │   └── 📁 screenshots/        # 스크린샷 이미지들
├── 📁 test-scripts/               # 테스트 스크립트 모음
│   ├── 📁 performance/            # 성능 테스트 스크립트
│   │   ├── 📄 _ENV.js             # 환경 설정
│   │   ├── 📁 advice/             # 법률 자문 관련 테스트
│   │   │   ├── 📄 advice_draft.js
│   │   │   ├── 📄 advice_lagel.js
│   │   │   └── 📄 advice_process.js
│   │   ├── 📁 clm/                # CLM 관련 테스트
│   │   │   ├── 📁 multi/          # 계열사 테스트
│   │   │   │   ├── 📄 clm_draft_multi.js
│   │   │   │   ├── 📄 clm_esign_multi.js
│   │   │   │   └── 📄 clm_final_multi.js
│   │   │   └── 📁 nomerl/         # 단일 그룹 테스트
│   │   │       ├── 📄 clm_draft.js
│   │   │       ├── 📄 clm_esign.js
│   │   │       └── 📄 clm_final.js
│   │   ├── 📁 litigation/         # 송무 관련 테스트
│   │   │   ├── 📄 litigation_draft.js
│   │   │   └── 📄 litigation_schedule.js
│   │   ├── 📁 dashboard/          # 대시보드 테스트
│   │   │   └── 📄 dashboard_setting.js
│   │   ├── 📁 login/              # 로그인 테스트
│   │   │   └── 📄 login_to_dashboard.js
│   │   └── 📁 python/             # Python 기반 K6 GUI
│   │       ├── 📄 k6_gui.py
│   │       └── 📄 k6_options.py
│   └── 📁 playwright/             # Playwright E2E 테스트
│       └── 📄 sample-login.spec.js
├── 📁 docs/                       # 프로젝트 문서
│   ├── 📄 README.md               # 문서 메인
│   ├── 📄 USAGE.md                # 사용법 가이드
│   ├── 📄 DEPLOYMENT_SUCCESS.md   # 배포 성공 가이드
│   ├── 📄 VERCEL_FRONTEND_DEPLOY.md # Vercel 프론트엔드 배포
│   ├── 📄 VERCEL_QUICK_DEPLOY.md  # Vercel 빠른 배포
│   ├── 📄 NEON_SETUP.md           # Neon DB 설정
│   ├── 📄 FREE_HOSTING_OPTIONS.md # 무료 호스팅 옵션
│   ├── 📄 WHITE_SCREEN_FIX.md     # 화이트 스크린 수정
│   └── 📄 LFBZ_performance_README.md # 성능 테스트 가이드
├── 📁 mysql-init/                 # MySQL 초기화 스크립트
│   ├── 📄 01-init.sql             # 기본 데이터베이스 생성
│   └── 📄 02-external-access.sql  # 외부 접근 권한 설정 (최신화됨)
├── 📄 docker-compose.yml          # Docker 서비스 설정 (MySQL + Backend)
├── 📄 setup-mysql-db.sh           # MySQL 데이터베이스 설정 스크립트
├── 📄 env.example                 # 환경 변수 예시 파일
├── 📄 .gitignore                  # Git 무시 파일 목록
└── 📄 README.md                   # 프로젝트 메인 README
```

## 🔧 주요 컴포넌트 상세 설명

### Backend (Flask API)

#### 📄 app.py
- **역할**: 메인 Flask 애플리케이션
- **주요 기능**:
  - 데이터베이스 연결 및 모델 정의
  - API 엔드포인트 구현
  - 환경별 설정 관리 (로컬 MySQL, Vercel SQLite)
  - CORS 및 보안 설정
- **최근 업데이트**: 폴더 API 속성 참조 오류 수정

#### 📁 routes/
- **folders.py**: 폴더 관리 API (계층적 구조 지원)
- **testcases.py**: 테스트 케이스 CRUD API
- **performance.py**: 성능 테스트 결과 관리
- **automation.py**: 자동화 테스트 관리
- **dashboard.py**: 대시보드 데이터 API
- **users.py**: 사용자 인증 및 권한 관리

#### 📁 engines/
- **k6_engine.py**: K6 성능 테스트 엔진 연동
- **playwright_engine.py**: Playwright 자동화 테스트 엔진

### Frontend (React)

#### 📁 components/dashboard/
- **UnifiedDashboard.js**: 통합 대시보드 메인 컴포넌트
- **FolderManager.js**: 폴더 구조 시각화 및 관리

#### 📁 components/testcases/
- **TestCaseAPP.js**: 테스트 케이스 관리 메인 앱
- **주요 기능**:
  - 폴더별 테스트 케이스 필터링
  - Excel 파일 업로드
  - 카테고리별 분류
  - 계층적 폴더 구조 표시

#### 📁 components/settings/
- **FolderManager.js**: 폴더 설정 및 관리
- **AccountManager.js**: 계정 정보 관리
- **ProjectManager.js**: 프로젝트 설정

### Database & Infrastructure

#### 📁 mysql-init/
- **01-init.sql**: 데이터베이스 및 테이블 생성
- **02-external-access.sql**: 외부 접근 권한 설정
  - `root@%` 사용자 생성
  - `testuser@%` 사용자 생성
  - 모든 환경에서 접근 가능하도록 설정

#### 📄 docker-compose.yml
- **MySQL 8.0**: 메인 데이터베이스
- **Backend**: Flask API 서버 (포트 8000)
- **네트워크**: 외부 접근 가능한 설정

## 🚀 배포 구조

### Vercel 배포
- **Backend**: `backend/vercel.json` 설정
- **Frontend**: `frontend/vercel.json` 설정
- **환경 변수**: Vercel Dashboard에서 관리

### 로컬 개발 환경
- **Docker MySQL**: `docker-compose up -d mysql`
- **Flask Backend**: `python app.py` (포트 8000)
- **React Frontend**: `npm start` (포트 3000)

## 📊 데이터 모델

### Folder 모델
```python
class Folder(db.Model):
    __tablename__ = 'Folders'
    id = db.Column(db.Integer, primary_key=True)
    folder_name = db.Column(db.String(100), nullable=False)
    folder_type = db.Column(db.String(50), default='environment')
    environment = db.Column(db.String(50), default='dev')
    deployment_date = db.Column(db.Date, nullable=True)
    parent_folder_id = db.Column(db.Integer, db.ForeignKey('Folders.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 폴더 구조
- **환경 폴더**: DEV, ALPHA, PRODUCTION
- **배포일자 폴더**: YYYY-MM-DD 형식
- **기능명 폴더**: CLM/Draft, Litigation/Schedule 등

## 🔧 최근 해결된 문제

### ✅ 완료된 수정사항
1. **폴더 API 500 에러**: `Folder.name` → `Folder.folder_name` 속성 참조 수정
2. **폴더 타입 "미분류"**: API 응답 형식 통일
3. **테스트 케이스 폴더 구조**: 프론트엔드 속성 참조 수정
4. **Vercel 배포**: 환경 변수 및 설정 최적화

### 🚧 진행 중인 이슈
- **Vercel 인증**: 401 Authentication Required 오류 (GitHub SSO 관련)

## 📈 성능 및 확장성

### 데이터베이스 최적화
- **연결 풀링**: SQLAlchemy 엔진 옵션 설정
- **타임아웃 설정**: 연결, 읽기, 쓰기 타임아웃 관리
- **SSL 모드**: Vercel 환경에서 안전한 연결

### API 최적화
- **CORS 설정**: 모든 환경에서 접근 가능
- **에러 핸들링**: 상세한 에러 메시지 및 로깅
- **비동기 처리**: Promise.all을 통한 병렬 API 호출

## 🔒 보안 설정

### 인증 및 권한
- **JWT 토큰**: 사용자 인증
- **역할 기반 접근 제어**: User, Admin 권한 분리
- **API 보안**: CORS, 헤더 보안 설정

### 데이터 보호
- **환경 변수**: 민감한 정보 분리
- **데이터베이스 접근**: 제한된 사용자 권한
- **HTTPS**: Vercel 환경에서 자동 SSL 적용
