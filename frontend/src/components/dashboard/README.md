# 📊 Dashboard Component

## 개요
통합 테스트 플랫폼의 메인 대시보드 컴포넌트입니다.

## 기능
- 테스트 케이스 통계 표시
- 성능 테스트 결과 요약
- 프로젝트 진행 상황 모니터링
- 실시간 데이터 시각화

## 파일 구조
```
dashboard/
├── UnifiedDashboard.js    # 메인 대시보드 컴포넌트
├── index.js              # 컴포넌트 export
└── README.md             # 이 파일
```

## 사용법
```javascript
import UnifiedDashboard from './components/dashboard';

// App.js에서 사용
<UnifiedDashboard />
```

## 의존성
- React
- Axios (API 통신)
- CSS 스타일링 