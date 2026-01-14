import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import login_to_dashboard from "../login/login_to_dashboard.js";
import { URLS } from "../url/url_base.js";
import { getFormattedTimestamp } from "../common/utils.js";

export const options = {
    scenarios: {
        ui: {
            executor: 'shared-iterations',
            options: {
                browser: {
                    type: 'chromium',
                    defaultViewport: {
                        width: 1920,
                        height: 1080,
                    },
                },
            },
        },
    },
    thresholds: {
        checks: ['rate==1.0'],
    }
}

async function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export default async function () {
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    let page;

    try {
        // LFBZ login 처리
        const page = await login_to_dashboard();
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
               
        //return page;
    }
    finally {
        await page.close();
    }
}

export function handleSummary(data) {
    const timestamp = getFormattedTimestamp().replace(/:/g, '_');
    return {
        [`Result/litigation_draft_summary_${timestamp}.html`]: htmlReport(data),
    };
}