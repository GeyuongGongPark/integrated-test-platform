# 🚀 Integrated Test Platform

완전한 클라우드 기반 테스트 관리 플랫폼입니다. 백엔드와 프론트엔드가 모두 Vercel에 배포되어 있으며, GitHub Actions를 통한 자동 CI/CD 파이프라인이 구축되어 있습니다.

## 🌟 주요 기능

### 📋 테스트 케이스 관리
- **CRUD 작업**: 테스트 케이스 생성, 조회, 수정, 삭제
- **카테고리 분류**: 메인/서브/상세 카테고리로 체계적 관리
- **상태 관리**: N/T, Pass, Fail 등 테스트 결과 상태 관리
- **결과 기록**: 테스트 실행 결과 및 노트 기록

### ⚡ 성능 테스트 관리
- **K6 스크립트**: 성능 테스트 스크립트 관리
- **실행 엔진**: K6 기반 성능 테스트 실행
- **결과 분석**: 응답 시간, 처리량, 에러율 등 성능 지표 분석
- **리포트 생성**: 성능 테스트 결과 리포트 생성

### 📊 통합 대시보드
- **실시간 모니터링**: 테스트 실행 상태 실시간 확인
- **통계 대시보드**: 테스트 결과 통계 및 차트
- **프로젝트 관리**: 다중 프로젝트 지원

## 🏗️ 기술 스택

### Frontend
- **React 19.1.1**: 최신 React 버전
- **Axios**: HTTP 클라이언트
- **CSS3**: 반응형 디자인
- **Error Boundary**: 에러 처리

### Backend
- **Flask 2.3.3**: Python 웹 프레임워크
- **SQLAlchemy 3.0.5**: ORM
- **Neon PostgreSQL**: 클라우드 데이터베이스 (팀 협업용)
- **SQLite**: 로컬 개발용 데이터베이스
- **Flask-CORS**: CORS 설정
- **Flask-Migrate**: 데이터베이스 마이그레이션

### DevOps
- **Vercel**: 프론트엔드/백엔드 호스팅
- **GitHub Actions**: CI/CD 파이프라인
- **Git**: 버전 관리

## 🌐 배포된 URL

### 🎯 메인 애플리케이션
- **프론트엔드**: https://integrated-test-platform-fe-gyeonggong-parks-projects.vercel.app
- **백엔드 API**: https://integrated-test-platform.vercel.app
- **헬스체크**: https://integrated-test-platform.vercel.app/health

### 📁 GitHub 저장소
- **레포지토리**: https://github.com/GeyuongGongPark/integrated-test-platform

## 🚀 빠른 시작

### 1. 로컬 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/GeyuongGongPark/integrated-test-platform.git
cd integrated-test-platform

# 백엔드 설정
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

# 프론트엔드 설정 (새 터미널)
cd frontend
npm install
npm start
```

### 2. 환경 변수 설정

#### 백엔드 (.env)
```env
# 클라우드 데이터베이스 (팀 협업용)
DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
DEV_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
TEST_DATABASE_URL=sqlite:///:memory:

FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here
```

#### 프론트엔드 (.env)
```env
REACT_APP_API_URL=http://localhost:5000
```

### 3. 데이터베이스 초기화

```bash
cd backend
flask db init
flask db migrate
flask db upgrade
```

## 📋 API 엔드포인트

### 테스트 케이스 관리
- `GET /testcases` - 테스트 케이스 목록 조회
- `POST /testcases` - 테스트 케이스 생성
- `GET /testcases/<id>` - 특정 테스트 케이스 조회
- `PUT /testcases/<id>` - 테스트 케이스 수정
- `DELETE /testcases/<id>` - 테스트 케이스 삭제

### 성능 테스트 관리
- `GET /performance-tests` - 성능 테스트 목록 조회
- `POST /performance-tests` - 성능 테스트 생성
- `POST /performance-tests/<id>/execute` - 성능 테스트 실행
- `GET /performance-tests/<id>/results` - 성능 테스트 결과 조회

### 프로젝트 관리
- `GET /projects` - 프로젝트 목록 조회
- `POST /projects` - 프로젝트 생성

### 헬스체크
- `GET /health` - 서버 상태 확인

## 🔧 CI/CD 파이프라인

### GitHub Actions 워크플로우
- **트리거**: main 브랜치 푸시
- **테스트**: 백엔드/프론트엔드 자동 테스트
- **배포**: Vercel 자동 배포

### 자동화된 프로세스
1. **코드 푸시** → GitHub 레포지토리
2. **자동 테스트** → GitHub Actions
3. **자동 배포** → Vercel
4. **실시간 확인** → 배포된 URL

## 🛠️ 개발 가이드

### 프로젝트 구조
```
integrated-test-platform/
├── backend/                 # Flask 백엔드
│   ├── app.py              # 메인 애플리케이션
│   ├── config.py           # 설정 관리
│   ├── requirements.txt    # Python 의존성
│   └── vercel.json        # Vercel 배포 설정
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── App.js         # 메인 앱 컴포넌트
│   │   ├── App.css        # 메인 스타일
│   │   ├── config.js      # API 설정
│   │   └── components/    # 컴포넌트 폴더
│   │       ├── dashboard/     # 📊 대시보드
│   │       │   ├── UnifiedDashboard.js
│   │       │   ├── index.js
│   │       │   └── README.md
│   │       ├── testcases/     # 🧪 테스트 케이스
│   │       │   ├── TestCaseAPP.js
│   │       │   ├── index.js
│   │       │   └── README.md
│   │       ├── performance/   # ⚡ 성능 테스트
│   │       │   ├── PerformanceTestManager.js
│   │       │   ├── index.js
│   │       │   └── README.md
│   │       └── utils/         # 🛠️ 공통 유틸리티
│   │           ├── ErrorBoundary.js
│   │           ├── index.js
│   │           └── README.md
│   ├── package.json       # Node.js 의존성
│   └── vercel.json       # Vercel 배포 설정
├── .github/workflows/     # GitHub Actions
│   └── deploy.yml        # CI/CD 워크플로우
├── docs/                 # 📚 문서
│   ├── README.md         # 문서 목록
│   ├── DEPLOYMENT_SUCCESS.md
│   ├── VERCEL_FRONTEND_DEPLOY.md
│   └── WHITE_SCREEN_FIX.md
└── test-scripts/         # 🧪 성능 테스트 스크립트
    ├── performance/
    ├── clm/
    └── common/
```

### 에러 처리
- **Error Boundary**: React 컴포넌트 에러 캐치
- **CORS 설정**: 프론트엔드-백엔드 통신 허용
- **환경 변수**: 개발/프로덕션 환경 분리

## 📊 모니터링

### Vercel 모니터링
- **Analytics**: 사용자 접속 통계
- **Functions**: 서버리스 함수 로그
- **Performance**: 페이지 로딩 속도

### GitHub 모니터링
- **Actions**: CI/CD 파이프라인 상태
- **Issues**: 버그 리포트 및 기능 요청
- **Pull Requests**: 코드 리뷰 및 병합

## 🔒 보안

### 환경 변수
- **백엔드**: `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV`
- **프론트엔드**: `REACT_APP_API_URL`

### CORS 설정
```python
CORS(app, origins=[
    'http://localhost:3000',
    'https://integrated-test-platform-fe-gyeonggong-parks-projects.vercel.app'
])
```

## 🚀 배포 정보

### 현재 상태
- ✅ **백엔드**: Vercel 배포 성공
- ✅ **프론트엔드**: Vercel 배포 성공
- ✅ **화면**: 정상 동작 확인
- ✅ **CI/CD**: GitHub Actions 자동화 완료

### 배포 환경
- **호스팅**: Vercel (무료 티어)
- **데이터베이스**: SQLite (프로덕션)
- **Node.js**: 18.x
- **Python**: 3.12

## 🤝 기여하기

### 개발 환경 설정
1. 저장소 포크
2. 로컬 환경 설정
3. 기능 개발
4. 테스트 작성
5. Pull Request 생성

### 코드 컨벤션
- **Python**: PEP 8
- **JavaScript**: ESLint
- **커밋 메시지**: Conventional Commits

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

### 문제 해결
- **GitHub Issues**: 버그 리포트
- **Vercel Support**: 배포 관련 문제
- **팀 내부**: 기능 요청 및 개선사항

### 문서
- [배포 성공 가이드](DEPLOYMENT_SUCCESS.md)
- [Vercel 프론트엔드 배포 가이드](VERCEL_FRONTEND_DEPLOY.md)
- [흰 화면 문제 해결 가이드](WHITE_SCREEN_FIX.md)

## 🎉 완료된 기능

### ✅ 구현 완료
- [x] 백엔드 API 개발
- [x] 프론트엔드 UI 개발
- [x] 데이터베이스 설계
- [x] CI/CD 파이프라인 구축
- [x] 클라우드 배포
- [x] 에러 처리
- [x] CORS 설정
- [x] 환경 변수 관리

### 🔄 향후 계획
- [ ] 사용자 인증 시스템
- [ ] 고급 권한 관리
- [ ] PostgreSQL 마이그레이션
- [ ] 실시간 알림 시스템
- [ ] 모바일 앱 개발
- [ ] 고급 분석 기능

---

**🚀 완전한 클라우드 기반 테스트 플랫폼 구축을 성공적으로 완료했습니다!**

무료 호스팅과 자동 배포를 통해 팀 협업에 최적화된 테스트 관리 시스템을 제공합니다.
