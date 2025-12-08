# 🚀 Integrated Test Platform

## 📋 프로젝트 개요

통합 테스트 플랫폼은 다양한 테스트 유형(API, 성능, 자동화)을 통합 관리할 수 있는 웹 기반 플랫폼입니다.

## ✨ 주요 기능

- **🧪 Test Cases**: 테스트 케이스 관리 및 실행
- **⚡ Performance Tests**: K6 기반 성능 테스트
- **🤖 Automation Tests**: Playwright 기반 자동화 테스트
- **📁 Folder Management**: 계층적 폴더 구조 관리
- **📊 Dashboard**: 테스트 결과 통계 및 분석
- **👥 User Management**: 사용자 및 프로젝트 관리
- **🌍 KST 시간대**: 한국 표준시 기반 일관된 시간 처리
- **☁️ S3 Integration**: AWS S3를 통한 테스트 스크립트 클라우드 저장
- **💻 Code Editor**: Monaco Editor 기반 고급 코드 에디터
- **📝 Script Management**: 테스트 스크립트 생성, 편집, 관리

## 🏗️ 기술 스택

### Backend
- **Python 3.13+**
- **Flask 2.3+**
- **SQLAlchemy 2.0+**
- **MySQL 8.0+**
- **Docker**
- **pytz**: KST 시간대 처리
- **boto3**: AWS S3 연동

### Frontend
- **React 18+**
- **Axios**
- **Chart.js**
- **Monaco Editor**: 고급 코드 에디터

### Testing Tools
- **K6** (성능 테스트)
- **Playwright** (자동화 테스트)

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd integrated-test-platform
```

### 2. 백엔드 실행
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 3. 프론트엔드 실행
```bash
cd frontend
npm install
npm start
```

### 4. 데이터베이스 설정
```bash
# Docker로 MySQL 실행
docker-compose up -d mysql

# 또는 스크립트 사용
./scripts/start-ubuntu-mysql.sh

# 데이터베이스 복구 (필요한 경우)
./scripts/restore_local_mysql.sh
```

### 5. 애플리케이션 재시작
```bash
# 전체 애플리케이션 재시작
./scripts/restart-all.sh

# 백엔드만 재시작
./scripts/restart-backend.sh
```

## 📁 프로젝트 구조

```
integrated-test-platform/
├── backend/                 # Flask 백엔드
│   ├── app.py              # 메인 애플리케이션
│   ├── models.py           # 데이터베이스 모델
│   ├── routes/             # API 라우트
│   ├── utils/              # 유틸리티 함수
│   │   └── timezone_utils.py # KST 시간대 처리
│   └── engines/            # 테스트 엔진 (K6, Playwright)
├── frontend/                # React 프론트엔드
│   ├── src/
│   │   ├── components/     # React 컴포넌트
│   │   ├── contexts/       # React Context
│   │   ├── pages/          # 페이지 컴포넌트
│   │   └── config.js       # API 설정
│   └── package.json
├── docs/                    # 문서 및 설정 파일
│   ├── database/           # 데이터베이스 설정 가이드
│   ├── deployment/         # 배포 가이드
│   ├── reports/            # 프로젝트 리포트
│   ├── API_TESTING_GUIDE.md # API 테스트 가이드
│   ├── TESTING_GUIDE.md    # 테스트 가이드
│   └── PROJECT_STRUCTURE.md # 프로젝트 구조
├── scripts/                 # 실행 및 관리 스크립트
│   ├── restart-all.sh      # 전체 애플리케이션 재시작
│   ├── restart-backend.sh  # 백엔드 재시작
│   ├── restore_database.sh # 데이터베이스 복구
│   └── ...                 # 기타 유틸리티 스크립트
├── test-scripts/            # 테스트 스크립트
│   ├── performance/        # K6 성능 테스트
│   └── playwright/         # Playwright 자동화 테스트
├── slack_reporter/          # Slack 리포트 리포터
│   ├── slack_reporter.ts   # Playwright Slack 리포터
│   └── playwright.config.ts # Playwright 설정
└── README.md               # 이 파일
```

## 🔐 권한 시스템

이 플랫폼은 **admin**, **user**, **guest** 세 가지 사용자 역할을 지원합니다.

- **📖 [권한별 기능 가이드](docs/PERMISSION_GUIDE.md)** - 각 역할별 접근 가능한 기능 상세 설명
- **🛡️ JWT 기반 인증** - 보안된 API 접근
- **🔒 역할 기반 접근 제어** - 사용자 권한에 따른 기능 제한

## 🌍 시간대 처리

- **KST (한국 표준시) 기반**: 모든 시간 데이터를 KST로 일관되게 처리
- **백엔드**: `utils/timezone_utils.py`를 통한 KST 시간 생성 및 변환
- **데이터베이스**: 모든 타임스탬프를 KST로 저장
- **API 응답**: KST 시간 형식으로 응답

## 🌐 배포

### Vercel 배포
- **Backend**: `https://backend-alpha-liard.vercel.app`
- **Frontend**: `https://integrated-test-platform-dydlxktca-gyeonggong-parks-projects.vercel.app`

### 환경 변수
```bash
DATABASE_URL=mysql+pymysql://user:password@host:port/database
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

## 📚 문서

### 일반 문서
- **API 가이드**: `docs/API_TESTING_GUIDE.md`
- **Postman 사용법**: `docs/POSTMAN_USAGE_GUIDE.md`
- **프로젝트 구조**: `docs/PROJECT_STRUCTURE.md`
- **테스트 가이드**: `docs/TESTING_GUIDE.md`
- **권한 가이드**: `docs/PERMISSION_GUIDE.md`

### 데이터베이스 관련
- **데이터베이스 설정**: `docs/database/README.md`
- **로컬 MySQL 설정**: `docs/database/LOCAL_DATABASE_SETUP.md`
- **MySQL Workbench 연결**: `docs/database/MYSQL_WORKBENCH_CONNECTION.md`

### 배포 관련
- **배포 가이드**: `docs/deployment/README.md`
- **Vercel 배포**: `docs/deployment/VERCEL_DEPLOYMENT_GUIDE.md`
- **S3 백업**: `docs/deployment/S3_BACKUP_GUIDE.md`

### 리포트
- **테스트 케이스 분석**: `docs/reports/TESTCASE_ANALYSIS_REPORT.md`
- **프로젝트 정리 요약**: `docs/reports/PROJECT_CLEANUP_SUMMARY.md`

### 스크립트
- **스크립트 사용법**: `scripts/README.md`

## 🧪 테스트

### API 테스트
```bash
# Postman Collection 사용
docs/postman_collection_v2.3.0.json
```

### 성능 테스트
```bash
cd test-scripts/performance
k6 run script.js
```

### 자동화 테스트
```bash
cd test-scripts/playwright
npx playwright test
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🆕 최신 기능 (v2.5.0)

### 🤝 협업 및 워크플로우
- **댓글 시스템**: 테스트 케이스, 테스트 결과 등에 댓글 추가/수정/삭제
- **멘션 기능**: `@username` 형식으로 멘션, 자동 알림
- **워크플로우 관리**: 커스텀 워크플로우 정의, 상태 전환, 권한 관리

### 🔗 테스트 의존성 관리
- **의존성 그래프**: 테스트 케이스 간 의존성 시각화
- **실행 순서 계산**: 위상 정렬로 의존성 기반 실행 순서 계산
- **순환 의존성 검사**: 자동 감지 및 방지
- **의존성 조건 확인**: 결과 기반 실행 가능 여부 확인

### 📊 고급 리포트 및 대시보드
- **커스텀 리포트 빌더**: 리포트 타입별 데이터 수집
- **다양한 출력 형식**: HTML, JSON, CSV 지원
- **리포트 실행 기록**: 리포트 생성 이력 관리
- **리포트 다운로드**: 생성된 리포트 파일 다운로드

### ⚡ 성능 최적화
- **Redis 캐싱**: 자주 조회되는 데이터 캐싱
- **응답 압축**: gzip 압축으로 네트워크 전송량 감소
- **캐시 무효화**: 데이터 변경 시 관련 캐시 자동 삭제
- **캐시 데코레이터**: 함수 결과 자동 캐싱

### 🔔 실시간 모니터링 및 알림
- **WebSocket 통신**: Flask-SocketIO 기반 실시간 통신
- **알림 시스템**: 테스트 실행, 스케줄 실행 등 알림
- **사용자별 알림 설정**: 이메일, Slack, 인앱 알림 설정

### ⏰ 자동화 및 스케줄링
- **테스트 스케줄 관리**: 일일, 주간, 월간, cron 스케줄
- **APScheduler 기반**: 백그라운드 스케줄러 서비스
- **스케줄 실행 기록**: 스케줄 실행 이력 관리

### 🔄 병렬 실행 및 큐 관리
- **Celery + Redis**: 비동기 테스트 실행
- **큐 관리 API**: 큐 상태 조회, 작업 취소, 통계
- **워커 모니터링**: 워커 상태 및 통계 조회

### 🔌 CI/CD 통합
- **GitHub Actions**: 웹훅 기반 통합
- **Jenkins**: 웹훅 기반 통합
- **CI/CD 실행 기록**: 실행 이력 및 결과 관리

### 💾 테스트 데이터 관리
- **테스트 데이터 세트**: 데이터 세트 생성, 수정, 삭제
- **데이터 마스킹**: 민감 정보 자동 마스킹
- **버전 관리**: 데이터 세트 버전 관리
- **필드 매핑**: 테스트 케이스와 데이터 세트 매핑
- **동적 데이터 생성**: 스키마 기반 테스트 데이터 생성

### 📈 고급 분석 및 트렌드
- **트렌드 분석**: 테스트 결과 트렌드 분석
- **Flaky 테스트 감지**: 불안정한 테스트 자동 감지
- **회귀 감지**: 테스트 결과 회귀 패턴 감지
- **실행 시간 분석**: 테스트 실행 시간 추적
- **커버리지 분석**: 테스트 커버리지 통계
- **실패 패턴 분석**: 실패 패턴 분석 및 인사이트
- **테스트 헬스**: 테스트 케이스 건강도 평가

### 🧹 프로젝트 정리 및 최적화 (v2.3.0)
- **불필요한 파일 정리**: 로그, 캐시, 임시 파일 자동 정리
- **코드 리팩토링**: 중복 코드 제거 및 구조 개선
- **문서 최신화**: API 문서 및 프로젝트 가이드 업데이트
- **성능 최적화**: 데이터베이스 쿼리 및 응답 시간 개선

### ☁️ S3 통합 테스트 스크립트 관리 (v2.3.0)
- **클라우드 저장**: AWS S3를 통한 테스트 스크립트 클라우드 저장
- **운영 환경 호환**: 로컬 파일 의존성 제거로 운영 환경에서 완전 동작
- **실시간 편집**: Monaco Editor를 통한 고급 코드 편집 기능
- **파일 관리**: 업로드, 다운로드, 삭제, 편집 등 완전한 파일 관리
- **다중 언어 지원**: JavaScript, Python, JSON, Markdown 등 다양한 언어 지원

### 💻 고급 코드 에디터 (v2.3.0)
- **Monaco Editor**: VS Code와 동일한 편집 경험
- **구문 강조**: 프로그래밍 언어별 자동 구문 강조
- **자동 완성**: 스마트 자동 완성 및 IntelliSense
- **폴딩**: 코드 블록 접기/펼치기
- **다크 모드**: 눈에 편한 다크 테마 지원

## 📞 연락처

- 프로젝트 링크: [https://github.com/username/integrated-test-platform](https://github.com/username/integrated-test-platform)
- E-Mail : [bakgg93@gmail.com](bakgg93@gmail.com)
- H.P : 010-8496-1463

---

**마지막 업데이트**: 2025년 12월 8일  
**버전**: 2.6.0  
**상태**: 프로덕션 배포 완료 ✅  
**주요 업데이트**: 
- 프로젝트 파일 구조 정리 (문서 및 스크립트 정리)
- Slack 리포트 기능 추가 (Playwright 테스트 결과 자동 전송)
- 데이터베이스 스키마 개선 (assignee_id 컬럼 추가)
- JIRA 환경별 통계 API 추가
