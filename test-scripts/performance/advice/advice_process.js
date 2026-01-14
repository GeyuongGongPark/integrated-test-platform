import { check } from "k6";
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { browser } from "k6/browser";
import advice_clm from "./advice_clm.js";
import { URLS } from '../url/url_base.js';
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
};
export default async function () {
    // const page = await browser.newPage();

    try {
        const page = await advice_clm();
        }
    finally {
        await page.close();
    }
}

export function handleSummary(data) {
    const timestamp = getFormattedTimestamp().replace(/:/g, '_');
    return {
        [`Result/clm_process_summary_${timestamp}.html`]: htmlReport(data),
    };
}