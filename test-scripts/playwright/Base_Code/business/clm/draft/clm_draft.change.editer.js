import { URLS } from "../../URL/url_base.js";
import { getFormattedTimestamp } from "../../common/utils.js";
import { SELECTORS } from "../../URL/config.js";
import { UserInfo} from "../../Account/Account_env.js";
import login_to_dashborad from "../../login/login_to_dashborad.js";
import clmdraftnew from "./clm_draft.new.js";

export default async function clm_draft_change_editer(page, options = {}) {
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    let timestamp = getNewTimestamp();

    try {
        await login_to_dashborad(page);
        await page.goto(URLS.CLM.DRAFT);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_clm_draft.png`});
        console.log("clm draft page:", await page.url()); // 진입 페이지 URL 확인
        await clmdraftnew(page, options);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_clm_draft.png`});
        console.log("clm draft page:", await page.url()); // 진입 페이지 URL 확인
        if (options.APPROVAL_SET === "use") {
            await page.locator('img[alt="결재자 추가하기"]').click();
        } else {
            await page.locator('//div[text()="계약서 검토 요청"]').click();
            await page.screenshot({path: `screenshots/${timestamp}_creat.png`});
            await page.waitForSelector('//div[contains(@class,"footer-safe-area")]//button[text()="확인" and not(@disabled)]');
            await page.locator('//div[contains(@class,"footer-safe-area")]//button[text()="확인"]').click();
            await page.waitForTimeout(10000);
            await page.screenshot({path: `screenshots/${timestamp}_new_contrat.png`});
        }
        await page.screenshot({path: `screenshots/${timestamp}_after_request.png`});
        await page.locator().click();
        
    } catch (error) {
        console.error('clmDraftChangeEditer.js 실행 중 오류:', error);
        throw error;   
    }
}