import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import login_to_dashboard from "../login/login_to_dashboard.js";
import { SELECTORS } from '../url/config.js';
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
        await wait(5000);
        await page.locator(SELECTORS.DASHBOARD.SETTING).click();
        await wait(5000);
        await page.screenshot({path: `screenshots/screenshot_${timestamp}.png`});
        await wait(5000);
        //return page;
    }
    finally{
        await page.close();
    }
}
export function handleSummary(data) {
    const timestamp = getFormattedTimestamp().replace(/:/g, '_');
    return {
        [`Result/dashboard_setting_summary_${timestamp}.html`]: htmlReport(data),
    };
}