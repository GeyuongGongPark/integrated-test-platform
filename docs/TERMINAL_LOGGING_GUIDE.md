# 터미널에서 프론트엔드 로그 확인 가이드

브라우저 개발자 도구 없이 터미널에서 프론트엔드 로그와 네트워크 요청을 확인하는 방법을 안내합니다.

## 📋 목차

1. [개발 서버 터미널 로그](#개발-서버-터미널-로그)
2. [curl로 API 직접 테스트](#curl로-api-직접-테스트)
3. [HTTPie 사용](#httpie-사용)
4. [로그 파일로 저장](#로그-파일로-저장)
5. [axios 인터셉터에 터미널 로깅 추가](#axios-인터셉터에-터미널-로깅-추가)
6. [프록시 도구 사용](#프록시-도구-사용)

## 💻 개발 서버 터미널 로그

### 기본 사용법

```bash
cd frontend
npm start
```

개발 서버를 실행하면 터미널에 다음 정보가 표시됩니다:

- 컴파일 상태
- 빌드 에러 및 경고
- 웹팩 번들링 정보
- Hot Module Replacement (HMR) 상태
- 포트 정보

### 로그 예시

```
Compiled successfully!

You can now view test-case-manager in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.100:3000

Note that the development build is not optimized.
To create a production build, use npm run build.
```

### 에러 확인

빌드 에러가 발생하면 터미널에 상세한 에러 메시지가 표시됩니다:

```
Failed to compile.

./src/components/Test.js
  Line 10:  'undefinedVariable' is not defined

npm ERR! code ELIFECYCLE
```

## 🔧 curl로 API 직접 테스트

### 기본 사용법

```bash
# GET 요청
curl http://localhost:8000/api/testcases

# 헤더 포함 GET 요청
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/testcases

# POST 요청
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"name":"Test Case","status":"Active"}' \
     http://localhost:8000/api/testcases

# 상세 정보 표시 (헤더 포함)
curl -v http://localhost:8000/api/testcases

# 응답 헤더만 확인
curl -I http://localhost:8000/api/testcases
```

### JSON 응답 포맷팅

```bash
# jq 설치 (JSON 포맷터)
brew install jq  # Mac
# 또는
sudo apt-get install jq  # Ubuntu/Debian

# 사용 예시
curl http://localhost:8000/api/testcases | jq

# 특정 필드만 추출
curl http://localhost:8000/api/testcases | jq '.[0].name'
```

### 인증 토큰 사용

```bash
# 토큰 변수에 저장
TOKEN="your-jwt-token-here"

# 토큰 사용
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/testcases
```

### 로그 파일로 저장

```bash
# 요청과 응답을 파일로 저장
curl -v http://localhost:8000/api/testcases > api_response.log 2>&1

# 타임스탬프와 함께 저장
curl -v http://localhost:8000/api/testcases | \
     tee -a "api_$(date +%Y%m%d_%H%M%S).log"
```

## 🚀 HTTPie 사용

HTTPie는 curl보다 사용하기 쉬운 HTTP 클라이언트입니다.

### 설치

```bash
# Mac
brew install httpie

# Ubuntu/Debian
sudo apt-get install httpie

# Python pip
pip install httpie
```

### 기본 사용법

```bash
# GET 요청
http GET http://localhost:8000/api/testcases

# 헤더 포함
http GET http://localhost:8000/api/testcases \
     Authorization:"Bearer YOUR_TOKEN"

# POST 요청
http POST http://localhost:8000/api/testcases \
     name="Test Case" \
     status="Active" \
     Authorization:"Bearer YOUR_TOKEN"

# JSON 파일로 요청
http POST http://localhost:8000/api/testcases \
     < request.json \
     Authorization:"Bearer YOUR_TOKEN"
```

### 세션 사용 (인증 자동화)

```bash
# 세션 생성 (쿠키/헤더 저장)
http --session=./session.json \
     POST http://localhost:8000/api/auth/login \
     username=user password=pass

# 세션 사용
http --session=./session.json \
     GET http://localhost:8000/api/testcases
```

## 📝 로그 파일로 저장

### 개발 서버 로그 저장

```bash
# 로그를 파일로 리다이렉트
npm start > frontend.log 2>&1

# 타임스탬프와 함께 저장
npm start 2>&1 | \
     while IFS= read -r line; do \
       echo "[$(date +'%Y-%m-%d %H:%M:%S')] $line"; \
     done | tee frontend.log
```

### 실시간 로그 확인 (tail 사용)

```bash
# 터미널 1: 로그 파일로 저장
npm start > frontend.log 2>&1

# 터미널 2: 실시간 로그 확인
tail -f frontend.log

# 에러만 필터링
tail -f frontend.log | grep -i error
```

### 로그 필터링

```bash
# 에러만 표시
npm start 2>&1 | grep -i error

# 경고만 표시
npm start 2>&1 | grep -i warning

# 특정 키워드 검색
npm start 2>&1 | grep "API"
```

## 🔍 axios 인터셉터에 터미널 로깅 추가

프론트엔드 코드에 터미널 로깅을 추가할 수 있습니다.

### 방법 1: axios 인터셉터 수정

`frontend/src/utils/apiLogger.js` 파일 생성:

```javascript
import axios from 'axios';

// 요청 인터셉터 - 터미널에 로그 출력
axios.interceptors.request.use(
  (config) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] → ${config.method.toUpperCase()} ${config.url}`);
    
    if (config.data) {
      console.log('Request Data:', JSON.stringify(config.data, null, 2));
    }
    
    if (config.headers.Authorization) {
      console.log('Authorization: Bearer ***');
    }
    
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 터미널에 로그 출력
axios.interceptors.response.use(
  (response) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ← ${response.status} ${response.config.url}`);
    console.log('Response Data:', JSON.stringify(response.data, null, 2));
    return response;
  },
  (error) => {
    const timestamp = new Date().toISOString();
    console.error(`[${timestamp}] ✗ ${error.response?.status || 'NETWORK'} ${error.config?.url}`);
    console.error('Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default axios;
```

### 방법 2: 환경 변수로 제어

```javascript
// 개발 환경에서만 로그 출력
const isDevelopment = process.env.NODE_ENV === 'development';

axios.interceptors.request.use(
  (config) => {
    if (isDevelopment) {
      console.log(`→ ${config.method.toUpperCase()} ${config.url}`);
    }
    return config;
  }
);
```

## 🌐 프록시 도구 사용

### mitmproxy 사용

mitmproxy는 터미널 기반 HTTP 프록시 도구입니다.

```bash
# 설치
pip install mitmproxy

# 실행
mitmproxy -p 8080

# 브라우저에서 프록시 설정: localhost:8080
# 모든 HTTP 요청이 터미널에 표시됨
```

### Charles Proxy (GUI, 터미널 모드 지원)

```bash
# Charles Proxy 설치 후
# 터미널에서 로그 확인 가능
```

## 📊 실용적인 스크립트 예시

### API 테스트 스크립트

`scripts/test-api.sh`:

```bash
#!/bin/bash

API_URL="http://localhost:8000/api"
TOKEN="your-token-here"

echo "=== API 테스트 시작 ==="
echo ""

# 테스트 케이스 목록 조회
echo "1. 테스트 케이스 목록 조회"
curl -s -H "Authorization: Bearer $TOKEN" \
     "$API_URL/testcases" | jq '.[0:3]'  # 처음 3개만 표시
echo ""

# 헬스 체크
echo "2. 헬스 체크"
curl -s "$API_URL/../health" | jq
echo ""

echo "=== 테스트 완료 ==="
```

실행:
```bash
chmod +x scripts/test-api.sh
./scripts/test-api.sh
```

### 로그 모니터링 스크립트

`scripts/monitor-logs.sh`:

```bash
#!/bin/bash

LOG_FILE="frontend.log"

echo "프론트엔드 로그 모니터링 시작..."
echo "로그 파일: $LOG_FILE"
echo ""

# 실시간 로그 확인
tail -f "$LOG_FILE" | \
  while IFS= read -r line; do
    # 에러는 빨간색으로
    if echo "$line" | grep -qi "error"; then
      echo -e "\033[31m$line\033[0m"
    # 경고는 노란색으로
    elif echo "$line" | grep -qi "warning"; then
      echo -e "\033[33m$line\033[0m"
    # 일반 로그
    else
      echo "$line"
    fi
  done
```

## 🔧 환경별 설정

### 개발 환경

```bash
# 상세 로그 활성화
DEBUG=true npm start

# 특정 모듈만 디버그
DEBUG=axios:* npm start
```

### 프로덕션 빌드

```bash
# 빌드 로그 확인
npm run build 2>&1 | tee build.log

# 빌드 에러 확인
npm run build 2>&1 | grep -i error
```

## 📚 유용한 명령어 모음

```bash
# API 응답 시간 측정
time curl http://localhost:8000/api/testcases

# 여러 요청 동시 테스트
for i in {1..10}; do
  curl http://localhost:8000/api/testcases &
done
wait

# 특정 시간 동안 로그 모니터링
timeout 60 tail -f frontend.log

# 로그에서 특정 패턴 찾기
grep -r "API Error" frontend.log

# 로그 통계
grep -c "error" frontend.log
grep -c "warning" frontend.log
```

## 🎯 추천 워크플로우

1. **개발 중**: 개발 서버 터미널에서 실시간 로그 확인
2. **API 테스트**: curl 또는 HTTPie로 직접 테스트
3. **디버깅**: 로그 파일로 저장 후 분석
4. **프로덕션**: 빌드 로그 확인 및 모니터링

## 📞 문제 해결

### 로그가 표시되지 않는 경우

1. **터미널 출력 확인**: `npm start` 실행 중인지 확인
2. **로그 레벨 확인**: 환경 변수 설정 확인
3. **파일 권한**: 로그 파일 쓰기 권한 확인

### API 요청이 실패하는 경우

1. **서버 실행 확인**: 백엔드 서버가 실행 중인지 확인
2. **포트 확인**: API URL이 올바른지 확인
3. **인증 확인**: 토큰이 유효한지 확인

