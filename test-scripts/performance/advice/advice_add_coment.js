import {htmlReport} from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { browser } from 'k6/browser';
import login_to_dashboard from "../login/login_to_dashboard";
import { URLS } from "../url/url_base";
import { getFormattedTimestamp } from "../common/utils";

export const options = {
    scenarios: {
        ui: {
            executor: 'shared-iterations',
            options: {
                browser: {
                    type : 'chromium',
                    defaultViewport: {
                        width: 2560,
                        height: 1440,
                    }
                }
            }
        }
    },
    threshold:{ 
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
        const page = await login_to_dashboard();
        await page.goto(URLS.ADVICE.REVIEW);
        console.log(`URL: ${URLS.ADVICE.REVIEW}`);
        let timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_advice_review.png`});

    }
    finally {}
}

export function handlesummary(data) {
    const timestamp = getFormattedTimestamp().replace(/:/g, '_');
    return{
        [`Result/advice/advice_add_coment_${timestamp}.html`]: htmlReport(data),
    }
}