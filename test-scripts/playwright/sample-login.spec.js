const { test, expect } = require('@playwright/test');
const { chromium, safari } = require('playwright');

test('로그인 테스트', async ({ page1 }) => {
  // 테스트 시작 시간 기록
  const startTime = Date.now();
  
  try {
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page1 = await context.newPage();

    // 페이지 이동
    await page1.goto('https://example.com/login');
    
    // 로그인 폼 입력
    await page1.fill('#username', 'testuser');
    await page1.fill('#password', 'testpass');
    
    // 로그인 버튼 클릭
    await page1.click('#login-button');
    
    // 로그인 성공 확인
    await expect(page1).toHaveURL('https://example.com/dashboard');
    await expect(page1.locator('.welcome-message')).toBeVisible();
    
    // 스크린샷 촬영
    await page1.screenshot({ path: 'test-results/login-success.png' });
    
    console.log('로그인 테스트 성공');
    
  } catch (error) {
    // 실패 시 스크린샷 촬영
    await page1.screenshot({ path: 'test-results/login-failed.png' });
    throw error;
  } finally {
    // 실행 시간 계산
    const executionTime = (Date.now() - startTime) / 1000;
    console.log(`테스트 실행 시간: ${executionTime}초`);
  }
});

test('잘못된 로그인 테스트', async ({ page1 }) => {
  const startTime = Date.now();
  
  try {
    await page1.goto('https://example.com/login');
    
    // 잘못된 로그인 정보 입력
    await page1.fill('#username', 'wronguser');
    await page1.fill('#password', 'wrongpass');
    
    await page1.click('#login-button');
    
    // 오류 메시지 확인
    await expect(page1.locator('.error-message')).toBeVisible();
    await expect(page1.locator('.error-message')).toContainText('잘못된 로그인 정보');
    
    await page1.screenshot({ path: 'test-results/login-error.png' });
    
    console.log('잘못된 로그인 테스트 성공');
    
  } catch (error) {
    await page1.screenshot({ path: 'test-results/login-error-failed.png' });
    throw error;
  } finally {
    const executionTime = (Date.now() - startTime) / 1000;
    console.log(`테스트 실행 시간: ${executionTime}초`);
  }
}); 

test('로그인 테스트2', async ({ page2 }) => {
  const startTime = Date.now();
  
  const browser = await safari.launch({ headless: false });
  const context = await browser.newContext();
  const page2 = await context.newPage();

  try {
    await page2.goto('https://example.com/login');
    await page2.screenshot({ path: 'test-results/login-success.png' });
    console.log('로그인 테스트 성공');
    
  } catch (error) {
    await page2.screenshot({ path: 'test-results/login-failed.png' });
    console.log('로그인 테스트 실패');
    throw error;
  } finally {
    const executionTime = (Date.now() - startTime) / 1000;
    console.log(`테스트 실행 시간: ${executionTime}초`);
    await browser.close();
  }
  
});