/**
    whiskey.business.lfdev.io에 접속
    CS-233.clm_id.json에 있는 계정으로 로그인
    CS-233.clm_id.json에 있는 clm_id로 계약서 상세 페이지로 이동
    계약서 상세 페이지에서 계약서 상세 정보를 출력
    [미리보기], [다운로드], [전자서명] 확인
    확인 내용 스크린샷 저장
**/


import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getFormattedTimestamp } from "../../Base_Code/business/common/utils.js";
import { SELECTORS } from '../../Base_Code/business/URL/config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 기본 URL 설정 (환경변수 또는 기본값 사용)
const BASE_URL = process.env.BASE_URL || 'https://whiskey.business.lfdev.io';

console.log(`Base URL: ${BASE_URL}`);

function loadAccountData() {
    const jsonPath = path.join(__dirname, 'CS-233.clm_id.json');
    const fileContent = fs.readFileSync(jsonPath, 'utf-8');
    return JSON.parse(fileContent);
}

async function loginWithAccount(page, email, password, baseUrl, password2) {
    try {
        await page.goto(baseUrl, { waitUntil: 'networkidle' });
        console.log(password2);
        await page.waitForSelector(SELECTORS.VERCEL.PASSWORD, { timeout: 1000 });
        await page.fill(SELECTORS.VERCEL.PASSWORD, password2);
        await page.click(SELECTORS.VERCEL.SUBMIT);
        // 비밀번호 입력 필드가 없거나 오류가 발생해도 계속 진행
        console.log('비밀번호 입력 필드가 없거나 처리 중 오류:', error.message);

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

function ensureScreenshotDir() {
    const screenshotDir = path.join(__dirname, '..', 'screenshots', 'CS-233');
    if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir, { recursive: true });
    }
    return screenshotDir;
}

async function navigateToContractDetail(page, baseUrl, clmId) {
    // 계약서 상세 페이지 URL 패턴 시도 (여러 패턴 지원)
    const urlPatterns = [
        `${baseUrl}/clm/${clmId}`
    ];

    let success = false;
    for (const url of urlPatterns) {
        try {
            await page.goto(url, { waitUntil: 'networkidle', timeout: 10000 });
            // 페이지가 성공적으로 로드되었는지 확인 (404가 아닌지)
            const currentUrl = page.url();
            if (!currentUrl.includes('404') && !currentUrl.includes('error')) {
                success = true;
                break;
            }
        } catch (error) {
            // 다음 URL 패턴 시도
            continue;
        }
    }

    if (!success) {
        // 기본 패턴으로 시도
        await page.goto(`${baseUrl}/clm/detail/${clmId}`, { waitUntil: 'networkidle' });
    }
    
    // 페이지 로드 대기
    await page.waitForTimeout(2000);

}

async function getContractDetailInfo(page) {
    try {
        // 계약서 상세 정보 추출 (페이지의 주요 정보 요소들)
        const title = await page.locator('h1, h2, [class*="title"], [class*="header"]').first().textContent().catch(() => 'N/A');
        const detailInfo = {
            url: page.url(),
            title: title || undefined,
        };
        return detailInfo;
    } catch (error) {
        console.error('계약서 상세 정보 추출 실패:', error);
        return { url: page.url(), error: error.message };
    }
}

async function checkActionButtons(page) {
    const buttons = {
        preview: null,
        download: null,
        esign: null
    };

    try {
        // 미리보기 버튼 확인
        const previewSelectors = [
            'button:has-text("미리보기")',
            'button:has-text("Preview")',
            '[alt*="미리보기"]',
            '[alt*="preview"]',
            '//button[contains(text(), "미리보기")]',
            '//button[contains(text(), "Preview")]'
        ];
        
        for (const selector of previewSelectors) {
            try {
                const element = page.locator(selector).first();
                if (await element.count() > 0 && await element.isVisible({ timeout: 1000 }).catch(() => false)) {
                    buttons.preview = selector;
                    break;
                }
            } catch (e) {}
        }

        // 다운로드 버튼 확인
        const downloadSelectors = [
            'button:has-text("다운로드")',
            'button:has-text("Download")',
            '[alt*="다운로드"]',
            '[alt*="download"]',
            '//button[contains(text(), "다운로드")]',
            '//button[contains(text(), "Download")]'
        ];
        
        for (const selector of downloadSelectors) {
            try {
                const element = page.locator(selector).first();
                if (await element.count() > 0 && await element.isVisible({ timeout: 1000 }).catch(() => false)) {
                    buttons.download = selector;
                    break;
                }
            } catch (e) {}
        }

        // 전자서명 확인 (계약명 클릭 방식 - 특정 영역 안에서 클릭 가능한 요소 찾기)
        try {
            // 전자서명 영역 (계약명이 있는 영역)
            const esignArea = page.locator('//*[@id="__next"]/div[1]/div[3]/div[2]/main/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/table/tbody/tr[8]/td/div');
            
            if (await esignArea.count() > 0 && await esignArea.isVisible({ timeout: 2000 }).catch(() => false)) {
                // 해당 영역 안에서 클릭 가능한 요소 찾기 (계약명 링크)
                const clickableSelectors = [
                    'a',
                    'div[class*="cursor-pointer"]',
                    'div[class*="clickable"]',
                    'span[class*="cursor-pointer"]',
                    'button',
                    '*[onclick]'
                ];
                
                for (const selector of clickableSelectors) {
                    try {
                        const element = esignArea.locator(selector).first();
                        if (await element.count() > 0 && await element.isVisible({ timeout: 1000 }).catch(() => false)) {
                            const text = await element.textContent().catch(() => '');
                            // 계약명이 있는 클릭 가능한 요소 확인
                            if (text && text.trim().length > 0) {
                                buttons.esign = `계약명 클릭 가능: "${text.trim()}"`;
                                break;
                            }
                        }
                    } catch (e) {}
                }
                
                // 클릭 가능한 요소를 찾지 못했지만 영역이 존재하면 존재한다고 표시
                if (!buttons.esign) {
                    const areaText = await esignArea.textContent().catch(() => '');
                    if (areaText && areaText.trim().length > 0) {
                        buttons.esign = `영역 존재 (계약명: "${areaText.trim()}")`;
                    } else {
                        buttons.esign = '영역 존재 (클릭 가능 요소 확인 필요)';
                    }
                }
            }
        } catch (e) {
            // 영역을 찾지 못한 경우
            buttons.esign = null;
        }
    } catch (error) {
        console.error('버튼 확인 중 오류:', error);
    }

    return buttons;
}

async function main() {
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        // 계정 데이터 로드
        const data = loadAccountData();
        const account = data.account[0];
        const vercel = data.vercel[0];
        const clmIds = data.clm_id;

        console.log(`로그인 계정: ${account.id}`);
        console.log(`vercel password: ${vercel.pw2}`)
        console.log(`확인할 계약서 수: ${clmIds.length}`);

        // 로그인
        const loginResult = await loginWithAccount(page, account.id, account.pw, BASE_URL, vercel.pw2);
        if (!loginResult.success) {
            console.error(loginResult.message);
            return;
        }
        console.log('로그인 성공');

        // 스크린샷 디렉토리 생성
        const screenshotDir = ensureScreenshotDir();

        // 각 clm_id에 대해 테스트 수행
        for (let i = 0; i < clmIds.length; i++) {
            const clmId = clmIds[i];
            const timestamp = getFormattedTimestamp().replace(/:/g, '_');
            
            console.log(`\n[${i + 1}/${clmIds.length}] 계약서 ID: ${clmId} 처리 중...`);

            try {
                // 계약서 상세 페이지로 이동
                await navigateToContractDetail(page, BASE_URL, clmId);
                
                // 페이지 로드 대기
                await page.waitForTimeout(3000);

                // 계약서 상세 정보 출력
                const detailInfo = await getContractDetailInfo(page);
                console.log(`계약서 상세 정보:`);
                console.log(`  URL: ${detailInfo.url}`);
                if ('title' in detailInfo) {
                    console.log(`  제목: ${detailInfo.title || 'N/A'}`);
                } else {
                    console.log(`  오류: ${detailInfo.error || 'N/A'}`);
                }

                // 액션 버튼 확인
                const buttons = await checkActionButtons(page);
                console.log(`버튼 확인 결과:`);
                console.log(`  미리보기: ${buttons.preview ? '✓ 발견' : '✗ 없음'}`);
                console.log(`  다운로드: ${buttons.download ? '✓ 발견' : '✗ 없음'}`);
                console.log(`  전자서명: ${buttons.esign ? '✓ 발견' : '✗ 없음'}`);

                // 스크린샷 저장
                const screenshotPath = path.join(screenshotDir, `${timestamp}_clm_${clmId}_detail.png`);
                await page.screenshot({ path: screenshotPath, fullPage: true });
                console.log(`스크린샷 저장: ${screenshotPath}`);

            } catch (error) {
                console.error(`계약서 ID ${clmId} 처리 중 오류:`, error.message);
                const errorScreenshotPath = path.join(screenshotDir, `${timestamp}_clm_${clmId}_error.png`);
                await page.screenshot({ path: errorScreenshotPath }).catch(() => {});
            }
        }

        console.log('\n모든 테스트 완료');

    } catch (error) {
        console.error('테스트 실행 중 오류:', error);
    } finally {
        await browser.close();
    }
}

// 테스트 실행
main().catch(console.error);