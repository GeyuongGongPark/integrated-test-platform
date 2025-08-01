# ⚡ Performance Test Component

## 개요
성능 테스트 관리 및 실행을 담당하는 컴포넌트입니다.

## 기능
- 성능 테스트 스크립트 관리
- 테스트 실행 및 모니터링
- 성능 지표 시각화
- 테스트 결과 분석

## 파일 구조
```
performance/
├── PerformanceTestManager.js    # 메인 성능 테스트 컴포넌트
├── index.js                    # 컴포넌트 export
└── README.md                   # 이 파일
```

## 사용법
```javascript
import PerformanceTestManager from './components/performance';

// App.js에서 사용
<PerformanceTestManager />
```

## 주요 기능
- 성능 테스트 스크립트 업로드
- 테스트 실행 상태 모니터링
- 결과 리포트 생성
- 성능 지표 대시보드

## 의존성
- React (useState, useEffect)
- Axios (API 통신)
- CSS 스타일링
- 차트 라이브러리 (선택사항) 