import login_to_dashborad from "../login/login_to_dashborad.js";
import { URLS } from "../URL/url_base.js";
import { getFormattedTimestamp } from "../common/utils.js";
import { SELECTORS } from "../URL/config.js";
import { UserInfo } from "../Account/Account_env.js";
import clmdraft from "./draft/clm_draft.js";

export default async function clm_detail(page, options = {}) {
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    let timestamp = getNewTimestamp();

    try {
        await login_to_dashborad(page);
        await page.goto(URLS.CLM.PROCESS);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_clm_detail.png`});
        console.log("clm detail page:", await page.url()); // 진입 페이지 URL 확인
        await clmdraft(page, options);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_clm_draft.png`});
        console.log("clm draft page:", await page.url()); // 진입 페이지 URL 확인
        return page;
    } catch (error) {
        console.error('clmDetail.js 실행 중 오류:', error);
        throw error;   
    }
}