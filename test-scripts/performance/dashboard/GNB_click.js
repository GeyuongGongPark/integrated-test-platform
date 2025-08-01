import { URLS } from '../url/base.js';
import login_to_dashborad from '../login/login_to_dashborad.js';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { getFormattedTimestamp } from '../common/utils.js';


  //브라우저 오픈
export const options = {
  scenarios: {
    ui: {
     executor: 'shared-iterations',
     options: {
        browser: {
        type: 'chromium',
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
        const page = await login_to_dashborad();
        let timestamp = getNewTimestamp();
        //CLM page
        await page.goto(URLS.CLM.DRAFT)
        await wait(5000);
        await page.screenshot({path: `screenshots/${timestamp}_clm_draft.png`});
        await page.goto(URLS.CLM.REVIEW)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_clm_review.png`});
        await page.goto(URLS.CLM.COMPLETE)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_clm_complete.png`});
        await page.goto(URLS.CLM.PAUSE)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_clm_pause.png`});
        //SEAL page
        await page.goto(URLS.SEAL.DRAFT)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_seal_draft.png`});
        await page.goto(URLS.SEAL.REVIEW)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_seal_review.png`});
        await page.goto(URLS.SEAL.LEDGER)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_seal_ledger.png`});
        //ADVICE page
        await page.goto(URLS.ADVICE.DRAFT)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_advice_draft.png`});
        await page.goto(URLS.ADVICE.REVIEW)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_advice_review.png`});
        //LITIGATGION page
        await page.goto(URLS.LITIGATION.DRAFT)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_litigation_draft.png`});
        await page.goto(URLS.LITIGATION.REVIEW)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_litigation_review.png`});
        await page.goto(URLS.LITIGATION.SCHEDULE)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_litigation_schedule.png`});
        //LAW page
        await page.goto(URLS.LAW.SCHEDULE)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_low_schedule.png`});
        //PROJECT page
        await page.goto(URLS.PROJECT.PROJECT)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_project.png`});
        //CONTRACT page
        await page.goto(URLS.CONTRACT.CONTRACT)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_contract.png`});
        await page.goto(URLS.CONTRACT.STAMP)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_stamp.png`});
        await page.goto(URLS.CONTRACT.LOGO)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_logo.png`});
        await page.goto(URLS.CONTRACT.TEAM_STAMP)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_team_stamp.png`});
        await page.goto(URLS.CONTRACT.WATERMARK)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_watermark.png`});
        //System Setting page
        await page.goto(URLS.SETTING.TEAM)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_team.png`});
        await page.goto(URLS.SETTING.ACCOUNT)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_account.png`});
        await page.goto(URLS.SETTING.NOTIFICATION)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_notification.png`});
        await page.goto(URLS.SETTING.LOG)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_log.png`});
        await page.goto(URLS.SETTING.FAILEDLOG)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_failedlog.png`});
        await page.goto(URLS.SETTING.FA)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_fa.png`});
        await page.goto(URLS.SETTING.MANAGEMENT)
        await page.screenshot({path: `screenshots/${timestamp}_management.png`});
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.goto(URLS.SETTING.SETUP)
        await wait(5000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `screenshots/${timestamp}_setup.png`});
    }
    finally {
        if (page) await page.close();
    }
}



//결과 저장 
  export function handleSummary(data) {
    const timestamp = getFormattedTimestamp().replace(/:/g, '_');  
    return {
          [`Result/all_page_summary_${timestamp}.html`]: htmlReport(data),
      };
  }