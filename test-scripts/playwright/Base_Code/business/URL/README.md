# URL 관리 시스템

이 폴더는 k6 테스트 스크립트에서 사용하는 모든 URL과 설정을 중앙에서 관리합니다.

## 파일 구조

- `base.js`: 기본 URL 정의
- `config.js`: 환경별 설정 및 로그인 정보
- `index.js`: 모든 설정을 한 곳에서 export

## 사용 방법

### 1. 기본 사용법

```javascript
import { URLS } from '../url/base.js';

// CLM Draft 페이지로 이동
await page.goto(URLS.CLM.DRAFT);

// Advice Draft 페이지로 이동
await page.goto(URLS.ADVICE.DRAFT);
```

### 2. 로그인 정보 사용

```javascript
import { getCurrentLoginCredentials, SELECTORS } from '../url/config.js';

// 현재 환경의 로그인 정보 가져오기
const credentials = getCurrentLoginCredentials();

// 로그인
await page.type(SELECTORS.LOGIN.EMAIL_INPUT, credentials.EMAIL);
await page.type(SELECTORS.LOGIN.PASSWORD_INPUT, credentials.PASSWORD);
```

### 3. 환경 변경

`config.js`에서 `CURRENT_ENV`를 변경하여 다른 환경을 사용할 수 있습니다:

```javascript
// alpha 환경으로 변경
export const CURRENT_ENV = ENVIRONMENTS.alpha;

// 개발 환경으로 변경
export const CURRENT_ENV = ENVIRONMENTS.DEVELOPMENT;
```

### 4. 환경별 로그인 정보 설정

각 환경별로 다른 로그인 정보를 사용할 수 있습니다:

```javascript
// config.js에서 환경별 로그인 정보 설정
export const LOGIN_CREDENTIALS = {
    PRODUCTION: {
        EMAIL: 'prod_email@example.com',
        PASSWORD: 'prod_password'
    },
    alpha: {
        EMAIL: 'alpha_email@example.com',
        PASSWORD: 'alpha_password'
    },
    DEVELOPMENT: {
        EMAIL: 'dev_email@example.com',
        PASSWORD: 'dev_password'
    }
};
```

## URL 구조

- `URLS.LOGIN.HOME`: 메인 페이지
- `URLS.LOGIN.LOGIN`: 로그인 페이지
- `URLS.LOGIN.DASHBOARD`: 대시보드
- `URLS.CLM.DRAFT`: CLM 초안 페이지
- `URLS.CLM.PROCESS`: CLM 처리 페이지
- `URLS.ADVICE.DRAFT`: Advice 초안 페이지
- `URLS.ADVICE.PROCESS`: Advice 처리 페이지

## 지원 환경

- **PRODUCTION**: `https://business.lawform.io`
- **alpha**: `https://alpha.business.lfdev.io`
## 장점

1. **중앙 관리**: 모든 URL을 한 곳에서 관리
2. **환경별 설정**: 개발/alpha/프로덕션 환경 쉽게 전환
3. **환경별 로그인**: 각 환경에 맞는 로그인 정보 자동 사용
4. **유지보수성**: URL 변경 시 한 곳만 수정하면 됨
5. **재사용성**: 여러 스크립트에서 동일한 URL 사용 가능 