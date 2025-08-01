const config = {
  development: {
    apiUrl: 'http://localhost:5000',
    uploadUrl: 'http://localhost:5000/uploads'
  },
  production: {
    apiUrl: process.env.REACT_APP_API_URL || 'https://your-backend-domain.com',
    uploadUrl: process.env.REACT_APP_UPLOAD_URL || 'https://your-backend-domain.com/uploads'
  }
};

const environment = process.env.NODE_ENV || 'development';
export default config[environment]; 