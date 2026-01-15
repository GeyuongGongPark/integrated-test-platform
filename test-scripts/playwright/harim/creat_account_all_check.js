import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getFormattedTimestamp } from "../Base_Code/common/utils.js";
import { SELECTORS } from '../Base_Code/URL/config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 기본 URL 설정 (환경변수 또는 기본값 사용)
const BASE_URL = process.env.BASE_URL || 'https://harim.business.lawform.io';

console.log(`Base URL: ${BASE_URL}`);

// JSON 파일 로드
function loadAccountData() {
    const jsonPath = path.join(__dirname, 'harim_account_all.json');
    const fileContent = fs.readFileSync(jsonPath, 'utf-8');
    return JSON.parse(fileContent);
}

// 로그인 함수
async function loginWithAccount(page, email, password, baseUrl) {
    try {
        await page.goto(baseUrl, { waitUntil: 'networkidle' });
        await page.goto(`${baseUrl}/login`, { waitUntil: 'networkidle' });

        await page.waitForSelector(SELECTORS.LOGIN.EMAIL_INPUT, { timeout: 15000 });
        await page.fill(SELECTORS.LOGIN.EMAIL_INPUT, email);
        await page.fill(SELECTORS.LOGIN.PASSWORD_INPUT, password);
        await page.click(SELECTORS.LOGIN.SUBMIT_BUTTON);

        // 대시보드로 이동했는지 확인
        await page.waitForURL(`${baseUrl}/dashboard`, { timeout: 30000 });
        return { success: true, message: '로그인 성공' };
    } catch (error) {
        return { success: false, message: `로그인 실패: ${error.message}` };
    }
}

// 로그아웃 함수
async function logoutAccount(page, baseUrl) {
    try {
        await page.goto(`${baseUrl}/profile?type=account`, { waitUntil: 'networkidle' });
        
        // 로그아웃 버튼 클릭
        const logoutButton = page.locator('img[alt="이동"]').nth(4);
        if (await logoutButton.isVisible({ timeout: 5000 })) {
            await logoutButton.click();
            await page.waitForTimeout(3000);
            return { success: true, message: '로그아웃 성공' };
        } else {
            return { success: false, message: '로그아웃 버튼을 찾을 수 없음' };
        }
    } catch (error) {
        return { success: false, message: `로그아웃 실패: ${error.message}` };
    }
}

// 스크린샷 저장 디렉토리 생성
function ensureScreenshotDir() {
    const screenshotDir = path.join(__dirname, '..', 'screenshots', 'harim_account_test');
    if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir, { recursive: true });
    }
    return screenshotDir;
}

// 실패한 계정 파일 파싱 함수
function parseFailAccountsFromText(failTextContent) {
    const accounts = [];
    const lines = failTextContent.split('\n');
    
    let currentAccount = null;
    let inLogsSection = false;
    let logContent = '';
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // 계정 시작 라인 감지: "  - {계정}: {에러 메시지}"
        if (line.startsWith('- ') && line.includes('@')) {
            // 이전 계정 저장
            if (currentAccount) {
                currentAccount.hasNavigatedTo = logContent.includes('navigated to');
                currentAccount.logContent = logContent.trim();
                accounts.push(currentAccount);
            }
            
            // 새 계정 시작
            const match = line.match(/^- (.+?): (.+)$/);
            if (match) {
                currentAccount = {
                    account: match[1],
                    errorMessage: match[2],
                    hasNavigatedTo: false,
                    logContent: ''
                };
                inLogsSection = false;
                logContent = '';
            }
        }
        // 로그 섹션 시작
        else if (line.includes('logs ===========================')) {
            inLogsSection = true;
            logContent = '';
        }
        // 로그 섹션 종료
        else if (line.includes('============================================================')) {
            if (inLogsSection && currentAccount) {
                currentAccount.hasNavigatedTo = logContent.includes('navigated to');
                currentAccount.logContent = logContent.trim();
            }
            inLogsSection = false;
        }
        // 로그 내용 수집
        else if (inLogsSection && currentAccount) {
            logContent += line + '\n';
        }
    }
    
    // 마지막 계정 저장
    if (currentAccount) {
        currentAccount.hasNavigatedTo = logContent.includes('navigated to');
        currentAccount.logContent = logContent.trim();
        accounts.push(currentAccount);
    }
    
    return accounts;
}

// 실패한 계정 분석 함수
function analyzeFailAccounts(failedAccountsDetails, screenshotDir) {
    if (failedAccountsDetails.length === 0) {
        console.log('\n실패한 계정이 없어 분석을 건너뜁니다.');
        return null;
    }

    // 실패한 계정 목록을 텍스트 형식으로 생성 (기존 형식과 동일하게)
    let failTextContent = '실패한 계정 목록:\n';
    failedAccountsDetails.forEach(detail => {
        failTextContent += `  - ${detail.account}: ${detail.login.message}\n`;
        failTextContent += '=========================== logs ===========================\n';
        // 에러 메시지에서 로그 정보 추출 (실제 로그는 테스트 결과에 포함되지 않을 수 있음)
        failTextContent += `waiting for navigation to "${BASE_URL}/dashboard" until "load"\n`;
        failTextContent += '============================================================\n';
    });

    // 실패한 계정 텍스트 파일 저장
    const failTextPath = path.join(screenshotDir, 'harim_account_fail.json');
    fs.writeFileSync(failTextPath, failTextContent, 'utf-8');

    // 파싱하여 분석
    const accounts = parseFailAccountsFromText(failTextContent);
    
    const withNavigatedTo = accounts.filter(acc => acc.hasNavigatedTo);
    const withoutNavigatedTo = accounts.filter(acc => !acc.hasNavigatedTo);
    
    console.log('\n' + '='.repeat(80));
    console.log('실패한 계정 분석 결과');
    console.log('='.repeat(80));
    console.log(`\n총 실패한 계정 수: ${accounts.length}`);
    console.log(`"navigated to" 로그가 있는 계정: ${withNavigatedTo.length}개`);
    console.log(`"navigated to" 로그가 없는 계정: ${withoutNavigatedTo.length}개`);
    
    if (withNavigatedTo.length > 0) {
        console.log('\n' + '='.repeat(80));
        console.log('"navigated to" 로그가 있는 계정 목록');
        console.log('='.repeat(80));
        withNavigatedTo.forEach((acc, index) => {
            console.log(`${index + 1}. ${acc.account}`);
            console.log(`   에러: ${acc.errorMessage}`);
            // navigated to URL 추출
            const navigatedMatches = acc.logContent.match(/navigated to "([^"]+)"/g);
            if (navigatedMatches) {
                const urls = navigatedMatches.map(m => m.match(/"([^"]+)"/)[1]);
                const uniqueUrls = [...new Set(urls)];
                console.log(`   이동한 URL: ${uniqueUrls.join(', ')}`);
            }
            console.log('');
        });
    }
    
    if (withoutNavigatedTo.length > 0) {
        console.log('\n' + '='.repeat(80));
        console.log('"navigated to" 로그가 없는 계정 목록');
        console.log('='.repeat(80));
        withoutNavigatedTo.forEach((acc, index) => {
            console.log(`${index + 1}. ${acc.account}`);
            console.log(`   에러: ${acc.errorMessage}`);
            console.log('');
        });
    }
    
    // JSON 파일로 저장
    const result = {
        total: accounts.length,
        withNavigatedTo: {
            count: withNavigatedTo.length,
            accounts: withNavigatedTo.map(acc => ({
                account: acc.account,
                errorMessage: acc.errorMessage,
                navigatedUrls: acc.logContent.match(/navigated to "([^"]+)"/g)?.map(m => m.match(/"([^"]+)"/)[1]) || []
            }))
        },
        withoutNavigatedTo: {
            count: withoutNavigatedTo.length,
            accounts: withoutNavigatedTo.map(acc => ({
                account: acc.account,
                errorMessage: acc.errorMessage
            }))
        }
    };
    
    const analyzedPath = path.join(screenshotDir, `analyzed_fail_accounts_${getFormattedTimestamp().replace(/:/g, '_')}.json`);
    fs.writeFileSync(analyzedPath, JSON.stringify(result, null, 2), 'utf-8');
    console.log(`\n분석 결과가 저장되었습니다: ${analyzedPath}`);
    
    return result;
}

// 메인 테스트 함수
async function testAllAccounts() {
    const accountData = loadAccountData();
    const accounts = accountData.accounts;
    const baseUrl = BASE_URL;

    console.log(`총 ${accounts.length}개의 계정에 대해 테스트를 시작합니다.`);
    console.log(`Base URL: ${baseUrl}\n`);

    const screenshotDir = ensureScreenshotDir();
    const results = {
        total: accounts.length,
        success: 0,
        failed: 0,
        details: []
    };

    const browser = await chromium.launch({ 
        headless: false, // 브라우저 창 표시
        slowMo: 100 // 동작을 천천히 (디버깅용)
    });

    try {
        for (let i = 0; i < accounts.length; i++) {
            const account = accounts[i];
            const accountId = account.id;
            const accountPw = account.pw;
            
            console.log(`\n[${i + 1}/${accounts.length}] 계정 테스트: ${accountId}`);

            const context = await browser.newContext();
            const page = await context.newPage();

            try {
                const timestamp = getFormattedTimestamp().replace(/:/g, '_');
                const safeAccountId = accountId.replace(/[@.]/g, '_');

                // 로그인 테스트
                console.log(`  → 로그인 시도 중...`);
                const loginResult = await loginWithAccount(page, accountId, accountPw, baseUrl);
                
                // 로그인 후 스크린샷
                const loginScreenshotPath = path.join(screenshotDir, `${safeAccountId}_${timestamp}_login.png`);
                await page.screenshot({ path: loginScreenshotPath, fullPage: true });
                console.log(`  → 스크린샷 저장: ${loginScreenshotPath}`);

                if (loginResult.success) {
                    console.log(`  ✓ 로그인 성공`);
                    results.success++;

                    // 로그아웃 테스트
                    console.log(`  → 로그아웃 시도 중...`);
                    const logoutResult = await logoutAccount(page, baseUrl);
                    
                    // 로그아웃 후 스크린샷
                    const logoutScreenshotPath = path.join(screenshotDir, `${safeAccountId}_${timestamp}_logout.png`);
                    await page.screenshot({ path: logoutScreenshotPath, fullPage: true });
                    console.log(`  → 스크린샷 저장: ${logoutScreenshotPath}`);

                    if (logoutResult.success) {
                        console.log(`  ✓ 로그아웃 성공`);
                    } else {
                        console.log(`  ✗ 로그아웃 실패: ${logoutResult.message}`);
                    }

                    results.details.push({
                        account: accountId,
                        login: loginResult,
                        logout: logoutResult,
                        status: 'success'
                    });
                } else {
                    console.log(`  ✗ 로그인 실패: ${loginResult.message}`);
                    results.failed++;
                    results.details.push({
                        account: accountId,
                        login: loginResult,
                        logout: null,
                        status: 'failed'
                    });
                }

            } catch (error) {
                console.error(`  ✗ 오류 발생: ${error.message}`);
                results.failed++;
                results.details.push({
                    account: accountId,
                    login: { success: false, message: error.message },
                    logout: null,
                    status: 'error'
                });
            } finally {
                await context.close();
                // 다음 계정 테스트 전 잠시 대기
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    } finally {
        await browser.close();
    }

    // 결과 요약 출력
    console.log('\n' + '='.repeat(60));
    console.log('테스트 결과 요약');
    console.log('='.repeat(60));
    console.log(`총 계정 수: ${results.total}`);
    console.log(`성공: ${results.success}`);
    console.log(`실패: ${results.failed}`);
    console.log(`성공률: ${((results.success / results.total) * 100).toFixed(2)}%`);
    console.log('='.repeat(60));

    // 실패한 계정 목록 출력
    const failedAccounts = results.details.filter(d => d.status === 'failed' || d.status === 'error');
    if (failedAccounts.length > 0) {
        console.log('\n실패한 계정 목록:');
        failedAccounts.forEach(detail => {
            console.log(`  - ${detail.account}: ${detail.login.message}`);
        });
    }

    // 결과를 JSON 파일로 저장
    const resultPath = path.join(screenshotDir, `test_results_${getFormattedTimestamp().replace(/:/g, '_')}.json`);
    fs.writeFileSync(resultPath, JSON.stringify(results, null, 2), 'utf-8');
    console.log(`\n상세 결과가 저장되었습니다: ${resultPath}`);

    // 실패한 계정 분석 실행
    if (failedAccounts.length > 0) {
        analyzeFailAccounts(failedAccounts, screenshotDir);
    }

    return results;
}

// 스크립트 실행
const args = process.argv.slice(2);
const command = args[0];

if (command === 'analyze') {
    // 분석만 실행하는 모드
    const screenshotDir = ensureScreenshotDir();
    const failFilePath = path.join(screenshotDir, 'harim_account_fail.json');
    
    if (!fs.existsSync(failFilePath)) {
        console.error(`실패한 계정 파일을 찾을 수 없습니다: ${failFilePath}`);
        console.log('먼저 테스트를 실행해주세요.');
        process.exit(1);
    }
    
    const failTextContent = fs.readFileSync(failFilePath, 'utf-8');
    const accounts = parseFailAccountsFromText(failTextContent);
    analyzeFailAccounts(accounts.map(acc => ({
        account: acc.account,
        login: { success: false, message: acc.errorMessage },
        status: acc.hasNavigatedTo ? 'failed' : 'error'
    })), screenshotDir);
} else {
    // 기본 모드: 테스트 실행
    testAllAccounts()
        .then(() => {
            console.log('\n테스트가 완료되었습니다.');
            process.exit(0);
        })
        .catch((error) => {
            console.error('\n테스트 실행 중 오류 발생:', error);
            process.exit(1);
        });
}
