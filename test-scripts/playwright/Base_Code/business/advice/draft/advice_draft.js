import login_to_dashborad from "../../login/login_to_dashborad.js";
import { URLS } from '../../URL/url_base.js';
import { getFormattedTimestamp } from "../../common/utils.js";

async function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export default async function adviceDraft(page, options = {}) {
  const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
  try {
    await login_to_dashborad(page);
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
    // 자문 분류 선택 (필요 시 확장)
    await page.waitForSelector('//img[@alt="arrow"]');
    await page.locator('//img[@alt="arrow"]').click();
    const adviceType = options.ADVICE_TYPE || "pi";
    switch (adviceType) {
      case "pi":
      case "cn":
      case "ft":
      case "ma":
      case "ci":
      case "tl":
      case "la":
      case "hr":
      case "cole":
      case "overle":
      case "etc":
      default:
        break;
    }
    return page;
  } catch (error) {
    console.error('advice_draft.js 실행 중 오류:', error);
    throw error;
  }
}

