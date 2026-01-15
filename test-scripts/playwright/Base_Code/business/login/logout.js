import { URLS } from '../URL/url_base.js';
import { getFormattedTimestamp } from "../common/utils.js";
import login_to_dashborad from "./login_to_dashborad.js";

// Playwright 전용 로그아웃 헬퍼
// 사용법: await logout(page)
export default async function logout(page) {
    const timestamp = getFormattedTimestamp().replace(/:/g, '_');

    await login_to_dashborad(page);

    await page.goto(URLS.SETTING.ACCOUNT);
    await page.screenshot({ path: `screenshots/${timestamp}_setting.png` });

    await page.locator('img[alt="이동"]').nth(4).click();
    await page.waitForTimeout(3000);

    await page.screenshot({ path: `screenshots/${timestamp}_logout.png` });
}