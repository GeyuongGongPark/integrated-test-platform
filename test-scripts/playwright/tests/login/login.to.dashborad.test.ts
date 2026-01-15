import { test } from '@playwright/test';
import login_to_dashborad from '../../Base_Code/business/login/login_to_dashborad.js';

test('로그인 시나리오', async ({page}) => {
  await login_to_dashborad
})// 예시: playwright test runner 없이 직접 실행
import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: false }); // headless: false로 브라우저 창 표시
  const context = await browser.newContext();
  const page = await context.newPage();
  await login_to_dashborad(page); // 실제 동작 확인
  // 필요한 추가 동작...
  // await browser.close();
})();