# 프론트엔드 배포 실패 해결 가이드

## 현재 상황
- ✅ **백엔드**: Vercel 배포 성공
- ❌ **프론트엔드**: Vercel 배포 실패 (`integrated-test-platform-fe`)

## 1단계: Vercel 로그 확인

### 1.1 Vercel 대시보드에서 로그 확인
1. https://vercel.com/dashboard 접속
2. `integrated-test-platform-fe` 프로젝트 클릭
3. **Functions** 탭 → **Logs** 확인
4. **Build Logs**에서 에러 메시지 확인

### 1.2 일반적인 에러 유형
- **Build Error**: 빌드 과정에서 실패
- **Dependency Error**: 의존성 설치 실패
- **Environment Error**: 환경 변수 문제
- **Node.js Version**: Node.js 버전 호환성 문제

## 2단계: 로컬 빌드 테스트

### 2.1 로컬에서 빌드 테스트
```bash
cd frontend
npm install
npm run build
```

### 2.2 빌드 성공 확인
- `build/` 폴더가 생성되는지 확인
- 에러 메시지가 없는지 확인

## 3단계: Vercel 설정 수정

### 3.1 프로젝트 설정 확인
Vercel 대시보드에서:
- **Framework Preset**: `Create React App`
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `build`
- **Install Command**: `npm install`

### 3.2 Node.js 버전 설정
```json
// package.json에 추가
{
  "engines": {
    "node": "18.x"
  }
}
```

## 4단계: 환경 변수 설정

### 4.1 백엔드 URL 설정
Vercel 대시보드 → Settings → Environment Variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `REACT_APP_API_URL` | `https://integrated-test-platform.vercel.app` | Production |
| `REACT_APP_API_URL` | `http://localhost:8000` | Preview |

## 5단계: vercel.json 설정

### 5.1 frontend/vercel.json 생성
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

## 6단계: package.json 확인

### 6.1 필수 스크립트 확인
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

### 6.2 의존성 확인
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "react-scripts": "5.0.1"
  }
}
```

## 7단계: 재배포

### 7.1 수동 재배포
1. Vercel 대시보드에서 **Redeploy** 클릭
2. 배포 진행 상황 모니터링
3. 로그에서 에러 확인

### 7.2 GitHub 푸시로 재배포
```bash
# 작은 변경사항 추가
echo "// 배포 테스트" >> frontend/src/App.js
git add .
git commit -m "프론트엔드 배포 테스트"
git push
```

## 8단계: 문제별 해결 방법

### 8.1 빌드 실패
- **Node.js 버전**: 18.x 사용
- **의존성 문제**: `npm ci` 사용
- **메모리 부족**: 빌드 메모리 증가

### 8.2 환경 변수 문제
- **REACT_APP_ 접두사**: 필수
- **Production/Preview**: 환경별 설정
- **문자열 값**: 따옴표 없이 입력

### 8.3 CORS 문제
- **백엔드 CORS 설정**: 프론트엔드 도메인 허용
- **환경 변수**: 올바른 백엔드 URL 설정

## 9단계: 성공 확인

### 9.1 배포 성공 체크
- ✅ **Vercel 대시보드**: 초록색 체크마크
- ✅ **도메인 접속**: React 앱 로딩
- ✅ **API 연결**: 백엔드와 통신
- ✅ **기능 테스트**: 모든 기능 정상 작동

### 9.2 최종 확인
```bash
# 프론트엔드 URL 접속 테스트
curl https://integrated-test-platform-fe.vercel.app

# 브라우저에서 확인
https://integrated-test-platform-fe.vercel.app
```

## 완료 체크리스트

- [ ] Vercel 로그 확인
- [ ] 로컬 빌드 테스트
- [ ] Vercel 설정 수정
- [ ] 환경 변수 설정
- [ ] vercel.json 생성
- [ ] package.json 확인
- [ ] 재배포 실행
- [ ] 성공 확인

## 다음 단계

1. **배포 성공**: 프론트엔드 배포 완료
2. **통합 테스트**: 전체 플랫폼 테스트
3. **팀 공유**: URL 공유
4. **모니터링**: Vercel Analytics 설정 