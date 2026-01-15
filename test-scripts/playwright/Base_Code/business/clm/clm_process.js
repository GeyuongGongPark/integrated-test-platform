import { URLS } from '../URL/url_base.js';
import { getFormattedTimestamp } from "../common/utils.js";
import clmDraft from "./draft/clm_draft.js";
import clmApproved from "./approved/clm_approved.js";
import clmLegal from "./legal/clm_legal.js";
import clmFinalApproved from "./final_approved/clm_final_approved.js";
import clmSeal from "./seal/clm_seal.js";
import clmEsign from "./esign/clm_esign.js";
import clmComplete from "./complete/clm_complete.js";
import clmPause from "./pause/clm_pause.js";
import clmCancel from "./cancel/clm_cancel.js";



export default async function clmProcess(page, options = {}) {
    // 예시: 프로세스 페이지로 이동 후 상태 확인 (필요 시 로직 확장)
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    let timestamp = getNewTimestamp();

    try {
        const resultPage = await login_to_dashborad(page);
        await resultPage.goto(URLS.CLM.PROCESS);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_clm_process.png`});
        console.log("clm process page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
        resultPage = await clmDraft(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_clm_draft.png`});
        console.log("clm draft page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
        resultPage = await clmApproved(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_clm_approved.png`});
        console.log("clm approved page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
        resultPage = await clmLegal(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshoßt({path: `screenshots/${timestamp}_clm_legal.png`});
        console.log("clm legal page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
        resultPage = await clmFinalApproved(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshoßt({path: `screenshots/${timestamp}_clm_final_approved.png`});
        console.log("clm final approved page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
        resultPage = await clmSeal(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshoßt({path: `screenshots/${timestamp}_clm_seal.png`});
        console.log("clm seal page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
        resultPage = await clmEsign(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshoßt({path: `screenshots/${timestamp}_clm_esign.png`});
        console.log("clm esign page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
        resultPage = await clmComplete(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshoßt({path: `screenshots/${timestamp}_clm_complete.png`});
        console.log("clm complete page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
        resultPage = await clmPause(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshoßt({path: `screenshots/${timestamp}_clm_pause.png`});
        console.log("clm pause page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
        resultPage = await clmCancel(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshoßt({path: `screenshots/${timestamp}_clm_cancel.png`});
        console.log("clm cancel page:", await resultPage.url()); // 진입 페이지 URL 확인
        return resultPage;
    } catch (error) {
        console.error('clm_process.js 실행 중 오류:', error);
        throw error;   
    }
}