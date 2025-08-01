# Vercel CLI 빠른 배포 가이드

## 1단계: Vercel CLI 설치

```bash
# npm으로 Vercel CLI 설치
npm install -g vercel

# 또는 yarn으로 설치
yarn global add vercel
```

## 2단계: Vercel 로그인

```bash
# Vercel 계정으로 로그인
vercel login
```

## 3단계: 프론트엔드 배포

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# Vercel 배포 시작
vercel
```

### 배포 설정 옵션:
- **Set up and deploy**: `Y`
- **Which scope**: `(선택)`
- **Link to existing project**: `N`
- **Project name**: `test-platform-frontend`
- **In which directory is your code located**: `./`
- **Want to override the settings**: `N`

## 4단계: 환경 변수 설정

```bash
# 백엔드 URL 환경 변수 추가
vercel env add REACT_APP_API_URL

# Production 환경
Value: https://your-backend-domain.vercel.app

# Preview 환경
Value: http://localhost:5000
```

## 5단계: 배포 확인

```bash
# 배포 상태 확인
vercel ls

# 최근 배포 확인
vercel ls --limit=5
```

## 6단계: 자동 배포 설정

```bash
# 프로덕션 배포
vercel --prod

# 특정 브랜치에서만 배포
vercel --prod --target=production
```

## 7단계: 도메인 확인

```bash
# 도메인 정보 확인
vercel domains ls

# 커스텀 도메인 추가 (선택사항)
vercel domains add your-domain.com
```

## 8단계: 로그 확인

```bash
# 배포 로그 확인
vercel logs

# 실시간 로그 확인
vercel logs --follow
```

## 9단계: 설정 파일 생성 (선택사항)

### vercel.json 생성
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

## 10단계: 문제 해결

### 빌드 실패 시
```bash
# 로컬 빌드 테스트
npm run build

# 의존성 재설치
rm -rf node_modules package-lock.json
npm install
```

### 환경 변수 문제 시
```bash
# 환경 변수 확인
vercel env ls

# 환경 변수 삭제 후 재설정
vercel env rm REACT_APP_API_URL
vercel env add REACT_APP_API_URL
```

## 완료 체크리스트

- [ ] Vercel CLI 설치
- [ ] Vercel 로그인
- [ ] 프론트엔드 배포
- [ ] 환경 변수 설정
- [ ] 배포 확인
- [ ] 자동 배포 설정
- [ ] 도메인 확인
- [ ] 기능 테스트

## 다음 단계

1. **백엔드 배포**: 동일한 방법으로 백엔드 배포
2. **통합 테스트**: 전체 플랫폼 테스트
3. **팀 공유**: URL 공유
4. **모니터링**: Vercel Analytics 설정 