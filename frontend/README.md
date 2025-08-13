# Integrated Test Platform - Frontend

React 기반의 통합 테스트 플랫폼 프론트엔드 애플리케이션입니다.

## 🚀 주요 기능

- **대시보드**: 통합된 테스트 결과 및 통계
- **성능 테스트**: K6 기반 성능 테스트 관리
- **자동화 테스트**: Playwright 기반 자동화 테스트
- **테스트 케이스**: 체계적인 테스트 케이스 관리
- **사용자 관리**: 프로젝트별 사용자 권한 관리

## 🏗️ 프로젝트 구조

```
src/
├── components/              # React 컴포넌트
│   ├── dashboard/          # 대시보드 관련 컴포넌트
│   ├── performance/        # 성능 테스트 컴포넌트
│   ├── automation/         # 자동화 테스트 컴포넌트
│   ├── testcases/          # 테스트 케이스 컴포넌트
│   ├── settings/           # 설정 관련 컴포넌트
│   └── utils/              # 유틸리티 컴포넌트
├── App.js                  # 메인 애플리케이션 컴포넌트
├── App.css                 # 메인 스타일
├── index.js                # 애플리케이션 진입점
└── config.js               # 설정 파일
```

## 🛠️ 기술 스택

- **React 18**: 사용자 인터페이스
- **CSS3**: 스타일링
- **Chart.js**: 데이터 시각화
- **Material-UI**: UI 컴포넌트 (계획)

## 📦 설치 및 실행

### 1. 의존성 설치
```bash
npm install
```

### 2. 개발 서버 실행
```bash
npm start
```

### 3. 프로덕션 빌드
```bash
npm run build
```

### 4. 테스트 실행
```bash
npm test
```

## 🔧 환경 설정

프론트엔드 설정은 `src/config.js`에서 관리됩니다:

```javascript
const config = {
  apiBaseUrl: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  // 기타 설정...
};
```

## 📱 컴포넌트 설명

### Dashboard
- **UnifiedDashboard**: 통합 대시보드
- **FolderManager**: 폴더 관리

### Performance Testing
- **PerformanceTestManager**: 성능 테스트 관리

### Automation Testing
- **AutomationTestManager**: 자동화 테스트 관리
- **AutomationTestDetail**: 자동화 테스트 상세

### Test Cases
- **TestCaseAPP**: 테스트 케이스 관리

### Settings
- **Settings**: 설정 메인 페이지
- **AccountManager**: 계정 관리
- **ProjectManager**: 프로젝트 관리
- **FolderManager**: 폴더 관리

## 🎨 스타일링

현재 CSS3를 사용하여 스타일링하고 있으며, 향후 Material-UI 도입을 계획하고 있습니다.

## 🧪 테스트

```bash
# 단위 테스트 실행
npm test

# 테스트 커버리지 확인
npm test -- --coverage

# E2E 테스트 (Playwright)
cd ../test-scripts/playwright
npx playwright test
```

## 📦 배포

### Vercel 배포
```bash
npm run build
vercel --prod
```

### 정적 파일 서버
```bash
npm run build
# build 폴더를 웹 서버에 업로드
```

## 🔄 개발 워크플로우

1. **기능 개발**: 새로운 컴포넌트 또는 기능 추가
2. **테스트**: 단위 테스트 및 통합 테스트 작성
3. **리뷰**: 코드 리뷰 및 품질 검증
4. **배포**: 테스트 통과 후 배포

## 📚 추가 문서

- [API 테스팅 가이드](../API_TESTING_GUIDE.md)
- [사용법 가이드](../docs/USAGE.md)
- [배포 가이드](../docs/DEPLOYMENT_SUCCESS.md)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
