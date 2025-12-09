/**
 * API 요청/응답 터미널 로깅 유틸리티
 * 개발 환경에서만 활성화됩니다.
 */

import axios from 'axios';

const isDevelopment = process.env.NODE_ENV === 'development';
const ENABLE_API_LOGGING = process.env.REACT_APP_ENABLE_API_LOGGING === 'true' || isDevelopment;

/**
 * 요청 인터셉터 - 터미널에 로그 출력
 */
axios.interceptors.request.use(
  (config) => {
    if (ENABLE_API_LOGGING) {
      const timestamp = new Date().toLocaleTimeString('ko-KR');
      const method = config.method?.toUpperCase() || 'GET';
      const url = config.url || '';
      
      // 터미널에 로그 출력 (브라우저 콘솔이 아닌 Node.js 터미널)
      // 개발 서버 터미널에서 확인 가능
      console.log(`[${timestamp}] → ${method} ${url}`);
      
      // 요청 데이터가 있으면 표시 (민감한 정보 제외)
      if (config.data && typeof config.data === 'object') {
        const sanitizedData = { ...config.data };
        // 비밀번호나 토큰 같은 민감한 정보는 마스킹
        if (sanitizedData.password) sanitizedData.password = '***';
        if (sanitizedData.token) sanitizedData.token = '***';
        console.log('  Request Data:', JSON.stringify(sanitizedData, null, 2));
      }
      
      // Authorization 헤더 확인
      if (config.headers?.Authorization) {
        console.log('  Authorization: Bearer ***');
      }
    }
    
    return config;
  },
  (error) => {
    if (ENABLE_API_LOGGING) {
      console.error('  Request Error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * 응답 인터셉터 - 터미널에 로그 출력
 */
axios.interceptors.response.use(
  (response) => {
    if (ENABLE_API_LOGGING) {
      const timestamp = new Date().toLocaleTimeString('ko-KR');
      const status = response.status;
      const url = response.config?.url || '';
      const method = response.config?.method?.toUpperCase() || 'GET';
      
      // 성공 응답
      console.log(`[${timestamp}] ← ${status} ${method} ${url}`);
      
      // 응답 데이터가 있으면 표시 (큰 데이터는 요약만)
      if (response.data) {
        const dataStr = JSON.stringify(response.data);
        if (dataStr.length > 500) {
          console.log('  Response: [Large data, ' + dataStr.length + ' chars]');
          if (Array.isArray(response.data)) {
            console.log(`  Array length: ${response.data.length}`);
          }
        } else {
          console.log('  Response:', JSON.stringify(response.data, null, 2));
        }
      }
    }
    
    return response;
  },
  (error) => {
    if (ENABLE_API_LOGGING) {
      const timestamp = new Date().toLocaleTimeString('ko-KR');
      const status = error.response?.status || 'NETWORK';
      const url = error.config?.url || 'unknown';
      const method = error.config?.method?.toUpperCase() || 'GET';
      
      // 에러 응답
      console.error(`[${timestamp}] ✗ ${status} ${method} ${url}`);
      
      if (error.response?.data) {
        console.error('  Error:', JSON.stringify(error.response.data, null, 2));
      } else {
        console.error('  Error:', error.message);
      }
    }
    
    return Promise.reject(error);
  }
);

export default axios;

