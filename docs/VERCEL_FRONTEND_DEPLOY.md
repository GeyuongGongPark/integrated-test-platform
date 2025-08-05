# Vercel 프론트엔드 배포 가이드

## 1단계: Vercel 계정 설정

### 1.1 Vercel 접속 및 로그인
1. https://vercel.com 접속
2. **Sign Up** 또는 **Log In** 클릭
3. **Continue with GitHub** 선택
4. GitHub 계정으로 로그인

### 1.2 GitHub 레포지토리 연결
1. Vercel 대시보드에서 **New Project** 클릭
2. **Import Git Repository** 섹션에서 GitHub 레포지토리 찾기
3. `GeyuongGongPark/integrated-test-platform` 선택

## 2단계: 프론트엔드 프로젝트 설정

### 2.1 프로젝트 설정
- **Framework Preset**: `Create React App` 선택
- **Root Directory**: `frontend` 입력
- **Build Command**: `npm run build` (자동 설정됨)
- **Output Directory**: `build` (자동 설정됨)
- **Install Command**: `npm install` (자동 설정됨)

### 2.2 고급 설정 (선택사항)
- **Override**: 체크하지 않음 (기본값 사용)
- **Environment Variables**: 나중에 설정

## 3단계: 프로젝트 생성 및 배포

### 3.1 프로젝트 생성
1. **Deploy** 버튼 클릭
2. 배포 진행 상황 확인
3. 배포 완료 후 도메인 URL 확인

### 3.2 배포 확인
- **성공**: 초록색 체크마크와 함께 "Ready" 표시
- **실패**: 빨간색 X 표시와 에러 로그 확인

## 4단계: 환경 변수 설정

### 4.1 백엔드 URL 설정
1. Vercel 대시보드에서 프로젝트 선택
2. **Settings** 탭 클릭
3. **Environment Variables** 섹션으로 이동
4. **Add** 버튼 클릭

### 4.2 환경 변수 추가
| Variable | Value | Environment |
|----------|-------|-------------|
| `REACT_APP_API_URL` | `https://your-backend-domain.vercel.app` | Production |
| `REACT_APP_API_URL` | `http://localhost:8000` | Preview |

## 5단계: 도메인 및 설정 확인

### 5.1 도메인 확인
- **Production URL**: `https://your-project-name.vercel.app`
- **Custom Domain**: 설정 가능 (선택사항)

### 5.2 설정 확인
- **Framework**: Create React App
- **Node.js Version**: 18.x (자동)
- **Build Output**: `/build` 폴더

## 6단계: 자동 배포 설정

### 6.1 GitHub 연동 확인
- **Repository**: `GeyuongGongPark/integrated-test-platform`
- **Branch**: `main`
- **Auto Deploy**: 활성화됨

### 6.2 배포 트리거
- **Push to main**: 자동 배포
- **Pull Request**: Preview 배포
- **Manual**: 수동 배포 가능

## 7단계: 테스트 및 확인

### 7.1 배포 테스트
```bash
# 프론트엔드 접속 테스트
curl https://your-project-name.vercel.app

# API 연결 테스트 (브라우저에서)
https://your-project-name.vercel.app
```

### 7.2 기능 확인
- ✅ **페이지 로딩**: React 앱 정상 표시
- ✅ **API 연결**: 백엔드와 통신 확인
- ✅ **반응형**: 모바일/데스크톱 확인

## 8단계: 문제 해결

### 8.1 빌드 실패
- **로그 확인**: Vercel 대시보드 → Functions → Logs
- **의존성 문제**: `package.json` 확인
- **Node.js 버전**: 18.x 사용 권장

### 8.2 API 연결 실패
- **CORS 설정**: 백엔드에서 프론트엔드 도메인 허용
- **환경 변수**: `REACT_APP_API_URL` 확인
- **네트워크**: 브라우저 개발자 도구에서 확인

### 8.3 성능 최적화
- **Bundle 분석**: `npm run build --analyze`
- **이미지 최적화**: WebP 형식 사용
- **코드 분할**: React.lazy() 사용

## 9단계: 추가 설정

### 9.1 커스텀 도메인 (선택사항)
1. **Settings** → **Domains**
2. **Add Domain** 클릭
3. 도메인 입력 및 DNS 설정

### 9.2 분석 도구 연결
- **Google Analytics**: 환경 변수로 설정
- **Sentry**: 에러 추적 설정
- **Hotjar**: 사용자 행동 분석

## 완료 체크리스트

- [ ] Vercel 계정 생성 및 로그인
- [ ] GitHub 레포지토리 연결
- [ ] 프론트엔드 프로젝트 설정
- [ ] 배포 성공 확인
- [ ] 환경 변수 설정
- [ ] API 연결 테스트
- [ ] 자동 배포 확인
- [ ] 기능 테스트 완료

## 다음 단계

1. **백엔드 배포**: 동일한 방법으로 백엔드도 배포
2. **통합 테스트**: 전체 플랫폼 테스트
3. **팀 공유**: URL을 팀원들과 공유
4. **모니터링**: Vercel Analytics 설정 