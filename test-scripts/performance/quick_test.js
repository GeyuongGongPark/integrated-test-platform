// Quick test script for performance testing
const quickTest = {
    // Quick performance test
    runQuickTest: async (page) => {
        console.log('Running quick performance test...');
        
        const startTime = Date.now();
        
        // Navigate to main page
        await page.goto('/');
        
        // Wait for page load
        await page.waitForLoadState('networkidle');
        
        const loadTime = Date.now() - startTime;
        console.log(`Page load time: ${loadTime}ms`);
        
        // Basic performance assertions
        if (loadTime < 3000) {
            console.log('✅ Quick test passed - page loads within 3 seconds');
        } else {
            console.log('❌ Quick test failed - page takes too long to load');
        }
        
        return loadTime;
    }
};

module.exports = quickTest;
