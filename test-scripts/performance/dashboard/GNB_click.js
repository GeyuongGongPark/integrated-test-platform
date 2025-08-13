// GNB (Global Navigation Bar) click test script
const gnbClick = {
    // Test GNB navigation
    testGNBNavigation: async (page) => {
        console.log('Testing GNB navigation...');
        
        // Test main menu clicks
        const menuItems = ['dashboard', 'performance', 'automation', 'testcases'];
        
        for (const item of menuItems) {
            await page.click(`[data-testid="gnb-${item}"]`);
            await page.waitForLoadState('networkidle');
            console.log(`Clicked on ${item} menu`);
        }
        
        console.log('GNB navigation test completed');
    }
};

module.exports = gnbClick; 
