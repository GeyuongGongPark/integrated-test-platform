# 프론트엔드 로그 확인 가이드

이 가이드는 프론트엔드 애플리케이션의 로그를 확인하는 방법을 안내합니다.

## 📋 목차

1. [브라우저 개발자 도구](#브라우저-개발자-도구)
2. [콘솔 로그 확인](#콘솔-로그-확인)
3. [네트워크 요청 확인](#네트워크-요청-확인)
4. [React DevTools](#react-devtools)
5. [프로덕션 환경 로그](#프로덕션-환경-로그)
6. [로컬 개발 환경 로그](#로컬-개발-환경-로그)
7. [에러 추적](#에러-추적)

## 🛠️ 브라우저 개발자 도구

### Chrome/Edge (Windows/Linux)
- **단축키**: `F12` 또는 `Ctrl + Shift + I`
- **또는**: `Ctrl + Shift + J` (콘솔만 열기)

### Chrome/Edge (Mac)
- **단축키**: `Cmd + Option + I`
- **또는**: `Cmd + Option + J` (콘솔만 열기)

### Firefox
- **단축키**: `F12` 또는 `Ctrl + Shift + I` (Windows/Linux)
- **단축키**: `Cmd + Option + I` (Mac)

### Safari
- **설정**: Safari > 환경설정 > 고급 > "메뉴 막대에서 개발자용 메뉴 보기" 체크
- **단축키**: `Cmd + Option + C`

## 📝 콘솔 로그 확인

### 1. 콘솔 탭 열기

개발자 도구를 연 후 **Console** 탭을 클릭합니다.

### 2. 로그 레벨별 확인

콘솔에서 로그 레벨별로 필터링할 수 있습니다:

- **All**: 모든 로그
- **Errors**: 에러만 (`console.error`)
- **Warnings**: 경고만 (`console.warn`)
- **Info**: 정보 (`console.info`)
- **Verbose**: 상세 로그 (`console.debug`)

### 3. 로그 검색

콘솔 상단의 필터 입력란에 키워드를 입력하여 특정 로그를 검색할 수 있습니다.

예시:
- `API` - API 관련 로그만 표시
- `Error` - 에러 관련 로그만 표시
- `Auth` - 인증 관련 로그만 표시

### 4. 로그 저장

콘솔에서 우클릭 > **Save as...** 를 선택하여 로그를 파일로 저장할 수 있습니다.

## 🌐 네트워크 요청 확인

### 1. Network 탭 열기

개발자 도구에서 **Network** 탭을 클릭합니다.

### 2. 요청 필터링

- **All**: 모든 요청
- **XHR/Fetch**: API 요청만
- **JS**: JavaScript 파일
- **CSS**: 스타일시트
- **Img**: 이미지

### 3. 요청 상세 확인

요청을 클릭하면 다음 정보를 확인할 수 있습니다:

- **Headers**: 요청/응답 헤더
- **Payload**: 요청 데이터
- **Response**: 응답 데이터
- **Timing**: 요청 시간 정보

### 4. API 요청 모니터링

1. Network 탭 열기
2. 필터에서 "XHR" 또는 "Fetch" 선택
3. 페이지에서 작업 수행
4. 요청 목록에서 API 호출 확인
5. 요청 클릭하여 상세 정보 확인

**주요 확인 사항:**
- 요청 URL이 올바른지
- 요청 헤더에 `Authorization` 토큰이 포함되어 있는지
- 응답 상태 코드 (200, 401, 500 등)
- 응답 데이터 형식

## ⚛️ React DevTools

### 설치

1. Chrome/Edge: [React Developer Tools 확장 프로그램](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
2. Firefox: [React Developer Tools 확장 프로그램](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)

### 사용 방법

1. 확장 프로그램 설치 후 개발자 도구 열기
2. **Components** 탭에서 React 컴포넌트 트리 확인
3. 컴포넌트 선택하여 props, state 확인
4. **Profiler** 탭에서 성능 분석

## 🚀 프로덕션 환경 로그

### Vercel 배포 환경

#### 1. Vercel 대시보드에서 확인

1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. 프로젝트 선택
3. **Deployments** 탭에서 배포 선택
4. **Functions** 탭에서 함수 로그 확인
5. **Runtime Logs** 탭에서 실시간 로그 확인

#### 2. 브라우저 콘솔 확인

프로덕션 환경에서도 브라우저 개발자 도구 콘솔을 열어 클라이언트 측 로그를 확인할 수 있습니다.

⚠️ **주의**: 프로덕션 빌드에서는 `console.log`가 최소화되거나 제거될 수 있습니다.

### 로그 레벨 설정

프로덕션 환경에서는 다음 로그만 표시됩니다:
- `console.error()` - 에러
- `console.warn()` - 경고

개발 환경에서만 표시되는 로그:
- `console.log()` - 일반 로그
- `console.debug()` - 디버그 로그

## 💻 로컬 개발 환경 로그

### 1. 개발 서버 실행

```bash
cd frontend
npm start
```

### 2. 터미널 로그 확인

개발 서버를 실행한 터미널에서 다음 정보를 확인할 수 있습니다:

- 컴파일 상태
- 빌드 에러
- 웹팩 경고
- Hot Module Replacement (HMR) 상태

### 3. 브라우저 콘솔 확인

개발 서버 실행 후 브라우저를 열고 개발자 도구 콘솔을 확인합니다.

### 4. 소스맵 확인

개발 환경에서는 소스맵이 활성화되어 있어 원본 파일 위치를 확인할 수 있습니다:

1. 콘솔에서 에러 클릭
2. **Sources** 탭에서 원본 파일 확인
3. 브레이크포인트 설정 가능

## 🐛 에러 추적

### 1. ErrorBoundary

애플리케이션에는 `ErrorBoundary` 컴포넌트가 있어 React 에러를 캐치합니다:

- 개발 환경: 에러 상세 정보 표시
- 프로덕션 환경: 사용자 친화적 에러 메시지 표시

### 2. 콘솔 에러 확인

콘솔에서 빨간색으로 표시되는 에러를 확인합니다:

```
❌ Error: ...
   at ComponentName (file.js:123:45)
   ...
```

### 3. 네트워크 에러 확인

Network 탭에서 빨간색으로 표시되는 실패한 요청을 확인합니다:

- **4xx**: 클라이언트 오류 (401 Unauthorized, 404 Not Found 등)
- **5xx**: 서버 오류 (500 Internal Server Error 등)

### 4. 스택 트레이스 분석

에러 메시지의 스택 트레이스를 확인하여 문제가 발생한 위치를 파악합니다:

```
Error: Cannot read property 'name' of undefined
    at TestCaseAPP.render (TestCaseAPP.js:234:15)
    at ReactDOM.render (react-dom.development.js:12345:5)
```

## 📊 주요 로그 확인 포인트

### 인증 관련

```javascript
// AuthContext.js에서 확인 가능한 로그
🎉 인증 성공 처리 시작
🎉 인증 성공 처리 완료
```

### API 요청

```javascript
// axios 인터셉터에서 확인 가능
Request: GET /api/testcases
Response: 200 OK
Error: 401 Unauthorized
```

### 컴포넌트 렌더링

```javascript
// 개발 환경에서만 표시
[App] Render Jira tab with modalMode=true
```

## 🔍 로그 필터링 팁

### 1. 특정 키워드로 필터링

콘솔 필터에 다음 키워드를 입력:
- `API` - API 관련 로그
- `Auth` - 인증 관련 로그
- `Error` - 에러만 표시
- `Warning` - 경고만 표시

### 2. 정규식 사용

콘솔 필터에서 정규식을 사용할 수 있습니다:
- `/API|Auth/` - API 또는 Auth 관련 로그
- `/Error|Warning/` - 에러 또는 경고

### 3. 로그 그룹화

코드에서 `console.group()` 사용:
```javascript
console.group('API Request');
console.log('URL:', url);
console.log('Method:', method);
console.groupEnd();
```

## 📱 모바일 디버깅

### Chrome DevTools 원격 디버깅

1. Android 기기에서 Chrome 실행
2. USB 디버깅 활성화
3. Chrome에서 `chrome://inspect` 접속
4. 기기 선택하여 디버깅

### iOS Safari 디버깅

1. Mac에서 Safari 실행
2. 개발자 > [기기명] > [웹페이지] 선택
3. 개발자 도구 열기

## 🛡️ 보안 주의사항

### 프로덕션 환경

⚠️ **중요**: 프로덕션 환경에서는 다음 정보를 로그에 출력하지 마세요:

- 사용자 비밀번호
- 인증 토큰 (전체)
- 개인정보
- API 키
- 데이터베이스 연결 정보

### 로그 정리

프로덕션 빌드 전에 불필요한 `console.log` 제거:

```bash
# 빌드 시 자동으로 제거됨 (react-scripts)
npm run build
```

## 📚 유용한 도구

### 1. React DevTools
- 컴포넌트 트리 시각화
- Props/State 확인
- 성능 프로파일링

### 2. Redux DevTools (사용 시)
- 상태 관리 디버깅
- 액션 히스토리 확인

### 3. Lighthouse
- 성능 분석
- 접근성 검사
- SEO 분석

## 🔧 문제 해결

### 로그가 표시되지 않는 경우

1. **콘솔 필터 확인**: 필터가 활성화되어 있는지 확인
2. **로그 레벨 확인**: `console.log`가 필터링되었는지 확인
3. **브라우저 캐시**: 하드 리프레시 (`Ctrl+Shift+R` 또는 `Cmd+Shift+R`)
4. **개발 서버 재시작**: 로컬 개발 환경인 경우 서버 재시작

### 네트워크 요청이 보이지 않는 경우

1. **필터 확인**: Network 탭의 필터 설정 확인
2. **Preserve log**: 페이지 이동 시 로그 유지 옵션 활성화
3. **캐시 비활성화**: "Disable cache" 옵션 활성화

## 📞 추가 도움말

문제가 계속되면 다음을 확인하세요:

1. 브라우저 콘솔의 에러 메시지
2. Network 탭의 실패한 요청
3. Vercel 대시보드의 배포 로그
4. GitHub Issues 또는 팀 채널

