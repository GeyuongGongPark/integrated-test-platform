const { test, expect } = require('@playwright/test');

test('로그인 테스트', async ({ page }) => {
  // 테스트 시작 시간 기록
  const startTime = Date.now();
  
  try {
    // 페이지 이동
    await page.goto('https://example.com/login');
    
    // 로그인 폼 입력
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'testpass');
    
    // 로그인 버튼 클릭
    await page.click('#login-button');
    
    // 로그인 성공 확인
    await expect(page).toHaveURL('https://example.com/dashboard');
    await expect(page.locator('.welcome-message')).toBeVisible();
    
    // 스크린샷 촬영
    await page.screenshot({ path: 'test-results/login-success.png' });
    
    console.log('로그인 테스트 성공');
    
  } catch (error) {
    // 실패 시 스크린샷 촬영
    await page.screenshot({ path: 'test-results/login-failed.png' });
    throw error;
  } finally {
    // 실행 시간 계산
    const executionTime = (Date.now() - startTime) / 1000;
    console.log(`테스트 실행 시간: ${executionTime}초`);
  }
});

test('잘못된 로그인 테스트', async ({ page }) => {
  const startTime = Date.now();
  
  try {
    await page.goto('https://example.com/login');
    
    // 잘못된 로그인 정보 입력
    await page.fill('#username', 'wronguser');
    await page.fill('#password', 'wrongpass');
    
    await page.click('#login-button');
    
    // 오류 메시지 확인
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText('잘못된 로그인 정보');
    
    await page.screenshot({ path: 'test-results/login-error.png' });
    
    console.log('잘못된 로그인 테스트 성공');
    
  } catch (error) {
    await page.screenshot({ path: 'test-results/login-error-failed.png' });
    throw error;
  } finally {
    const executionTime = (Date.now() - startTime) / 1000;
    console.log(`테스트 실행 시간: ${executionTime}초`);
  }
}); 