import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { getFormattedTimestamp } from "../../common/utils.js";
import clm_draftNew from "./clm_draft.new.js";
import clm_draftChange from "./clm_draft.change.js";
import clm_draftStop from "./clm_draft.stop.js";


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
  const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
  let page;
  try {
    
    // 계약 구분 선택
    if ( __ENV.DRAFT_TYPE === "new") { // 계약 구분 : 신규
      page = await clm_draftNew();
    }
    else if ( __ENV.DRAFT_TYPE === "change") { // 계약 구분 : 변경
      page = await clm_draftChange();
    }
    else if ( __ENV.DRAFT_TYPE === "stop") { // 계약 구분 : 해지
      page = await clm_draftStop();
    }
    else {
      console.log("input __ENV.DRAFT_TYPE");
    }
    return page;
  } finally {
    //await page.close();
  }
}

export function handleSummary(data) {
  const timestamp = getFormattedTimestamp().replace(/:/g, '_');  
  return {
        [`Result/clm_draft_summary_${timestamp}.html`]: htmlReport(data),
    };
}

