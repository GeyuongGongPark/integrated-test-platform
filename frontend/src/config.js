const config = {
  development: {
    apiUrl: 'http://localhost:5000',
    uploadUrl: 'http://localhost:5000/uploads'
  },
  production: {
    apiUrl: process.env.REACT_APP_API_URL || 'https://integrated-test-platform.vercel.app',
    uploadUrl: process.env.REACT_APP_UPLOAD_URL || 'https://integrated-test-platform.vercel.app/uploads'
  }
};

const environment = process.env.NODE_ENV || 'development';
export default config[environment]; 