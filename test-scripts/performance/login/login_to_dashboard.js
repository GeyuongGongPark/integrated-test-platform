// Login to dashboard test script
const loginToDashboard = {
    // Test login functionality
    testLogin: async (page) => {
        console.log('Testing login functionality...');
        
        // Navigate to login page
        await page.goto('/login');
        
        // Fill login form
        await page.fill('[data-testid="username"]', 'testuser');
        await page.fill('[data-testid="password"]', 'testpass');
        
        // Submit form
        await page.click('[data-testid="login-button"]');
        
        // Wait for redirect to dashboard
        await page.waitForURL('/dashboard');
        
        console.log('Login test completed successfully');
    }
};

module.exports = loginToDashboard; 
