# 🎨 프론트엔드 배포 가이드

## ✅ 현재 상태
- ✅ React 앱 정상 작동
- ✅ 백엔드 API 연결 설정 완료
- ✅ 환경별 설정 파일 준비 완료

## 📋 프론트엔드 배포 단계

### 1단계: 환경 설정 확인

#### config.js 확인:
```javascript
const config = {
  development: {
    apiUrl: 'http://localhost:8000'
  },
  production: {
    apiUrl: 'https://your-backend-domain.com'  // 배포된 백엔드 URL
  }
};

export default config[process.env.NODE_ENV || 'development'];
```

### 2단계: 빌드 테스트

```bash
# 의존성 설치
npm install

# 개발 서버 테스트
npm start

# 프로덕션 빌드
npm run build
```

### 3단계: 배포 플랫폼별 설정

#### Vercel 배포:
```bash
# 1. Vercel CLI 설치
npm i -g vercel

# 2. 프로젝트 배포
vercel --prod
```

#### Netlify 배포:
```bash
# 1. Netlify CLI 설치
npm i -g netlify-cli

# 2. 로그인
netlify login

# 3. 배포
netlify deploy --prod
```

#### GitHub Pages 배포:
```bash
# 1. package.json에 homepage 추가
"homepage": "https://your-username.github.io/your-repo-name"

# 2. gh-pages 설치
npm install --save-dev gh-pages

# 3. package.json에 스크립트 추가
"predeploy": "npm run build",
"deploy": "gh-pages -d build"

# 4. 배포
npm run deploy
```

### 4단계: 환경변수 설정

#### Vercel 환경변수:
```
REACT_APP_API_URL=https://your-backend-domain.com
```

#### Netlify 환경변수:
```
REACT_APP_API_URL=https://your-backend-domain.com
```

### 5단계: 배포 후 확인

#### 브라우저에서 확인:
1. 배포된 URL 접속
2. 개발자 도구 열기 (F12)
3. Network 탭에서 API 호출 확인
4. Console 탭에서 오류 확인

#### API 연결 테스트:
```javascript
// 브라우저 콘솔에서 실행
fetch('https://your-backend-domain.com/health')
  .then(response => response.json())
  .then(data => console.log(data));
```

## 🔧 문제 해결

### 1. API 연결 오류 (401, CORS)
- 백엔드 CORS 설정 확인
- API URL이 올바른지 확인
- 환경변수 설정 확인

### 2. 빌드 오류
- Node.js 버전 확인 (14+ 권장)
- 의존성 재설치: `rm -rf node_modules && npm install`
- 캐시 클리어: `npm run build -- --reset-cache`

### 3. 배포 후 화면이 안 보임
- 빌드 파일 확인
- 라우팅 설정 확인
- 404 페이지 설정

## 📱 반응형 디자인 확인

### 모바일 테스트:
- Chrome DevTools > Toggle device toolbar
- 다양한 화면 크기 테스트
- 터치 인터페이스 확인

### 브라우저 호환성:
- Chrome, Firefox, Safari, Edge 테스트
- 최신 버전에서 정상 작동 확인

## 🎯 성공 기준

### ✅ 완료 체크리스트:
- [ ] 프론트엔드 배포 완료
- [ ] 백엔드 API 연결 정상
- [ ] 데이터 로딩 확인
- [ ] 반응형 디자인 확인
- [ ] 브라우저 호환성 확인
- [ ] 성능 최적화 확인

## 🚀 최종 확인

배포 완료 후 다음을 확인하세요:

1. **기본 기능:**
   - 페이지 로딩
   - 네비게이션
   - 데이터 표시

2. **API 연결:**
   - 프로젝트 목록
   - 성능 테스트 목록
   - 테스트 실행 결과

3. **사용자 경험:**
   - 로딩 상태
   - 오류 처리
   - 반응형 디자인

## 📞 지원

문제 발생 시:
1. 브라우저 개발자 도구 확인
2. 배포 플랫폼 로그 확인
3. 백엔드 API 상태 확인
4. 환경변수 설정 재확인 