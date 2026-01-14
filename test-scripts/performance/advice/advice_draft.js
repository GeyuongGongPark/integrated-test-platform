import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { browser } from 'k6/browser';
import login_to_dashboard from "../login/login_to_dashboard.js";
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
            width: 2560,
            height: 1440,
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
    const page = await login_to_dashboard();
    // 법률 자문 임시 저장 리스트 호출
    await page.goto(URLS.ADVICE.DRAFT);
    let timestamp = getNewTimestamp();
    await page.screenshot({path: `screenshots/${timestamp}_advice_draft.png`});
    // 신규 자문 요청 btn 선택
    await page.waitForSelector('//button[text()="신규 자문 요청" and not(@disabled)]');
    await page.locator('//button[text()="신규 자문 요청"]').click();
    timestamp = getNewTimestamp();
    await page.screenshot({path: `screenshots/${timestamp}_after_request.png`});
    // 법률 자문 요청 모달 확인 btn 클릭
    await page.waitForSelector('//div[contains(@class,"footer-safe-area")]//button[text()="확인" and not(@disabled)]');
    await page.locator('//div[contains(@class,"footer-safe-area")]//button[text()="확인"]').click();
    timestamp = getNewTimestamp();
    await wait(10000);
    await page.screenshot({path: `screenshots/${timestamp}_after_confirm.png`});
    //자문 분류 선택
    await page.waitForSelector('//img[@alt="arrow"]');
    await page.locator('//img[@alt="arrow"]').click();
    if (__ENV.ADVICE_TYPE === "pi") {

    }
    else if (__ENV.ADVICE_TYPE === "cn") {

    }
    else if (__ENV.ADVICE_TYPE === "ft") {

    }
    else if (__ENV.ADVICE_TYPE === "ma") {

    }
    else if (__ENV.ADVICE_TYPE === "ci") {

    }
    else if (__ENV.ADVICE_TYPE === "tl") {

    }
    else if (__ENV.ADVICE_TYPE === "la") {

    }
    else if (__ENV.ADVICE_TYPE === "hr") {

    }
    else if (__ENV.ADVICE_TYPE === "cole") {

    }
    else if (__ENV.ADVICE_TYPE === "overle") {

    }
    else if (__ENV.ADVICE_TYPE === "etc") {

    }
    else { 
      console.log("input _ENV.ADVICE_TYPE");
    }
    return page;
  }
  finally{
    //await page.close();
  }
}
export function handleSummary(data) {
  const timestamp = getFormattedTimestamp().replace(/:/g, '_');  
  return {
        [`Result/advice_draft_summary_${timestamp}.html`]: htmlReport(data),
    };
}

