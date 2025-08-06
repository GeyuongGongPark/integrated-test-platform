const config = {
  development: {
    apiUrl: 'http://localhost:8000',
    uploadUrl: 'http://localhost:8000/uploads'
  },
  production: {
    apiUrl: process.env.REACT_APP_API_URL || 'https://backend-alpha-liard.vercel.app',
    uploadUrl: process.env.REACT_APP_UPLOAD_URL || 'https://backend-alpha-liard.vercel.app/uploads'
  }
};

// 환경에 따라 동적으로 설정 선택
const environment = process.env.NODE_ENV || 'development';
const currentConfig = config[environment];

// 환경 정보 로깅 (개발 환경에서만)
if (environment === 'development') {
  console.log('🌍 Environment:', environment);
  console.log('🔗 API URL:', currentConfig.apiUrl);
  console.log('📤 Upload URL:', currentConfig.uploadUrl);
}

export default currentConfig;