import { test } from '@playwright/test';
import login_to_dashborad from '../../Base_Code/business/login/login_to_dashborad.js';
import { URLS } from '../../Base_Code/business/URL/url_base.js';
import { getFormattedTimestamp } from '../../Base_Code/business/common/utils.js';

const wait = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

test('로그아웃 시나리오', async ({ page }) => {
    const timestamp = getFormattedTimestamp().replace(/:/g, '_');

    await login_to_dashborad(page);

    await page.goto(URLS.SETTING.ACCOUNT);
    await page.screenshot({ path: `screenshots/${timestamp}_setting.png` });

    await page.locator('img[alt="이동"]').nth(4).click();
    await wait(3000);

    await page.screenshot({ path: `screenshots/${timestamp}_logout.png` });
});
