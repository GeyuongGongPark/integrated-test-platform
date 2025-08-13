// Simple test script for basic functionality
const simpleTest = {
    // Basic functionality test
    runSimpleTest: async (page) => {
        console.log('Running simple functionality test...');
        
        try {
            // Navigate to main page
            await page.goto('/');
            
            // Check if page title exists
            const title = await page.title();
            console.log(`Page title: ${title}`);
            
            // Check if main content is visible
            const mainContent = await page.locator('main, [role="main"]');
            if (await mainContent.isVisible()) {
                console.log('✅ Simple test passed - main content is visible');
                return true;
            } else {
                console.log('❌ Simple test failed - main content not visible');
                return false;
            }
        } catch (error) {
            console.error('Simple test error:', error);
            return false;
        }
    }
};

module.exports = simpleTest;
