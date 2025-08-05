# Integrated Test Platform 통합 계획서

## 🎯 통합 목표

### 기존 프로젝트 분석
- **TCM**: 테스트 케이스 관리 시스템 (Flask + React + SQLite)
- **LFBZ_performance**: 웹 성능 테스트 자동화 (k6 + Playwright + Python GUI)

### 통합 후 시스템
- **통합된 테스트 관리 플랫폼**: 테스트 케이스 관리 + 성능 테스트 자동화
- **단일 웹 인터페이스**: 모든 테스트 활동을 웹에서 관리
- **통합 데이터베이스**: 테스트 케이스와 성능 테스트 결과 통합 저장

## ✅ 통합 완료 상태

### Phase 1: 데이터베이스 확장 ✅
- [x] PerformanceTests 테이블 추가
- [x] PerformanceTestResults 테이블 추가
- [x] TestExecutions 테이블 추가
- [x] Projects 테이블 추가
- [x] Folders 테이블 추가
- [x] 데이터베이스 스키마 확장 완료

### Phase 2: Backend API 확장 ✅
- [x] 성능 테스트 관련 API 엔드포인트 구현
- [x] k6 실행 엔진 구현
- [x] 테스트 실행 API 구현
- [x] 프로젝트 관리 API 구현
- [x] 폴더 관리 API 구현
- [x] 통합 데이터베이스 연결 (Neon PostgreSQL)

### Phase 3: Frontend 확장 ✅
- [x] 통합 네비게이션 구현
- [x] 성능 테스트 관리 컴포넌트 구현
- [x] 통합 대시보드 구현
- [x] 설정 관리 컴포넌트 구현
- [x] 자동화 테스트 컴포넌트 구현
- [x] 기존 TCM UI와 통합

### Phase 4: LFBZ_performance 통합 ✅
- [x] k6 스크립트들을 새로운 시스템에 통합
- [x] 환경 설정 관리 기능 구현
- [x] 테스트 결과 리포트 생성 기능

## 🏗️ 통합 아키텍처

```
Integrated Test Platform
├── Frontend (React)
│   ├── Dashboard (통합 대시보드)
│   ├── Test Case Management (기존 TCM)
│   ├── Performance Test Management (새로 추가)
│   ├── Settings Management (새로 추가)
│   ├── Automation Management (새로 추가)
│   └── Folder Management (새로 추가)
├── Backend (Flask)
│   ├── Test Case APIs (기존)
│   ├── Performance Test APIs (새로 추가)
│   ├── Project Management APIs (새로 추가)
│   ├── Folder Management APIs (새로 추가)
│   ├── Test Execution Engine (새로 추가)
│   └── Unified Database (Neon PostgreSQL)
├── Test Execution Layer
│   ├── k6 Performance Tests (LFBZ_performance)
│   ├── Playwright UI Tests (새로 추가)
│   └── Test Orchestration
└── Data Storage
    ├── Neon PostgreSQL Database (프로덕션)
    ├── SQLite Database (개발용)
    └── Test Results & Reports
```

## 🚀 실행 방법

### 1. 백엔드 실행
```bash
cd integrated-test-platform/backend
pip install -r requirements.txt
python app.py
```

### 2. 프론트엔드 실행
```bash
cd integrated-test-platform/frontend
npm install
npm start
```

### 3. 환경 변수 설정
```bash
# 백엔드 .env
DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
DEV_DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
TEST_DATABASE_URL=sqlite:///:memory:

# 프론트엔드 .env
REACT_APP_API_URL=http://localhost:8000
```

## 📋 사용법

### 1. 테스트 케이스 관리
- **프로젝트 생성**: 새로운 프로젝트를 생성하여 테스트 케이스를 그룹화
- **테스트 케이스 추가**: 프로젝트별로 테스트 케이스를 생성하고 관리
- **폴더 관리**: 테스트 케이스를 폴더별로 체계적 관리
- **테스트 실행**: UI 테스트를 실행하고 결과를 기록
- **결과 관리**: 테스트 결과와 스크린샷을 저장하고 관리

### 2. 성능 테스트 관리
- **성능 테스트 등록**: k6 스크립트를 시스템에 등록
- **환경 설정**: 테스트 환경 변수 설정
- **테스트 실행**: 성능 테스트를 실행하고 결과 수집
- **결과 분석**: 응답 시간, 처리량, 오류율 등 성능 지표 분석

### 3. 통합 대시보드
- **전체 현황**: 모든 테스트의 실행 상태와 결과 요약
- **프로젝트별 통계**: 프로젝트별 테스트 진행 상황
- **성능 트렌드**: 성능 테스트 결과의 시간별 변화 추이
- **실시간 모니터링**: 테스트 실행 상태 실시간 확인

### 4. 설정 관리
- **계정 관리**: 사용자 계정 정보 관리
- **프로젝트 설정**: 프로젝트별 설정 관리
- **폴더 구조**: 테스트 케이스 폴더 구조 관리

## 🔧 기술 구현

### 1. 데이터베이스 스키마
```python
# 성능 테스트 관련 테이블
class PerformanceTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    script_path = db.Column(db.String(200), nullable=False)
    environment_vars = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PerformanceTestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('performance_test.id'))
    execution_time = db.Column(db.Float)
    response_time = db.Column(db.Float)
    throughput = db.Column(db.Float)
    error_rate = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 2. k6 실행 엔진
```python
# k6 실행 엔진
class K6ExecutionEngine:
    def __init__(self, k6_script_dir="test-scripts/performance/clm/nomerl"):
        self.k6_script_dir = k6_script_dir
    
    def execute_test(self, script_name, environment_vars):
        """k6 성능 테스트 실행"""
        script_path = os.path.join(self.k6_script_dir, script_name)
        env_vars = " ".join([f"-e {k}={v}" for k, v in environment_vars.items()])
        
        cmd = f"k6 run {env_vars} {script_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        return self.parse_k6_output(result.stdout)
```

### 3. 웹 인터페이스 통합
```javascript
// frontend/src/App.js
function App() {
  const [currentView, setCurrentView] = useState('dashboard');

  const renderContent = () => {
    switch (currentView) {
      case 'test-cases':
        return <TestCaseApp />;
      case 'performance-tests':
        return <PerformanceTestManager />;
      case 'settings':
        return <Settings />;
      case 'automation':
        return <AutomationTestManager />;
      case 'dashboard':
      default:
        return <UnifiedDashboard />;
    }
  };

  return (
    <div className="App">
      <nav className="navbar">
        <div className="nav-brand">
          <h1>통합 테스트 관리 플랫폼</h1>
        </div>
        <div className="nav-links">
          <button onClick={() => setCurrentView('dashboard')}>대시보드</button>
          <button onClick={() => setCurrentView('test-cases')}>테스트 케이스</button>
          <button onClick={() => setCurrentView('performance-tests')}>성능 테스트</button>
          <button onClick={() => setCurrentView('automation')}>자동화</button>
          <button onClick={() => setCurrentView('settings')}>설정</button>
        </div>
      </nav>
      <main className="main-content">
        {renderContent()}
      </main>
    </div>
  );
}
```

## 🎯 통합 완료 상태

### ✅ 완료된 작업
1. **데이터베이스 스키마 확장**: 성능 테스트 관련 테이블 추가
2. **Backend API 확장**: 성능 테스트 관리 API 구현
3. **Frontend 통합**: 단일 웹 인터페이스로 통합
4. **k6 스크립트 통합**: 기존 LFBZ_performance 스크립트 통합
5. **실행 환경 설정**: 자동 실행 스크립트 업데이트
6. **클라우드 배포**: Vercel + Neon PostgreSQL
7. **CI/CD 파이프라인**: GitHub Actions 자동화

### 🔄 현재 실행 중인 서비스
- **Backend**: http://localhost:8000 (Flask API)
- **Frontend**: http://localhost:3000 (React UI)
- **Database**: Neon PostgreSQL (프로덕션), SQLite (개발용)

### 📊 통합 결과
- **단일 플랫폼**: 테스트 케이스와 성능 테스트를 하나의 인터페이스에서 관리
- **통합 데이터베이스**: 모든 테스트 데이터를 하나의 데이터베이스에서 관리
- **향상된 사용자 경험**: 직관적인 네비게이션과 통합된 대시보드
- **클라우드 기반**: 무료 호스팅과 자동 배포

## 🚀 다음 단계

### 향후 개선 사항
1. **사용자 인증 시스템**: 로그인/회원가입 기능
2. **고급 권한 관리**: 역할 기반 접근 제어
3. **실시간 알림**: 테스트 완료/실패 알림
4. **API 문서 자동 생성**: 테스트 결과 기반 문서 생성
5. **모바일 앱**: 모바일 환경 지원

### 확장 가능한 기능
1. **다양한 테스트 도구 지원**: Selenium, Cypress 등
2. **클라우드 테스트 환경**: AWS, Azure 등 클라우드 환경 지원
3. **모바일 테스트**: Appium 등 모바일 테스트 도구 통합
4. **API 테스트**: Postman, Newman 등 API 테스트 도구 통합

## 📝 결론

TCM과 LFBZ_performance의 통합이 성공적으로 완료되었습니다. 이제 하나의 통합된 플랫폼에서 테스트 케이스 관리와 성능 테스트를 모두 수행할 수 있습니다. 

**주요 성과:**
- ✅ 단일 웹 인터페이스로 모든 테스트 활동 관리
- ✅ 통합된 데이터베이스로 테스트 이력 추적
- ✅ k6 성능 테스트 자동화 통합
- ✅ 향상된 사용자 경험과 직관적인 네비게이션
- ✅ 클라우드 기반 무료 호스팅
- ✅ 자동 CI/CD 파이프라인

이 통합된 시스템은 향후 다양한 테스트 도구와 환경을 추가로 통합할 수 있는 확장 가능한 아키텍처를 제공합니다. 