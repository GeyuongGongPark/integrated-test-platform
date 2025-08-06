import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 1,
  duration: '5s',  // 5초만 실행
};

export default function () {
  const response = http.get('https://httpbin.org/get');
  
  check(response, {
    'status is 200': (r) => r.status === 200,
  });
} 