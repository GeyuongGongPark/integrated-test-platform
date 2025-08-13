// Logout test script
const logout = {
    // Test logout functionality
    testLogout: async (page) => {
        console.log('Testing logout functionality...');
        
        // Click logout button
        await page.click('[data-testid="logout-button"]');
        
        // Wait for redirect to login page
        await page.waitForURL('/login');
        
        // Verify user is logged out
        const loginForm = await page.locator('[data-testid="login-form"]');
        if (await loginForm.isVisible()) {
            console.log('Logout test completed successfully');
        } else {
            throw new Error('Logout failed - user not redirected to login page');
        }
    }
};

module.exports = logout; 
