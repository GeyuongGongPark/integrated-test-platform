import login_to_dashborad from "../login/login_to_dashborad.js";
import { URLS } from "../URL/url_base.js";
import { getFormattedTimestamp } from "../common/utils.js";

async function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export default async function litigationDraft(page, options = {}) {
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    try {
        await login_to_dashborad(page);
        // 송무 임시 저장 리스트 호출
        await page.goto(URLS.LITIGATION.DRAFT);
        let timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/screenshots_${timestamp}.png`});
        // 신규 송무 등록 btn 선택
        await page.waitForSelector('//button[text()="신규 송무 등록" and not(@disabled)]');
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/screenshot_${timestamp}_before_request.png`});
        await page.locator('//button[text()="신규 송무 등록"]').click();
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/screenshot_${timestamp}_after_request.png`});
        return page;
    } catch (error) {
        console.error('litigation_draft.js 실행 중 오류:', error);
        throw error;
    }
}