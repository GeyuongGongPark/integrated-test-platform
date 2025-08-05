# 흰 화면 문제 해결 가이드

## 현재 상황
- ✅ **백엔드**: Vercel 배포 성공
- ✅ **프론트엔드**: Vercel 배포 성공
- ❌ **화면**: 흰 화면만 표시

## 1단계: 브라우저 개발자 도구 확인

### 1.1 콘솔 에러 확인
1. **F12** 또는 **Ctrl+Shift+I**로 개발자 도구 열기
2. **Console** 탭에서 에러 메시지 확인
3. **Network** 탭에서 API 요청 실패 확인

### 1.2 일반적인 에러 유형
- **JavaScript 에러**: React 컴포넌트 로딩 실패
- **API 연결 실패**: 백엔드 서버 연결 문제
- **환경 변수 문제**: `REACT_APP_API_URL` 설정 오류
- **CORS 에러**: 브라우저에서 API 요청 차단

## 2단계: 환경 변수 확인

### 2.1 Vercel 환경 변수 설정
Vercel 대시보드 → Settings → Environment Variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `REACT_APP_API_URL` | `https://integrated-test-platform.vercel.app` | Production |
| `REACT_APP_API_URL` | `http://localhost:8000` | Preview |

### 2.2 환경 변수 확인 방법
```javascript
// 브라우저 콘솔에서 확인
console.log(process.env.REACT_APP_API_URL);
```

## 3단계: API 연결 테스트

### 3.1 백엔드 헬스체크
```bash
# 백엔드 URL로 직접 접속 테스트
curl https://integrated-test-platform.vercel.app/health
```

### 3.2 브라우저에서 API 테스트
```javascript
// 브라우저 콘솔에서 API 테스트
fetch('https://integrated-test-platform.vercel.app/health')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

## 4단계: React 앱 디버깅

### 4.1 간단한 테스트 컴포넌트 생성
```javascript
// App.js를 임시로 단순화
import React from 'react';

function App() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Test Platform</h1>
      <p>API URL: {process.env.REACT_APP_API_URL}</p>
      <p>Environment: {process.env.NODE_ENV}</p>
      <button onClick={() => alert('Button works!')}>
        Test Button
      </button>
    </div>
  );
}

export default App;
```

### 4.2 에러 바운더리 추가
```javascript
// ErrorBoundary.js 생성
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.log('Error:', error);
    console.log('Error Info:', errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

## 5단계: CORS 설정 확인

### 5.1 백엔드 CORS 설정
```python
# backend/app.py에서 CORS 설정 확인
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    'http://localhost:3000',
    'https://integrated-test-platform-fe.vercel.app',
    'https://your-frontend-domain.vercel.app'
])
```

### 5.2 프론트엔드 도메인 허용
백엔드에서 프론트엔드 도메인을 CORS 허용 목록에 추가

## 6단계: 빌드 설정 확인

### 6.1 public/index.html 확인
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Test Platform</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

### 6.2 src/index.js 확인
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

## 7단계: 로컬 테스트

### 7.1 로컬에서 빌드 테스트
```bash
cd frontend
npm run build
npx serve -s build
```

### 7.2 로컬에서 환경 변수 테스트
```bash
# .env 파일 생성
echo "REACT_APP_API_URL=http://localhost:8000" > .env
npm start
```

## 8단계: Vercel 재배포

### 8.1 강제 재배포
1. Vercel 대시보드에서 **Redeploy** 클릭
2. **Clear Cache and Deploy** 선택
3. 배포 완료 후 다시 확인

### 8.2 GitHub 푸시로 재배포
```bash
# 작은 변경사항 추가
echo "// 흰 화면 디버깅" >> frontend/src/App.js
git add .
git commit -m "흰 화면 문제 디버깅"
git push
```

## 9단계: 문제별 해결 방법

### 9.1 JavaScript 에러
- **콘솔 에러 확인**: 구체적인 에러 메시지 파악
- **컴포넌트 단순화**: 복잡한 컴포넌트를 단순한 것으로 교체
- **에러 바운더리**: React 에러 바운더리 추가

### 9.2 API 연결 실패
- **환경 변수**: `REACT_APP_API_URL` 올바른 값 설정
- **CORS 설정**: 백엔드에서 프론트엔드 도메인 허용
- **네트워크**: 브라우저 네트워크 탭에서 요청 확인

### 9.3 빌드 문제
- **캐시 클리어**: Vercel에서 캐시 클리어 후 재배포
- **의존성**: `npm ci`로 의존성 재설치
- **Node.js 버전**: 18.x 사용 확인

## 10단계: 성공 확인

### 10.1 정상 작동 체크
- ✅ **React 앱 로딩**: 메인 페이지 표시
- ✅ **API 연결**: 백엔드와 통신 성공
- ✅ **기능 테스트**: 모든 기능 정상 작동
- ✅ **반응형**: 모바일/데스크톱 확인

### 10.2 최종 확인
```bash
# 프론트엔드 URL 접속
https://integrated-test-platform-fe.vercel.app

# 백엔드 헬스체크
https://integrated-test-platform.vercel.app/health
```

## 완료 체크리스트

- [ ] 브라우저 개발자 도구 확인
- [ ] 환경 변수 설정
- [ ] API 연결 테스트
- [ ] React 앱 디버깅
- [ ] CORS 설정 확인
- [ ] 빌드 설정 확인
- [ ] 로컬 테스트
- [ ] Vercel 재배포
- [ ] 성공 확인

## 다음 단계

1. **문제 해결**: 흰 화면 문제 완전 해결
2. **기능 테스트**: 모든 기능 정상 작동 확인
3. **팀 공유**: 완전한 플랫폼 URL 공유
4. **모니터링**: Vercel Analytics 설정 