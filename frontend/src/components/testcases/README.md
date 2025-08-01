# 🧪 Test Cases Component

## 개요
테스트 케이스 관리 기능을 담당하는 컴포넌트입니다.

## 기능
- 테스트 케이스 CRUD (생성, 조회, 수정, 삭제)
- 프로젝트별 테스트 케이스 분류
- 테스트 결과 기록 및 상태 관리
- 카테고리별 필터링

## 파일 구조
```
testcases/
├── TestCaseAPP.js        # 메인 테스트 케이스 컴포넌트
├── index.js              # 컴포넌트 export
└── README.md             # 이 파일
```

## 사용법
```javascript
import TestCaseApp from './components/testcases';

// App.js에서 사용
<TestCaseApp />
```

## API 엔드포인트
- `GET /testcases` - 테스트 케이스 목록 조회
- `POST /testcases` - 새 테스트 케이스 생성
- `PUT /testcases/:id` - 테스트 케이스 수정
- `DELETE /testcases/:id` - 테스트 케이스 삭제
- `GET /projects` - 프로젝트 목록 조회

## 의존성
- React (useState, useEffect)
- Axios (API 통신)
- CSS 스타일링 