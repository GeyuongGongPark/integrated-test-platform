import { chromium } from 'playwright';
import { URLS } from '../URL/url_base.js';
import { SELECTORS } from '../URL/config.js';
import { getFormattedTimestamp } from '../utils.js';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
// import AutoDocPage from './create_autodoc.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
console.log('URLS:', URLS);

function loadAccountData() {
    const jsonPath = path.join(__dirname, '..', 'account', 'samsung.json');
    const fileContent = fs.readFileSync(jsonPath, 'utf-8');
    return JSON.parse(fileContent);
}


async function loginWithAccount(page, email, password, screenshotDir) {
    const getNewTimestamp = () => getFormattedTimestamp().replace(/:/g, '_');
    try {
        await page.goto(URLS.LOGIN.LOGIN);
        await page.waitForTimeout(3000);    // 페이지 로드 대기
        let timestamp = getNewTimestamp();
        await page.screenshot({path: `${screenshotDir}/${timestamp}_login.png`});
        await page.waitForSelector(SELECTORS.LOGIN.EMAIL_INPUT, { timeout: 15000 });    // 이메일 입력 필드 대기
        await page.fill(SELECTORS.LOGIN.EMAIL_INPUT, email);
        await page.fill(SELECTORS.LOGIN.PASSWORD_INPUT, password);    // 비밀번호 입력
        await page.click(SELECTORS.LOGIN.SUBMIT_BUTTON);
        await page.waitForURL(URLS.DRIVE.DRIVE, { timeout: 30000 });    // 드라이브 페이지 이동 대기
        await page.waitForTimeout(3000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `${screenshotDir}/${timestamp}_drive.png`});    // 드라이브 페이지 스크린샷
        await page.goto(URLS.DRIVE.DOCUMENT);
        await page.waitForTimeout(3000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `${screenshotDir}/${timestamp}_document.png`});    // 문서 페이지 스크린샷
        
        // XPath를 사용하여 요소 클릭
        const xpathSelector = '//*[@id="__next"]/div[3]/div[3]/div[1]/div/div/div/div/a';
        await page.locator(`xpath=${xpathSelector}`).waitFor({ timeout: 10000 });
        await page.locator(`xpath=${xpathSelector}`).click();
        await page.waitForTimeout(3000);
        timestamp = getNewTimestamp();
        await page.screenshot({path: `${screenshotDir}/${timestamp}_after_click.png`});    // 클릭 후 스크린샷
        
        // AutoDoc 페이지로 이동
        // const autoDocResult = await AutoDocPage(page, screenshotDir);    // AutoDoc 페이지로 이동 결과 반환
        // if (!autoDocResult.success) {
        //     console.error(autoDocResult.message);    // AutoDoc 페이지로 이동 실패 시 에러 출력
        // }
        
        return { success: true, message: '로그인 성공' };    // 로그인 성공 시 결과 반환
    } catch (error) {
        return { success: false, message: `로그인 실패: ${error.message}` };    // 로그인 실패 시 결과 반환
    }
    }

    function ensureScreenshotDir() {
        const screenshotDir = path.join(__dirname, '..', 'screenshots', 'samsung', 'documents');
        if (!fs.existsSync(screenshotDir)) {
            fs.mkdirSync(screenshotDir, { recursive: true });
        }
        return screenshotDir;
    }


async function main() {
    const browser = await chromium.launch({ headless: false });
    const screenshotDir = ensureScreenshotDir();
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        const data = loadAccountData();
        const account = data.DEV.master;

        console.log(`로그인 계정: ${account.id}`);
        console.log('LOGIN URL:', URLS.LOGIN.LOGIN);

        const loginResult = await loginWithAccount(page, account.id, account.password, screenshotDir);
        if (!loginResult.success) {
            console.error(loginResult.message);
            return;
        }
        console.log('로그인 성공');
    } catch (error) {
        console.error('main error:', error);
        throw error;
    } finally {
        // await browser.close();
    }

    console.log('URL:', await page.url());
}

main().catch(console.error);