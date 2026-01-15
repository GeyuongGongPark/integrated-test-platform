import login_to_dashborad from "../../login/login_to_dashborad.js";
import { URLS } from "../../URL/url_base.js";
import { getFormattedTimestamp } from "../../common/utils.js";

async function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export async function approve_ok(page, options = {}) {
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    try{
        await login_to_dashborad(page);
        await page.goto(URLS.CLM.DRAFT);
        let timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_clm.png`});
        await page.waitForSelector('//button[text()="신규 검토 요청" and not(@disabled)]');
        await page.locator('//button[text()="신규 검토 요청"]').click();

        await page.waitForSelector('//div[contains(@class,"footer-safe-area")]//button[text()="확인" and not(@disabled)]');
        await page.locator('//div[contains(@class,"footer-safe-area")]//button[text()="확인"]').click();
        await page.waitForTimeout(10000);
        await page.screenshot({path: `screenshots/${timestamp}_after_confirm.png`});
        await page.locator('//label[.//div[text()="신규"]]').click();
        await page.waitForSelector('//div[text()="관련 계약 찾아보기"]');
        await page.locator('//div[text()="관련 계약 찾아보기"]').click();

    }
    catch (error) {
        console.error('clm.approve.ok.js 실행 중 오류:', error);
        throw error;
    }
}