// tests/test_example.spec.js
import { test, expect } from '@playwright/test';
import axios from 'axios';
import { getCurrentLoginCredentials, URLS, SELECTORS } from '../url/config.js';
import { getFormattedTimestamp } from "../common/utils.js";

test('Login Test', async ({ page }) => {
    const credentials = getCurrentLoginCredentials();
    const testCaseId = 1; // 예시로 사용할 테스트 케이스 ID
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');

    await page.goto(URLS.LOGIN.HOME);
    await page.screenshot({ path: `screenshots/${getNewTimestamp()}_main.png` });

    await page.goto(URLS.LOGIN.LOGIN);
    await page.screenshot({ path: `screenshots/${getNewTimestamp()}_login.png` });

    await page.fill(SELECTORS.LOGIN.EMAIL_INPUT, credentials.EMAIL);
    await page.fill(SELECTORS.LOGIN.PASSWORD_INPUT, credentials.PASSWORD);
    await page.click(SELECTORS.LOGIN.SUBMIT_BUTTON);

    await page.waitForNavigation();
    await page.goto(URLS.LOGIN.DASHBOARD);
    await page.screenshot({ path: `screenshots/${getNewTimestamp()}_dashboard.png` });

    // 스크린샷 경로
    const screenshotPath = `screenshots/${getNewTimestamp()}_dashboard.png`;

    // 결과 기록
    await recordTestResult(testCaseId, 'Pass', screenshotPath);
});

const recordTestResult = async (testCaseId, result, screenshotPath) => {
    await axios.post('http://localhost:8000/testresults', {
        test_case_id: testCaseId,
        result: result,
        notes: 'Automated test result',
        screenshot: screenshotPath // 스크린샷 경로 추가
    });
};
