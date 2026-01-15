import { URLS } from './URL/url_base.js';
import { getFormattedTimestamp } from './common/utils.js';
import login_to_dashborad from './login/login_to_dashborad.js';
import clmProcess from './clm/clm_process.js';
import adviceProcess from './advice/advice_process.js';
import litigationProcess from './litigation/litigation_process.js';
import bulkProcess from './bulk/bulk_process.js';
import projectProcess from './project/project_process.js';
import contractProcess from './contract/contract_process.js';
import settingProcess from './setting/setting_process.js';



export default async function LFBZProcess(page, options = {}) {
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    let timestamp = getNewTimestamp();

    try {
        const resultPage = await login_to_dashborad(page);
        await resultPage.goto(URLS.LFBZ.PROCESS);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_lfbz_process.png`});
        console.log("lfbz process page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await clmProcess(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_clm_process.png`});
        console.log("clm process page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await adviceProcess(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_advice_process.png`});
        console.log("advice process page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await litigationProcess(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_litigation_process.png`});
        console.log("litigation process page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await bulkProcess(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_bulk_process.png`});
        console.log("bulk process page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await lawProcess(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_law_process.png`});
        console.log("law process page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await projectProcess(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_project_process.png`});
        console.log("project process page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await contractProcess(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_contract_process.png`});
        console.log("contract process page:", await resultPage.url()); // 진입 페이지 URL 확인
        resultPage = await settingProcess(resultPage, options);
        timestamp = getNewTimestamp();
        await resultPage.screenshot({path: `screenshots/${timestamp}_setting_process.png`});
        console.log("setting process page:", await resultPage.url()); // 진입 페이지 URL 확�
        return resultPage;
    } catch (error) {
        console.error('LFBZProcess.js 실행 중 오류:', error);
        throw error;
    }
}