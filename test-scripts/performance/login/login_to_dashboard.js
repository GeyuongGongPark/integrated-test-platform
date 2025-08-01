import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { browser } from 'k6/browser';
import { URLS } from '../url/base.js';
import { getCurrentLoginCredentials, SELECTORS } from '../url/config.js';
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

export default async function () {
  const page = await browser.newPage();
  const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
  const credentials = getCurrentLoginCredentials();
  
  try {
    await page.goto(URLS.LOGIN.HOME);
    let timestamp = getNewTimestamp();
    await page.screenshot({path: `screenshots/${timestamp}_main.png`});
    await page.goto(URLS.LOGIN.LOGIN);
    timestamp = getNewTimestamp();
    await page.screenshot({path: `screenshots/${timestamp}_login.png`});
    await page.waitForSelector(SELECTORS.LOGIN.EMAIL_INPUT);
    await page.type(SELECTORS.LOGIN.EMAIL_INPUT, credentials.EMAIL);
    await page.waitForSelector(SELECTORS.LOGIN.PASSWORD_INPUT);
    await page.type(SELECTORS.LOGIN.PASSWORD_INPUT, credentials.PASSWORD);
    await page.click(SELECTORS.LOGIN.SUBMIT_BUTTON, { nht: 0 });
    await page.goto(URLS.LOGIN.DASHBOARD);
    timestamp = getNewTimestamp();
    await page.screenshot({path: `screenshots/${timestamp}_dashborad.png`});
    return page;
  }

  finally{
    //await page.close();
  }
}
export function handleSummary(data) {
  const timestamp = getFormattedTimestamp().replace(/:/g, '_');
  return {
        [`Result/login_summary_${timestamp}.html`]: htmlReport(data),
    };
}

