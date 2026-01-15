// 환경별 설정
export const ENVIRONMENTS = {
    PRODUCTION: {
        BASE_URL: 'https://samsung.business.lawform.io',
        NAME: 'production'
    },
    alpha: {
        BASE_URL: 'https://samsung.business.lfdev.io',
        NAME: 'alpha'
    }
};

// 현재 사용할 환경 (기본값: PRODUCTION)
export const CURRENT_ENV = ENVIRONMENTS.PRODUCTION;

// 환경별 로그인 정보
export const LOGIN_CREDENTIALS = {
    PRODUCTION: {
        EMAIL: 'ggpark+sam_m@amicuslex.net',
        PASSWORD: '1q2w#E$R'
    },
    alpha: {
        EMAIL: 'ggpark+sam_m@amicuslex.net',
        PASSWORD: '1q2w#E$R'
    }
};

// 현재 환경의 로그인 정보를 가져오는 함수
export function getCurrentLoginCredentials() {
    return LOGIN_CREDENTIALS[CURRENT_ENV.NAME] || LOGIN_CREDENTIALS.PRODUCTION;
}

// 셀렉터 정보
export const SELECTORS = {
    
    LOGIN: {
        EMAIL_INPUT: 'input[type="email"]',
        PASSWORD_INPUT: 'input[type="password"]',
        SUBMIT_BUTTON: 'button[type="submit"]',
        LOGOUT: 'img[alt="이동"]'
    },
    GNB: {
        MY: 'img[alt="내 문서함"]',
        // 계약서 생성 영역 
        AUTO: 'img[alt="문서 작성"]',
        REVIEW: 'img[alt="문서 조회"]',
        LOGOUT: 'button[text()="로그아웃"]'
    }
}; 