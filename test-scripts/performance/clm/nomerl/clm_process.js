import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { getFormattedTimestamp } from "../../common/utils.js";
import clm_draft from "./clm_draft.js";
import _ENV from "../../_ENV.js";


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

async function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export default async function () {
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    let page;

    try {
        page = await clm_draft();

        
        
        if ( _ENV.CLM_PROGRESS === "1") {
            

        }
        else if (_ENV.CLM_PROGRESS === "2") {

        }
        else {

        }
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