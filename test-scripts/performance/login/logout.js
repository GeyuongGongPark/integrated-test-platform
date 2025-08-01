import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { browser } from 'k6/browser';
import { URLS } from '../url/base.js';
import { getCurrentLoginCredentials, SELECTORS } from '../url/config.js';
import { getFormattedTimestamp } from "../common/utils.js";
import login_to_dashborad from "./login_to_dashborad.js";

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
    },
};
async function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
export default async function () {
    const timestamp = getFormattedTimestamp().replace(/:/g, '_');
    let page;

    try {
        page = await login_to_dashborad();
        await page.goto(URLS.SETTING.ACCOUNT);
        await page.screenshot({path: `screenshots/${timestamp}_setting.png`});
        // const elements = await page.evaluate(() => {
        //     return Array.from(document.querySelectorAll('img[alt="이동"]')).map(el => el.outerHTML);
        // });
        // console.log(elements); // 실제로 몇 개가 있는지, 6번째가 맞는지 확인

        await page.evaluate(() => {
            document.querySelectorAll('img[alt="이동"]')[4].click();
        });
        await wait(3000);
        await page.screenshot({path: `screenshots/${timestamp}_logout.png`});
    } finally {
        if (page) {
            await page.close();
        }
    }
}

export function handleSummary(data){
    const timestamp = getFormattedTimestamp().replace(/:/g, '_');
    return{
        [`Result/logout_summary_${timestamp}.html`]: htmlReport(data),
    };
}