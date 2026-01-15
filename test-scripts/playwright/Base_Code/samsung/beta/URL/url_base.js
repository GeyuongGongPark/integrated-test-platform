import { loadAccountEnv } from '../account/Account_env.js';

const account = await loadAccountEnv();
console.log('account:', account);

let BASE_URL = '';
BASE_URL = account.baseUrl;

// 로그인 관련 URL
export const LOGIN_URLS = {
    LOGIN: `${BASE_URL}/login`
};
//My 계약서 URL
export const DRIVE_URLS = {
    DRIVE: `${BASE_URL}/drive`, //내 문서함
    DOCUMENT: `${BASE_URL}/drive#documents_finder` //문서 생성
}
// CLM 관련 URL
export const CLM_URLS = {
    REVIEW: `${BASE_URL}/clm/review` //문서 조회
};

// 모든 URL을 하나의 객체로 통합
export const URLS = {
    BASE: BASE_URL,
    LOGIN: LOGIN_URLS,
    CLM: CLM_URLS,
    DRIVE: DRIVE_URLS,
}; 

