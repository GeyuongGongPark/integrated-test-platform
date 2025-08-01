# 🛠️ Utils Components

## 개요
공통으로 사용되는 유틸리티 컴포넌트들을 모아둔 폴더입니다.

## 컴포넌트 목록

### ErrorBoundary
React 컴포넌트에서 발생하는 JavaScript 오류를 포착하고 처리하는 컴포넌트입니다.

#### 기능
- 자식 컴포넌트의 JavaScript 오류 포착
- 오류 발생 시 대체 UI 표시
- 개발 모드에서 오류 상세 정보 표시
- 사용자 친화적인 오류 메시지

#### 사용법
```javascript
import { ErrorBoundary } from './components/utils';

<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>
```

## 파일 구조
```
utils/
├── ErrorBoundary.js    # 오류 처리 컴포넌트
├── index.js           # 컴포넌트 export
└── README.md          # 이 파일
```

## 의존성
- React (Component, getDerivedStateFromError, componentDidCatch)
- CSS 스타일링 