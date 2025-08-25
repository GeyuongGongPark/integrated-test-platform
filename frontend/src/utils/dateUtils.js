/**
 * UTC 시간을 KST(한국 표준시)로 변환하는 유틸리티 함수들
 */

/**
 * UTC 시간을 KST로 변환
 * @param {string|Date} utcTime - UTC 시간 (ISO 문자열 또는 Date 객체)
 * @returns {Date} KST 시간
 */
export const convertUTCToKST = (utcTime) => {
  if (!utcTime) return null;
  
  const date = new Date(utcTime);
  if (isNaN(date.getTime())) return null;
  
  // UTC 시간을 KST로 변환 (UTC+9)
  const kstTime = new Date(date.getTime() + (9 * 60 * 60 * 1000));
  return kstTime;
};

/**
 * UTC 시간을 KST 문자열로 변환 (한국어 형식)
 * @param {string|Date} utcTime - UTC 시간
 * @returns {string} KST 시간 문자열
 */
export const formatUTCToKST = (utcTime) => {
  const kstTime = convertUTCToKST(utcTime);
  if (!kstTime) return 'N/A';
  
  return kstTime.toLocaleString('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
};

/**
 * UTC 시간을 KST 날짜만 표시 (한국어 형식)
 * @param {string|Date} utcTime - UTC 시간
 * @returns {string} KST 날짜 문자열
 */
export const formatUTCToKSTDate = (utcTime) => {
  const kstTime = convertUTCToKST(utcTime);
  if (!kstTime) return 'N/A';
  
  return kstTime.toLocaleDateString('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

/**
 * UTC 시간을 KST 시간만 표시 (한국어 형식)
 * @param {string|Date} utcTime - UTC 시간
 * @returns {string} KST 시간 문자열
 */
export const formatUTCToKSTTime = (utcTime) => {
  const kstTime = convertUTCToKST(utcTime);
  if (!kstTime) return 'N/A';
  
  return kstTime.toLocaleTimeString('ko-KR', {
    timeZone: 'Asia/Seoul',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
};

/**
 * Unix timestamp를 KST로 변환
 * @param {number} timestamp - Unix timestamp (초)
 * @returns {string} KST 시간 문자열
 */
export const formatUnixTimestampToKST = (timestamp) => {
  if (!timestamp) return 'N/A';
  
  // Unix timestamp를 밀리초로 변환
  const utcTime = new Date(timestamp * 1000);
  return formatUTCToKST(utcTime);
};
