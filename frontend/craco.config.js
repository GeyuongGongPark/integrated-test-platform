const path = require('path');

module.exports = {
  webpack: {
    alias: {
      '@tms': path.resolve(__dirname, 'src'),
    },
  },
};
