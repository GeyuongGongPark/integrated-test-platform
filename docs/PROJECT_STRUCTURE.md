# 프로젝트 구조 상세 가이드

## 📁 전체 프로젝트 구조

```
integrated-test-platform/
├── 📁 backend/                    # Flask 백엔드 API 서버
│   ├── 📄 app.py                  # 메인 Flask 애플리케이션
│   ├── 📄 celery_app.py          # Celery 비동기 작업 설정
│   ├── 📄 tasks.py               # Celery 태스크 정의
│   ├── 📄 socketio_handlers.py  # WebSocket 이벤트 핸들러
│   ├── 📄 vercel.json            # Vercel 배포 설정
│   ├── 📄 requirements.txt       # Python 의존성
│   ├── 📄 Dockerfile             # Docker 컨테이너 설정
│   ├── 📁 engines/               # 테스트 엔진 모듈
│   │   ├── 📄 __init__.py
│   │   └── 📄 k6_engine.py      # K6 성능 테스트 엔진
│   ├── 📁 routes/                # API 라우트 모듈
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth.py            # 인증 API
│   │   ├── 📄 folders.py         # 폴더 관리 API
│   │   ├── 📄 testcases.py       # 테스트 케이스 API
│   │   ├── 📄 testcases_extended.py # 확장 테스트 케이스 API
│   │   ├── 📄 performance.py    # 성능 테스트 API
│   │   ├── 📄 automation.py      # 자동화 테스트 API
│   │   ├── 📄 dashboard_extended.py # 확장 대시보드 API
│   │   ├── 📄 users.py           # 사용자 관리 API
│   │   ├── 📄 jira_issues.py     # JIRA 이슈 관리 API
│   │   ├── 📄 schedules.py       # 테스트 스케줄 관리 API
│   │   ├── 📄 queue.py           # 큐 관리 API
│   │   ├── 📄 notifications.py   # 알림 관리 API
│   │   ├── 📄 analytics.py       # 분석 및 트렌드 API
│   │   ├── 📄 cicd.py            # CI/CD 통합 API
│   │   ├── 📄 test_data.py       # 테스트 데이터 관리 API
│   │   ├── 📄 collaboration.py   # 협업 및 워크플로우 API
│   │   ├── 📄 dependencies.py    # 테스트 의존성 관리 API
│   │   └── 📄 reports.py         # 커스텀 리포트 API
│   ├── 📁 services/              # 비즈니스 로직 서비스
│   │   ├── 📄 scheduler_service.py    # 스케줄러 서비스
│   │   ├── 📄 notification_service.py # 알림 서비스
│   │   ├── 📄 cicd_service.py         # CI/CD 서비스
│   │   ├── 📄 test_data_service.py    # 테스트 데이터 서비스
│   │   ├── 📄 collaboration_service.py # 협업 서비스
│   │   ├── 📄 dependency_service.py    # 의존성 서비스
│   │   ├── 📄 report_service.py        # 리포트 서비스
│   │   └── 📄 cache_service.py         # 캐싱 서비스
│   ├── 📁 utils/                 # 유틸리티 모듈
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth.py            # 인증 관련 유틸리티
│   │   ├── 📄 auth_decorators.py # 인증 데코레이터
│   │   ├── 📄 cors.py            # CORS 설정
│   │   ├── 📄 timezone_utils.py  # KST 시간대 처리 유틸리티
│   │   ├── 📄 compression.py     # 응답 압축 유틸리티
│   │   └── 📄 logger.py          # 로깅 유틸리티
│   ├── 📁 migrations/            # 데이터베이스 마이그레이션
│   │   ├── 📄 alembic.ini
│   │   ├── 📄 env.py
│   │   └── 📁 versions/          # 마이그레이션 버전 파일들
│   ├── 📁 config/                # 설정 파일들
│   ├── 📁 logs/                  # 로그 파일들
│   ├── 📁 tests/                 # 백엔드 테스트
│   └── 📁 venv/                  # Python 가상환경
├── 📁 frontend/                  # React 프론트엔드 애플리케이션
│   ├── 📄 package.json           # Node.js 의존성
│   ├── 📄 vercel.json            # Vercel 프론트엔드 배포 설정
│   ├── 📁 src/                   # 소스 코드
│   │   ├── 📄 App.js             # 메인 React 컴포넌트
│   │   ├── 📄 index.js           # 애플리케이션 진입점
│   │   ├── 📄 config.js          # 환경별 API 설정
│   │   ├── 📁 components/        # React 컴포넌트들
│   │   │   ├── 📁 dashboard/     # 대시보드 관련 컴포넌트
│   │   │   ├── 📁 testcases/     # 테스트 케이스 관리
│   │   │   ├── 📁 performance/   # 성능 테스트 관리
│   │   │   ├── 📁 automation/     # 자동화 테스트 관리
│   │   │   ├── 📁 settings/      # 설정 관리
│   │   │   ├── 📁 auth/          # 인증 관련 컴포넌트
│   │   │   └── 📁 utils/         # 유틸리티 컴포넌트
│   │   ├── 📁 contexts/         # React Context
│   │   │   └── 📄 AuthContext.js # 인증 컨텍스트
│   │   ├── 📁 hooks/             # 커스텀 훅
│   │   ├── 📁 pages/             # 페이지 컴포넌트
│   │   ├── 📁 services/          # API 서비스
│   │   └── 📁 tests/             # 테스트 파일들
│   └── 📁 screenshots/           # 스크린샷 이미지들
├── 📁 test-scripts/              # 테스트 스크립트 모음
│   ├── 📁 performance/           # 성능 테스트 스크립트
│   └── 📁 playwright/            # Playwright E2E 테스트
├── 📁 docs/                      # 프로젝트 문서
│   ├── 📄 README.md              # 문서 메인
│   ├── 📄 PROJECT_STRUCTURE.md   # 프로젝트 구조 (이 파일)
│   ├── 📄 API_TESTING_GUIDE.md   # API 테스트 가이드
│   ├── 📄 TESTING_GUIDE.md      # 테스트 가이드
│   ├── 📄 PERMISSION_GUIDE.md    # 권한별 기능 가이드
│   ├── 📄 AUTH_SYSTEM_PLAN.md   # 인증 시스템 계획
│   ├── 📄 JIRA_INTEGRATION_PLAN.md # JIRA 통합 계획
│   ├── 📄 POSTMAN_USAGE_GUIDE.md # Postman 사용법
│   ├── 📄 DEPLOYMENT_SUMMARY.md # 배포 요약
│   ├── 📄 postman_collection_v2.4.0_complete.json # Postman 컬렉션
│   └── 📁 mysql-init/            # MySQL 초기화 스크립트
├── 📁 config/                    # 설정 파일들
├── 📁 logs/                      # 로그 파일들
├── 📁 screenshots/               # 프로젝트 스크린샷
├── 📁 ubuntu-setup/              # Ubuntu 설정 스크립트
├── 📄 docker-compose.yml        # Docker Compose 설정
├── 📄 docker-compose.ubuntu.yml # Ubuntu용 Docker Compose
└── 📄 README.md                 # 프로젝트 메인 README
```

## 🔧 주요 변경사항 (2025년 1월 9일)

### ✅ 고급 기능 구현 완료

#### 1. 협업 및 워크플로우
- **댓글 시스템**: 테스트 케이스, 테스트 결과 등에 댓글 추가/수정/삭제
- **멘션 기능**: `@username` 형식으로 멘션, 자동 알림
- **워크플로우 관리**: 커스텀 워크플로우 정의, 상태 전환, 권한 관리

#### 2. 테스트 의존성 관리
- **의존성 그래프**: 테스트 케이스 간 의존성 시각화
- **실행 순서 계산**: 위상 정렬로 의존성 기반 실행 순서 계산
- **순환 의존성 검사**: 자동 감지 및 방지
- **의존성 조건 확인**: 결과 기반 실행 가능 여부 확인

#### 3. 고급 리포트 및 대시보드
- **커스텀 리포트 빌더**: 리포트 타입별 데이터 수집
- **다양한 출력 형식**: HTML, JSON, CSV 지원
- **리포트 실행 기록**: 리포트 생성 이력 관리
- **리포트 다운로드**: 생성된 리포트 파일 다운로드

#### 4. 성능 최적화
- **Redis 캐싱**: 자주 조회되는 데이터 캐싱
- **응답 압축**: gzip 압축으로 네트워크 전송량 감소
- **캐시 무효화**: 데이터 변경 시 관련 캐시 자동 삭제
- **캐시 데코레이터**: 함수 결과 자동 캐싱

#### 5. 실시간 모니터링 및 알림
- **WebSocket 통신**: Flask-SocketIO 기반 실시간 통신
- **알림 시스템**: 테스트 실행, 스케줄 실행 등 알림
- **사용자별 알림 설정**: 이메일, Slack, 인앱 알림 설정

#### 6. 자동화 및 스케줄링
- **테스트 스케줄 관리**: 일일, 주간, 월간, cron 스케줄
- **APScheduler 기반**: 백그라운드 스케줄러 서비스
- **스케줄 실행 기록**: 스케줄 실행 이력 관리

#### 7. 병렬 실행 및 큐 관리
- **Celery + Redis**: 비동기 테스트 실행
- **큐 관리 API**: 큐 상태 조회, 작업 취소, 통계
- **워커 모니터링**: 워커 상태 및 통계 조회

#### 8. CI/CD 통합
- **GitHub Actions**: 웹훅 기반 통합
- **Jenkins**: 웹훅 기반 통합
- **CI/CD 실행 기록**: 실행 이력 및 결과 관리

#### 9. 테스트 데이터 관리
- **테스트 데이터 세트**: 데이터 세트 생성, 수정, 삭제
- **데이터 마스킹**: 민감 정보 자동 마스킹
- **버전 관리**: 데이터 세트 버전 관리
- **필드 매핑**: 테스트 케이스와 데이터 세트 매핑
- **동적 데이터 생성**: 스키마 기반 테스트 데이터 생성

#### 10. 고급 분석 및 트렌드
- **트렌드 분석**: 테스트 결과 트렌드 분석
- **Flaky 테스트 감지**: 불안정한 테스트 자동 감지
- **회귀 감지**: 테스트 결과 회귀 패턴 감지
- **실행 시간 분석**: 테스트 실행 시간 추적
- **커버리지 분석**: 테스트 커버리지 통계
- **실패 패턴 분석**: 실패 패턴 분석 및 인사이트
- **테스트 헬스**: 테스트 케이스 건강도 평가

### 🌍 KST 시간대 처리 구현
- **timezone_utils.py**: KST 시간 처리 전용 유틸리티 모듈
- **모든 모델**: created_at, updated_at 등 시간 필드를 KST 기반으로 변경
- **모든 API**: 응답 시간을 KST로 통일
- **파일명 생성**: KST 기반 타임스탬프 사용

### 📱 프론트엔드 로그 정리
- **콘솔 로그 최소화**: 보안을 위한 불필요한 로그 제거
- **개발/프로덕션 환경 분리**: 환경별 로그 레벨 조정

### 🧹 코드 리팩토링
- **중복 코드 제거**: 반복되는 로직 통합 및 모듈화
- **구조 개선**: 파일 구조 및 네이밍 컨벤션 통일
- **성능 최적화**: 데이터베이스 쿼리 및 응답 시간 개선

## 🗂️ 파일 정리 원칙

1. **일회성 스크립트**: 문제 해결 후 즉시 삭제
2. **중복 파일**: 최신 버전만 유지
3. **보안**: 민감한 정보가 포함된 로그 제거
4. **일관성**: 시간대, 로깅 등 시스템 전반의 일관성 유지
5. **성능**: 불필요한 파일로 인한 성능 저하 방지

## 📊 현재 상태

- **백엔드**: KST 시간대 처리 완료, 코드 리팩토링 완료, 고급 기능 구현 완료
- **프론트엔드**: 로그 정리 완료, KST 시간 표시
- **데이터베이스**: KST 시간 저장 완료, 쿼리 최적화
- **문서**: 최신화 완료, API 문서 업데이트
- **프로젝트**: 불필요한 파일 정리 완료

## 🚀 새로운 API 엔드포인트

### 협업 및 워크플로우 (`/collaboration`)
- `GET /comments` - 댓글 목록 조회
- `POST /comments` - 댓글 생성
- `PUT /comments/{id}` - 댓글 수정
- `DELETE /comments/{id}` - 댓글 삭제
- `GET /mentions` - 멘션 목록 조회
- `POST /mentions/{id}/read` - 멘션 읽음 처리
- `GET /workflows` - 워크플로우 목록 조회
- `POST /workflows` - 워크플로우 생성
- `POST /workflows/{id}/apply` - 워크플로우 적용
- `POST /workflows/transition` - 워크플로우 상태 전환

### 테스트 의존성 관리 (`/dependencies`)
- `GET /dependencies` - 의존성 목록 조회
- `POST /dependencies` - 의존성 생성
- `GET /dependencies/graph` - 의존성 그래프 조회
- `POST /dependencies/execution-order` - 실행 순서 계산
- `GET /dependencies/testcases/{id}/check` - 의존성 조건 확인

### 커스텀 리포트 (`/reports`)
- `GET /reports` - 리포트 목록 조회
- `POST /reports` - 리포트 생성
- `POST /reports/{id}/generate` - 리포트 생성 및 실행
- `GET /reports/executions/{id}/download` - 리포트 다운로드

### 테스트 데이터 관리 (`/test-data`)
- `GET /test-data/datasets` - 데이터 세트 목록 조회
- `POST /test-data/datasets` - 데이터 세트 생성
- `POST /test-data/datasets/{id}/versions` - 버전 생성
- `GET /test-data/mappings` - 매핑 목록 조회
- `POST /test-data/generate` - 동적 데이터 생성

### 알림 시스템 (`/notifications`)
- `GET /notifications` - 알림 목록 조회
- `POST /notifications/{id}/read` - 알림 읽음 처리
- `GET /notifications/settings` - 알림 설정 조회
- `PUT /notifications/settings` - 알림 설정 업데이트

### 스케줄 관리 (`/schedules`)
- `GET /schedules` - 스케줄 목록 조회
- `POST /schedules` - 스케줄 생성
- `POST /schedules/{id}/run-now` - 즉시 실행
- `POST /schedules/{id}/toggle` - 활성화/비활성화

### 큐 관리 (`/queue`)
- `POST /queue/testcases/{id}/execute` - 테스트 케이스 큐에 추가
- `GET /queue/tasks/{task_id}` - 작업 상태 조회
- `GET /queue/stats` - 큐 통계 조회
- `GET /queue/workers` - 워커 상태 조회

### 분석 및 트렌드 (`/analytics`)
- `GET /analytics/trends` - 트렌드 분석
- `GET /analytics/flaky-tests` - Flaky 테스트 감지
- `GET /analytics/regression-detection` - 회귀 감지
- `GET /analytics/test-health` - 테스트 헬스 분석

### CI/CD 통합 (`/cicd`)
- `GET /cicd/integrations` - 통합 목록 조회
- `POST /cicd/integrations` - 통합 생성
- `POST /cicd/webhook/github` - GitHub 웹훅
- `POST /cicd/webhook/jenkins` - Jenkins 웹훅

---

**마지막 업데이트**: 2025년 1월 9일  
**버전**: 2.5.0  
**상태**: 프로덕션 배포 완료 ✅
