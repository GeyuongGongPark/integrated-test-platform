# 프로젝트 구조 상세 가이드

## 📁 전체 프로젝트 구조

```
integrated-test-platform/
├── 📁 backend/                    # Flask 백엔드 API 서버
│   ├── 📄 app.py                  # 메인 Flask 애플리케이션 (KST 시간대 처리 완료)
│   ├── 📄 vercel.json             # Vercel 배포 설정
│   ├── 📄 requirements.txt        # Python 의존성 (pytz 추가)
│   ├── 📄 Dockerfile              # Docker 컨테이너 설정
│   ├── 📁 engines/                # 테스트 엔진 모듈
│   │   ├── 📄 __init__.py
│   │   └── 📄 k6_engine.py        # K6 성능 테스트 엔진
│   ├── 📁 routes/                 # API 라우트 모듈 (KST 시간대 처리 완료)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth.py             # 인증 API
│   │   ├── 📄 folders.py          # 폴더 관리 API
│   │   ├── 📄 testcases.py        # 테스트 케이스 API
│   │   ├── 📄 testcases_extended.py # 확장 테스트 케이스 API
│   │   ├── 📄 performance.py      # 성능 테스트 API
│   │   ├── 📄 automation.py       # 자동화 테스트 API
│   │   ├── 📄 dashboard_extended.py # 확장 대시보드 API
│   │   └── 📄 users.py            # 사용자 관리 API
│   ├── 📁 utils/                  # 유틸리티 모듈
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth.py             # 인증 관련 유틸리티
│   │   ├── 📄 auth_decorators.py  # 인증 데코레이터
│   │   ├── 📄 cors.py             # CORS 설정
│   │   └── 📄 timezone_utils.py   # KST 시간대 처리 유틸리티 (신규)
│   ├── 📁 migrations/             # 데이터베이스 마이그레이션
│   │   ├── 📄 alembic.ini
│   │   ├── 📄 env.py
│   │   └── 📁 versions/           # 마이그레이션 버전 파일들
│   ├── 📁 config/                 # 설정 파일들
│   ├── 📁 logs/                   # 로그 파일들
│   ├── 📁 tests/                  # 백엔드 테스트
│   └── 📁 venv/                   # Python 가상환경
├── 📁 frontend/                   # React 프론트엔드 애플리케이션
│   ├── 📄 package.json            # Node.js 의존성
│   ├── 📄 vercel.json             # Vercel 프론트엔드 배포 설정
│   ├── 📁 src/                    # 소스 코드
│   │   ├── 📄 App.js              # 메인 React 컴포넌트
│   │   ├── 📄 index.js            # 애플리케이션 진입점
│   │   ├── 📄 config.js           # 환경별 API 설정
│   │   ├── 📁 components/         # React 컴포넌트들
│   │   │   ├── 📁 dashboard/      # 대시보드 관련 컴포넌트
│   │   │   │   ├── 📄 UnifiedDashboard.js    # 통합 대시보드
│   │   │   │   ├── 📄 FolderManager.js        # 폴더 관리
│   │   │   │   └── 📄 index.js
│   │   │   ├── 📁 testcases/      # 테스트 케이스 관리
│   │   │   │   ├── 📄 TestCaseAPP.js          # 메인 테스트 케이스 앱
│   │   │   │   ├── 📄 TestCaseAPP.css
│   │   │   │   └── 📄 index.js
│   │   │   ├── 📁 performance/    # 성능 테스트 관리
│   │   │   │   ├── 📄 PerformanceTestManager.js
│   │   │   │   └── 📄 index.js
│   │   │   ├── 📁 automation/     # 자동화 테스트 관리
│   │   │   │   ├── 📄 AutomationTestManager.js
│   │   │   │   └── 📄 index.js
│   │   │   ├── 📁 settings/       # 설정 관리
│   │   │   │   ├── 📄 FolderManager.js        # 폴더 설정
│   │   │   │   ├── 📄 AccountManager.js       # 계정 관리
│   │   │   │   ├── 📄 ProjectManager.js       # 프로젝트 관리
│   │   │   │   └── 📄 Settings.js             # 메인 설정
│   │   │   ├── 📁 auth/           # 인증 관련 컴포넌트
│   │   │   │   ├── 📄 Login.js                 # 로그인
│   │   │   │   └── 📄 index.js
│   │   │   └── 📁 utils/          # 유틸리티 컴포넌트
│   │   │       ├── 📄 ErrorBoundary.js
│   │   │       └── 📄 index.js
│   │   ├── 📁 contexts/           # React Context
│   │   │   └── 📄 AuthContext.js  # 인증 컨텍스트
│   │   ├── 📁 hooks/              # 커스텀 훅
│   │   ├── 📁 pages/              # 페이지 컴포넌트
│   │   ├── 📁 services/           # API 서비스
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
│   │   ├── 📁 python/             # Python 기반 K6 GUI
│   │   │   ├── 📄 k6_gui.py
│   │   │   └── 📄 k6_options.py
│   │   ├── 📁 url/                 # URL 테스트
│   │   ├── 📁 screenshots/        # 테스트 스크린샷
│   │   ├── 📄 quick_test.js       # 빠른 테스트
│   │   └── 📄 simple_test.js      # 간단 테스트
│   └── 📁 playwright/             # Playwright E2E 테스트
│       └── 📄 sample-login.spec.js
├── 📁 docs/                       # 프로젝트 문서
│   ├── 📄 README.md               # 문서 메인
│   ├── 📄 PROJECT_STRUCTURE.md    # 프로젝트 구조 (이 파일)
│   ├── 📄 API_TESTING_GUIDE.md    # API 테스트 가이드
│   ├── 📄 TESTING_GUIDE.md        # 테스트 가이드
│   ├── 📄 PERMISSION_GUIDE.md     # 권한별 기능 가이드
│   ├── 📄 AUTH_SYSTEM_PLAN.md     # 인증 시스템 계획
│   ├── 📄 JIRA_INTEGRATION_PLAN.md # JIRA 통합 계획
│   ├── 📄 POSTMAN_USAGE_GUIDE.md  # Postman 사용법
│   ├── 📄 DEPLOYMENT_SUMMARY.md   # 배포 요약
│   ├── 📄 VERCEL_DEPLOYMENT_GUIDE.md # Vercel 배포 가이드
│   ├── 📄 UBUNTU_MYSQL_SETUP.md  # Ubuntu MySQL 설정
│   ├── 📄 MYSQL_WORKBENCH_CONNECTION.md # MySQL Workbench 연결
│   ├── 📄 postman_collection_v2.json # Postman 컬렉션 v2
│   ├── 📄 postman_environment_v2.json # Postman 환경 v2
│   ├── 📄 env.example             # 환경 변수 예시
│   └── 📁 mysql-init/             # MySQL 초기화 스크립트
├── 📁 config/                     # 설정 파일들
│   └── 📁 mysql-init/             # MySQL 초기화
├── 📁 logs/                       # 로그 파일들
├── 📁 screenshots/                # 프로젝트 스크린샷
├── 📁 ubuntu-setup/               # Ubuntu 설정 스크립트
├── 📄 docker-compose.yml          # Docker Compose 설정
├── 📄 docker-compose.ubuntu.yml   # Ubuntu용 Docker Compose
├── 📄 start-ubuntu-mysql.sh       # Ubuntu MySQL 시작 스크립트
├── 📄 mysql-tunnel.sh             # MySQL 터널 스크립트
├── 📄 my.cnf                      # MySQL 설정
├── 📄 .gitignore                  # Git 무시 파일
├── 📄 .vercel/                    # Vercel 설정
└── 📄 README.md                   # 프로젝트 메인 README
```

## 🔧 주요 변경사항 (2025년 8월 27일)

### ✅ 정리된 파일들
- **백엔드 정리 스크립트들**: 일회성 데이터 정리 스크립트들 모두 제거
- **중복 Postman 파일**: v1 파일들 제거, v2만 유지
- **불필요한 설정 파일**: 중복 docker-compose.yml 제거

### 🌍 KST 시간대 처리 구현
- **timezone_utils.py**: KST 시간 처리 전용 유틸리티 모듈
- **모든 모델**: created_at, updated_at 등 시간 필드를 KST 기반으로 변경
- **모든 API**: 응답 시간을 KST로 통일
- **파일명 생성**: KST 기반 타임스탬프 사용

### 📱 프론트엔드 로그 정리
- **콘솔 로그 최소화**: 보안을 위한 불필요한 로그 제거
- **개발/프로덕션 환경 분리**: 환경별 로그 레벨 조정

## 🗂️ 파일 정리 원칙

1. **일회성 스크립트**: 문제 해결 후 즉시 삭제
2. **중복 파일**: 최신 버전만 유지
3. **보안**: 민감한 정보가 포함된 로그 제거
4. **일관성**: 시간대, 로깅 등 시스템 전반의 일관성 유지

## 📊 현재 상태

- **백엔드**: KST 시간대 처리 완료, 정리 스크립트 제거
- **프론트엔드**: 로그 정리 완료, KST 시간 표시
- **데이터베이스**: KST 시간 저장 완료
- **문서**: 최신화 완료

---

**마지막 업데이트**: 2025년 8월 27일  
**버전**: 2.1.0  
**상태**: 프로덕션 배포 완료 ✅
