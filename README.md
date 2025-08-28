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

## 🏗️ 기술 스택

### Backend
- **Python 3.13+**
- **Flask 2.3+**
- **SQLAlchemy 2.0+**
- **MySQL 8.0+**
- **Docker**
- **pytz**: KST 시간대 처리

### Frontend
- **React 18+**
- **Axios**
- **Chart.js**

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

# 또는 docs/mysql-init/ 스크립트 실행
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
│   ├── postman_collection_v2.json
│   ├── postman_environment_v2.json
│   ├── PERMISSION_GUIDE.md # 권한별 기능 가이드
│   ├── API_TESTING_GUIDE.md # API 테스트 가이드
│   ├── TESTING_GUIDE.md    # 테스트 가이드
│   └── PROJECT_STRUCTURE.md # 프로젝트 구조
├── test-scripts/            # 테스트 스크립트
│   ├── performance/        # K6 성능 테스트
│   └── playwright/         # Playwright 자동화 테스트
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

- **API 가이드**: `docs/API_TESTING_GUIDE.md`
- **Postman 사용법**: `docs/POSTMAN_USAGE_GUIDE.md`
- **프로젝트 구조**: `docs/PROJECT_STRUCTURE.md`
- **배포 요약**: `docs/DEPLOYMENT_SUMMARY.md`
- **테스트 가이드**: `docs/TESTING_GUIDE.md`
- **권한 가이드**: `docs/PERMISSION_GUIDE.md`

## 🧪 테스트

### API 테스트
```bash
# Postman Collection 사용
docs/postman_collection_v2.json
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


## 📞 연락처

- 프로젝트 링크: [https://github.com/username/integrated-test-platform](https://github.com/username/integrated-test-platform)
- E-Mail : [bakgg93@gmail.com](bakgg93@gmail.com)
- H.P : 010-8496-1463

---

**마지막 업데이트**: 2025년 8월 27일  
**버전**: 2.1.0  
**상태**: 프로덕션 배포 완료 ✅  
**주요 업데이트**: KST 시간대 처리, 파일 정리, 문서 최신화
