# URL Configuration

이 디렉토리는 테스트 환경별 URL 설정을 관리합니다.

## 파일 구조
- `base.js`: 기본 URL 설정
- `config.js`: 테스트 설정
- `index.js`: 설정 내보내기
- `env_data.json`: 환경별 데이터

## 사용법
```javascript
const { base, config } = require('./url');
``` 
