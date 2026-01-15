import { URLS } from '../URL/url_base.js';
import { getFormattedTimestamp } from "../common/utils.js";
import adviceDraft from "./draft/advice_draft.js";
import adviceApproved from "./approved/advice_approved.js";
import adviceLegal from "./legal/advice_legal.js";
import advicePause from "./pause/advice_pause.js";
import adviceCancel from "./cancel/advice_cancel.js";
import adviceComplete from "./complete/advice_complete.js";

export default async function adviceProcess(page, options = {}) {
    // 예시: 프로세스 페이지로 이동 후 상태 확인 (필요 시 로직 확장)
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    let timestamp = getNewTimestamp();

    try {
        const resultPage = await login_to_dashborad(page);
        await resultPage.goto(URLS.ADVICE.PROCESS);
        timestamp = getNewTimestamp();
        resultPage = await adviceDraft(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_advice_draft.png`});
        console.log("advice draft page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await adviceApproved(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_advice_approved.png`});
        console.log("advice approved page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await adviceLegal(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_advice_legal.png`});
        console.log("advice legal page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await advicePause(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_advice_pause.png`});
        console.log("advice pause page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await adviceCancel(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_advice_cancel.png`});
        console.log("advice cancel page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await adviceComplete(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_advice_complete.png`});
        console.log("advice complete page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
    } catch (error) {
        console.error('adviceProcess.js 실행 중 오류:', error);
        throw error;   
    }
}