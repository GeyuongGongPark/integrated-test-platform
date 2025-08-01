# Integrated Test Platform

통합 테스트 플랫폼으로, 웹 애플리케이션 테스트와 성능 테스트를 위한 종합적인 솔루션입니다.

## 프로젝트 구조

```
integrated-test-platform/
├── backend/                 # Flask 백엔드
│   ├── app.py              # 메인 Flask 애플리케이션
│   ├── requirements.txt    # Python 의존성
│   ├── test_management.db # SQLite 데이터베이스
│   └── venv/              # Python 가상환경
├── frontend/               # React 프론트엔드
│   ├── src/               # React 소스 코드
│   ├── public/            # 정적 파일
│   ├── package.json       # Node.js 의존성
│   └── build/             # 빌드 결과물
├── test-scripts/          # 성능 테스트 스크립트
│   └── performance/       # k6 성능 테스트
│       ├── login/         # 로그인 테스트
│       ├── clm/           # 계약 검토 테스트
│       ├── advice/        # 법률 자문 테스트
│       ├── litigation/    # 송무 테스트
│       ├── dashboard/     # 대시보드 테스트
│       ├── common/        # 공통 유틸리티
│       └── url/           # URL 설정
├── docs/                  # 문서
│   ├── INTEGRATION_PLAN.md
│   └── LFBZ_performance_README.md
├── README.md              # 프로젝트 개요
└── USAGE.md               # 사용법 가이드
```

## 주요 기능

### 1. 웹 애플리케이션 테스트 관리
- **프로젝트 관리**: 테스트 프로젝트 생성 및 관리
- **테스트 케이스 관리**: 체계적인 테스트 케이스 CRUD
- **테스트 결과 관리**: Pass/Fail/N/T/N/A/Block 상태 관리
- **스크린샷 관리**: 테스트 실행 시 자동 스크린샷 저장

### 2. 성능 테스트 자동화
- **k6 기반 성능 테스트**: 브라우저 자동화 테스트
- **다양한 시나리오**: 로그인, 계약 검토, 법률 자문, 송무 등
- **환경별 설정**: 개발/스테이징/프로덕션 환경 지원
- **결과 리포트**: HTML 형태의 상세한 테스트 결과

## 빠른 시작

### 1. 백엔드 실행
```bash
cd integrated-test-platform/backend

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는 venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

백엔드 서버는 `http://localhost:8000`에서 실행됩니다.

### 2. 프론트엔드 실행
```bash
cd integrated-test-platform/frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

프론트엔드는 `http://localhost:3000`에서 실행됩니다.

### 3. 성능 테스트 실행
```bash
cd integrated-test-platform/test-scripts/performance

# 로그인 테스트 실행
k6 run login/login_to_dashboard.js

# CLM 테스트 실행
k6 run clm/nomerl/clm_draft.js

# 법률 자문 테스트 실행
k6 run advice/advice_draft.js
```

## 성능 테스트 스크립트

### 환경 설정
- **환경 변수**: `url/env_data.json`에서 환경별 설정
- **URL 설정**: `url/base.js`에서 API 엔드포인트 관리
- **셀렉터**: `url/config.js`에서 UI 요소 셀렉터 관리

### 테스트 시나리오

#### 로그인 테스트
```bash
k6 run login/login_to_dashboard.js
```
- 사용자 로그인 프로세스 테스트
- 대시보드 접근 확인
- 스크린샷 자동 저장

#### CLM (계약 검토) 테스트
```bash
# 신규 계약 테스트
k6 run clm/nomerl/clm_draft.new.js

# 변경 계약 테스트
k6 run clm/nomerl/clm_draft.change.js

# 해지 계약 테스트
k6 run clm/nomerl/clm_draft.stop.js
```

#### 법률 자문 테스트
```bash
k6 run advice/advice_draft.js
```

#### 송무 테스트
```bash
k6 run litigation/litigation_draft.js
```

### 환경 변수 설정

테스트 실행 시 환경 변수를 통해 동작을 제어할 수 있습니다:

```bash
# 기본 환경
k6 run -e DRAFT_TYPE=new -e EDITOR_USE=use clm/nomerl/clm_draft.js

# 변경 계약 테스트
k6 run -e DRAFT_TYPE=change -e CONTRACT_TYPE=file clm/nomerl/clm_draft.js

# 편집기 사용 안함
k6 run -e EDITOR_USE=no clm/nomerl/clm_draft.js
```

## API 엔드포인트

### 프로젝트 관리
- `GET /projects` - 프로젝트 목록 조회
- `POST /projects` - 프로젝트 생성

### 테스트 케이스 관리
- `GET /testcases` - 테스트 케이스 목록 조회
- `POST /testcases` - 테스트 케이스 생성
- `PUT /testcases/<id>/status` - 테스트 케이스 상태 업데이트
- `DELETE /testcases/<id>` - 테스트 케이스 삭제

### 테스트 결과 관리
- `GET /testresults/<test_case_id>` - 테스트 결과 조회
- `POST /testresults` - 테스트 결과 생성

## 데이터베이스

### SQLite 기반
- **파일 위치**: `backend/test_management.db`
- **데이터 지속성**: 서버 재시작 후에도 데이터 유지
- **자동 백업**: 데이터베이스 파일 복사로 백업 가능

### 주요 테이블
- `projects`: 프로젝트 정보
- `TestCases`: 테스트 케이스 정보
- `TestResults`: 테스트 실행 결과
- `Screenshots`: 스크린샷 파일 정보
- `Folders`: 폴더 구조 관리

## 개발 환경

### 백엔드 (Flask)
- **Python 3.13**
- **Flask**: 웹 프레임워크
- **SQLAlchemy**: ORM
- **Flask-CORS**: CORS 지원

### 프론트엔드 (React)
- **Node.js 18+**
- **React 18**
- **Material-UI**: UI 컴포넌트

### 성능 테스트 (k6)
- **k6**: 브라우저 자동화 테스트
- **Playwright**: 브라우저 제어
- **HTML Reporter**: 테스트 결과 리포트

## 문제 해결

### 포트 충돌
```bash
# 백엔드 포트 확인
lsof -i :8000

# 프론트엔드 포트 확인
lsof -i :3000

# 프로세스 종료
kill -9 [PID]
```

### 가상환경 문제
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 데이터베이스 초기화
```bash
cd backend
rm -f test_management.db
python app.py
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 연락처

프로젝트 관련 문의사항이 있으시면 이슈를 등록해 주세요.
