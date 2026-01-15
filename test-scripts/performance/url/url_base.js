import { loadAccountEnv } from '../Account/Account_env.js';

const account = loadAccountEnv();
const BASE_URL = account.baseUrl;
console.log('account:', account);

// 로그인 관련 URL
export const LOGIN_URLS = {
    HOME: `${BASE_URL}`,
    LOGIN: `${BASE_URL}/login`,
    DASHBOARD: `${BASE_URL}/dashboard`
};
//My 계약서 URL
export const DRIVE_ULS = {
    DRIVE: `${BASE_URL}/drive`, //My 게약서
    TEAM: `${BASE_URL}/team_standard_contract` //기업 표준 계약서 
}

//대량생성 관련 URL
export const BULK_URLS = {
    BULK: `${BASE_URL}/bulk` //대량 생성
}
// CLM 관련 URL
export const CLM_URLS = {
    DRAFT: `${BASE_URL}/clm/draft`, //계약 검토 요청
    PROCESS: `${BASE_URL}/clm/process`, //계약 검토 요청 조회
    SEARCH: `${BASE_URL}/clm/search`, //통합검색
    REVIEW: `${BASE_URL}/clm/review`, //검토 요청 조회
    COMPLETE: `${BASE_URL}/clm/complete`, //체결 계약서 조회
    PAUSE: `${BASE_URL}/clm/complete?is_paused=2` //일시 중단 리스트
};

//SEAL 관련 URL
export const SEAL_URLS = {
    DRAFT: `${BASE_URL}/seal/draft`, //인감 사용 신청청
    REVIEW: `${BASE_URL}/seal`, //인감 사용 신청 조회
    LEDGER: `${BASE_URL}/seal/ledger` //인감 관리 대장
}
// Advice 관련 URL
export const ADVICE_URLS = {
    DRAFT: `${BASE_URL}/advice/draft`, //법률 지문 요청 
    PROCESS: `${BASE_URL}/advice/process`,
    REVIEW: `${BASE_URL}/advice` //법률 자문 조회
};

//Litigation 관련 URL
export const LITIGATION_URLS = {
    DRAFT: `${BASE_URL}/litigation/draft`, //송무 등록 
    PROCESS: `${BASE_URL}/litigation/process`,
    REVIEW: `${BASE_URL}/litigation`, //송무 조회 
    SCHEDULE: `${BASE_URL}/litigation/schedule` //송무 전체 일정
};

//법령 정보 관련 URL
export const LAW_URLS = {
    SCHEDULE: `${BASE_URL}/law` //법령 캘린더 
}

//프로젝트 관련 URL
export const PROJECT_URLS = {
    PROJECT: `${BASE_URL}/project` //프로젝트 조회
}

//계약 정보 관리 관련 URL
export const CONTRACT_URLS = {
    CONTRACT: `${BASE_URL}/contact`, //계약처 관리
    STAMP: `${BASE_URL}/template?type=stamp`, //직인
    LOGO: `${BASE_URL}/template?type=logo`, //로고
    TEAM_STAMP: `${BASE_URL}/template?type=team_stamp`, //기업직인 
    WATERMARK: `${BASE_URL}/template?type=watermark` //워터마크
}

//시스템 설정 관련 URL
export const SETTING_URLS = {
    TEAM: `${BASE_URL}/teams`, //구성원 관리
    ACCOUNT: `${BASE_URL}/profile?type=account`, //회원정보_계정 설정
    NOTIFICATION: `${BASE_URL}/profile?type=notification`, //회원정보_알림/이메일 수신 설정 
    LOG: `${BASE_URL}/profile?type=log`, //회원정보_로그인 기록
    FAILEDLOG: `${BASE_URL}/profile?type=failedLog`, //회원정보_로그인 실패 기록
    FA: `${BASE_URL}/profile?type=twoFA`, //2단계 인증
    MANAGEMENT: `${BASE_URL}/profile?type=deviceManagement`, //회원정보_로그인 관리 
    SETUP: `${BASE_URL}/setup` //설정
}

// 모든 URL을 하나의 객체로 통합
export const URLS = {
    BASE: BASE_URL,
    LOGIN: LOGIN_URLS,
    CLM: CLM_URLS,
    SEAL: SEAL_URLS,
    ADVICE: ADVICE_URLS,
    LITIGATION: LITIGATION_URLS,
    BULK: BULK_URLS,
    LAW: LAW_URLS,
    PROJECT: PROJECT_URLS,
    CONTRACT: CONTRACT_URLS,
    SETTING: SETTING_URLS
}; 

console.log('URLS:', URLS);