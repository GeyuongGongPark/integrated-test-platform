// Common utility functions for performance testing
const utils = {
    // Generate random data
    generateRandomString: (length = 10) => {
        return Math.random().toString(36).substring(2, length + 2);
    },
    
    // Wait for specified time
    wait: (ms) => {
        return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    // Format timestamp
    formatTimestamp: (timestamp) => {
        return new Date(timestamp).toISOString();
    }
};

module.exports = utils; 
