import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getFormattedTimestamp } from "../Base_Code/business/common/utils.js";
import { SELECTORS } from '../Base_Code/business/URL/config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 기본 URL 설정 (환경변수 또는 기본값 사용)
const BASE_URL = process.env.BASE_URL || 'https://harim.business.lawform.io';

console.log(`Base URL: ${BASE_URL}`);

// 로그인 정보
const LOGIN_EMAIL = 'developer+id20251002103114449_m@amicuslex.net';
const LOGIN_PASSWORD = '1q2w#E$R';

// 스크린샷 저장 디렉토리 생성
function ensureScreenshotDir() {
    const screenshotDir = path.join(__dirname, '..', 'screenshots', 'harim_contract_check');
    if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir, { recursive: true });
    }
    return screenshotDir;
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

// 체결 계약서 조회 메뉴로 이동
async function navigateToContractList(page, baseUrl) {
    try {
        // GNB 메뉴 열기 (필요한 경우)
        try {
            const gnbButton = page.locator(SELECTORS.DASHBOARD.GNB);
            if (await gnbButton.isVisible({ timeout: 3000 })) {
                await gnbButton.click();
                await page.waitForTimeout(1000);
            }
        } catch (e) {
            // GNB 버튼이 없거나 이미 열려있을 수 있음
        }

        // 체결 계약서 조회 메뉴 클릭
        await page.waitForSelector(SELECTORS.GNB.CLM_COMPLETE, { timeout: 15000 });
        await page.click(SELECTORS.GNB.CLM_COMPLETE);
        
        // 페이지 로드 대기
        await page.waitForURL(`${baseUrl}/clm/complete`, { timeout: 30000 });
        await page.waitForTimeout(2000);
        
        return { success: true, message: '체결 계약서 조회 페이지로 이동 성공' };
    } catch (error) {
        return { success: false, message: `체결 계약서 조회 페이지 이동 실패: ${error.message}` };
    }
}

// 계약명 목록 가져오기
async function getContractNames(page) {
    try {
        // 페이지 로드 대기
        await page.waitForTimeout(2000);
        
        // 계약명이 있는 요소 찾기 (여러 패턴 시도)
        const contractSelectors = [
            '//table//tbody//tr//td[contains(@class, "cursor-pointer")]',
            '//div[contains(@class, "contract")]//a',
            '//div[contains(@class, "contract-name")]',
            '//table//tbody//tr//td[2]//a',
            '//table//tbody//tr//td[2]//div[contains(@class, "cursor-pointer")]',
            '//tbody//tr//td[2]//*[contains(@class, "cursor-pointer")]',
            '//tbody//tr//td[2]//*[text()]'
        ];

        const contractNames = [];
        
        for (const selector of contractSelectors) {
            try {
                const elements = page.locator(selector);
                const count = await elements.count();
                
                if (count > 0) {
                    for (let i = 0; i < count; i++) {
                        const element = elements.nth(i);
                        if (await element.isVisible({ timeout: 1000 }).catch(() => false)) {
                            const text = await element.textContent().catch(() => '');
                            if (text && text.trim().length > 0) {
                                const contractName = text.trim();
                                // 중복 제거
                                if (!contractNames.find(c => c.name === contractName)) {
                                    contractNames.push({
                                        name: contractName,
                                        selector: selector,
                                        index: i
                                    });
                                }
                            }
                        }
                    }
                    
                    if (contractNames.length > 0) {
                        break; // 요소를 찾았으면 중단
                    }
                }
            } catch (e) {
                continue;
            }
        }

        // 테이블의 모든 행에서 계약명 추출 시도
        if (contractNames.length === 0) {
            try {
                const rows = page.locator('//table//tbody//tr');
                const rowCount = await rows.count();
                
                for (let i = 0; i < rowCount; i++) {
                    const row = rows.nth(i);
                    // 두 번째 열(계약명)에서 텍스트 추출
                    const contractCell = row.locator('td').nth(1);
                    if (await contractCell.isVisible({ timeout: 1000 }).catch(() => false)) {
                        const text = await contractCell.textContent().catch(() => '');
                        if (text && text.trim().length > 0) {
                            const contractName = text.trim();
                            if (!contractNames.find(c => c.name === contractName)) {
                                contractNames.push({
                                    name: contractName,
                                    selector: `//table//tbody//tr[${i + 1}]//td[2]`,
                                    index: i
                                });
                            }
                        }
                    }
                }
            } catch (e) {
                console.log('테이블에서 계약명 추출 실패:', e.message);
            }
        }

        return contractNames;
    } catch (error) {
        console.error('계약명 목록 가져오기 실패:', error);
        return [];
    }
}

// 계약명 클릭하여 상세 페이지로 이동
async function clickContractName(page, contractName, index) {
    try {
        // 여러 방법으로 계약명 클릭 시도
        const clickSelectors = [
            `//table//tbody//tr[${index + 1}]//td[2]//*[contains(@class, "cursor-pointer")]`,
            `//table//tbody//tr[${index + 1}]//td[2]//a`,
            `//table//tbody//tr[${index + 1}]//td[2]`,
            `//table//tbody//tr[${index + 1}]`,
            `//*[contains(text(), "${contractName}")]//ancestor::tr//td[2]//*[contains(@class, "cursor-pointer")]`,
            `//*[contains(text(), "${contractName}")]//ancestor::tr//td[2]`
        ];

        let clicked = false;
        for (const selector of clickSelectors) {
            try {
                const element = page.locator(selector).first();
                if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
                    await element.click();
                    await page.waitForTimeout(2000);
                    // URL이 변경되었는지 확인
                    const currentUrl = page.url();
                    if (currentUrl.includes('/clm/') && !currentUrl.includes('/complete')) {
                        clicked = true;
                        break;
                    }
                }
            } catch (e) {
                continue;
            }
        }

        if (!clicked) {
            // 직접 텍스트로 찾아서 클릭
            try {
                const contractLink = page.locator(`text="${contractName}"`).first();
                if (await contractLink.isVisible({ timeout: 2000 }).catch(() => false)) {
                    await contractLink.click();
                    await page.waitForTimeout(2000);
                    clicked = true;
                }
            } catch (e) {
                // 마지막 시도: 부모 요소 클릭
                try {
                    const contractLink = page.locator(`text="${contractName}"`).first();
                    const parent = contractLink.locator('..');
                    if (await parent.isVisible({ timeout: 2000 }).catch(() => false)) {
                        await parent.click();
                        await page.waitForTimeout(2000);
                        clicked = true;
                    }
                } catch (e2) {
                    console.log(`계약명 "${contractName}" 클릭 실패`);
                }
            }
        }

        return clicked;
    } catch (error) {
        console.error(`계약명 "${contractName}" 클릭 중 오류:`, error.message);
        return false;
    }
}

// 계약서 상세 페이지에서 관리번호와 요청 기업 정보 추출
async function extractContractInfo(page) {
    const info = {
        managementNumber: '',
        requestCompany: ''
    };

    try {
        // 테이블에서 정보 추출 시도
        const tableSelectors = [
            '//table//tbody//tr',
            '//table//tr',
            '//div[contains(@class, "table")]//tr'
        ];

        for (const selector of tableSelectors) {
            try {
                const rows = page.locator(selector);
                const rowCount = await rows.count();
                
                for (let i = 0; i < rowCount; i++) {
                    const row = rows.nth(i);
                    const cells = row.locator('td, th');
                    const cellCount = await cells.count();
                    
                    for (let j = 0; j < cellCount; j++) {
                        const cell = cells.nth(j);
                        const cellText = await cell.textContent().catch(() => '');
                        const label = cellText.trim();
                        
                        // 관리번호 찾기
                        if ((label.includes('관리번호') || label.includes('관리 번호') || label.includes('번호')) && !info.managementNumber) {
                            const nextCell = cells.nth(j + 1);
                            if (await nextCell.count() > 0) {
                                const value = await nextCell.textContent().catch(() => '');
                                if (value && value.trim().length > 0) {
                                    info.managementNumber = value.trim();
                                }
                            }
                        }
                        
                        // 요청 기업 찾기
                        if ((label.includes('요청 기업') || label.includes('요청기업') || label.includes('계약처') || label.includes('상대방')) && !info.requestCompany) {
                            const nextCell = cells.nth(j + 1);
                            if (await nextCell.count() > 0) {
                                const value = await nextCell.textContent().catch(() => '');
                                if (value && value.trim().length > 0) {
                                    info.requestCompany = value.trim();
                                }
                            }
                        }
                    }
                }
                
                if (info.managementNumber && info.requestCompany) {
                    break;
                }
            } catch (e) {
                continue;
            }
        }

        // 직접 텍스트로 찾기 시도
        if (!info.managementNumber || !info.requestCompany) {
            try {
                const allText = await page.textContent().catch(() => '');
                
                // 관리번호 패턴 찾기 (예: CLM-2024-001, 20240101001 등)
                const mgmtPatterns = [
                    /관리번호[:\s]*([^\n\r]+)/i,
                    /관리 번호[:\s]*([^\n\r]+)/i,
                    /번호[:\s]*([A-Z0-9\-]+)/i
                ];
                
                for (const pattern of mgmtPatterns) {
                    const match = allText.match(pattern);
                    if (match && match[1] && !info.managementNumber) {
                        info.managementNumber = match[1].trim();
                        break;
                    }
                }
                
                // 요청 기업 패턴 찾기
                const companyPatterns = [
                    /요청 기업[:\s]*([^\n\r]+)/i,
                    /요청기업[:\s]*([^\n\r]+)/i,
                    /계약처[:\s]*([^\n\r]+)/i,
                    /상대방[:\s]*([^\n\r]+)/i
                ];
                
                for (const pattern of companyPatterns) {
                    const match = allText.match(pattern);
                    if (match && match[1] && !info.requestCompany) {
                        info.requestCompany = match[1].trim();
                        break;
                    }
                }
            } catch (e) {
                // 텍스트 추출 실패
            }
        }

        // URL에서 관리번호 추출 시도 (예: /clm/12345)
        if (!info.managementNumber) {
            try {
                const url = page.url();
                const urlMatch = url.match(/\/clm\/([^\/\?]+)/);
                if (urlMatch && urlMatch[1]) {
                    info.managementNumber = urlMatch[1];
                }
            } catch (e) {}
        }

    } catch (error) {
        console.error('계약서 정보 추출 중 오류:', error);
    }

    return info;
}

// 계약서 상세 페이지에서 문서 확인
async function checkDocuments(page) {
    const result = {
        contractDocument: false,
        attachments: false,
        supplements: false,
        details: {}
    };

    try {
        // 페이지 로드 대기
        await page.waitForTimeout(3000);

        // 비밀번호 입력 필드가 있는지 확인하고 입력
        try {
            const passwordInput = page.locator('//*[@id="bottom-section"]/form/div/input');
            if (await passwordInput.count() > 0 && await passwordInput.isVisible({ timeout: 3000 }).catch(() => false)) {
                await passwordInput.fill('dkalzntmfprtm');
                const submitButton = page.locator('//*[@id="bottom-section"]/form//button[@type="submit"], //*[@id="bottom-section"]/form//button[contains(text(), "확인")], //*[@id="bottom-section"]/form//button[contains(text(), "제출")]').first();
                if (await submitButton.count() > 0 && await submitButton.isVisible({ timeout: 1000 }).catch(() => false)) {
                    await submitButton.click();
                    await page.waitForTimeout(2000);
                }
            }
        } catch (error) {
            // 비밀번호 입력 필드가 없거나 오류가 발생해도 계속 진행
        }

        // 계약서 문서 확인 (다운로드 버튼, 미리보기 버튼 등)
        const documentSelectors = [
            'button:has-text("다운로드")',
            'button:has-text("미리보기")',
            'button:has-text("Download")',
            'button:has-text("Preview")',
            '[alt*="다운로드"]',
            '[alt*="미리보기"]',
            '//button[contains(text(), "다운로드")]',
            '//button[contains(text(), "미리보기")]'
        ];

        for (const selector of documentSelectors) {
            try {
                const element = page.locator(selector).first();
                if (await element.count() > 0 && await element.isVisible({ timeout: 1000 }).catch(() => false)) {
                    result.contractDocument = true;
                    result.details.contractDocumentSelector = selector;
                    break;
                }
            } catch (e) {}
        }

        // 첨부 문서 확인
        const attachmentSelectors = [
            '//*[contains(text(), "첨부")]',
            '//*[contains(text(), "첨부파일")]',
            '//*[contains(text(), "Attachment")]',
            '//div[contains(@class, "attachment")]',
            '//div[contains(@class, "file-list")]',
            '//*[contains(text(), "첨부")]//following-sibling::*//a',
            '//*[contains(text(), "첨부")]//following-sibling::*//button'
        ];

        for (const selector of attachmentSelectors) {
            try {
                const elements = page.locator(selector);
                const count = await elements.count();
                if (count > 0) {
                    // 첨부 파일이 실제로 있는지 확인 (다운로드 가능한 링크나 버튼)
                    for (let i = 0; i < count; i++) {
                        const element = elements.nth(i);
                        if (await element.isVisible({ timeout: 1000 }).catch(() => false)) {
                            const text = await element.textContent().catch(() => '');
                            const href = await element.getAttribute('href').catch(() => '');
                            const onClick = await element.getAttribute('onclick').catch(() => '');
                            
                            if (text && text.trim().length > 0 && (href || onClick || text.includes('다운로드') || text.includes('파일'))) {
                                result.attachments = true;
                                result.details.attachmentCount = count;
                                break;
                            }
                        }
                    }
                    if (result.attachments) break;
                }
            } catch (e) {}
        }

        // 별첨 문서 확인
        const supplementSelectors = [
            '//*[contains(text(), "별첨")]',
            '//*[contains(text(), "별첨서류")]',
            '//*[contains(text(), "Supplement")]',
            '//div[contains(@class, "supplement")]',
            '//*[contains(text(), "별첨")]//following-sibling::*//a',
            '//*[contains(text(), "별첨")]//following-sibling::*//button'
        ];

        for (const selector of supplementSelectors) {
            try {
                const elements = page.locator(selector);
                const count = await elements.count();
                if (count > 0) {
                    // 별첨 파일이 실제로 있는지 확인
                    for (let i = 0; i < count; i++) {
                        const element = elements.nth(i);
                        if (await element.isVisible({ timeout: 1000 }).catch(() => false)) {
                            const text = await element.textContent().catch(() => '');
                            const href = await element.getAttribute('href').catch(() => '');
                            const onClick = await element.getAttribute('onclick').catch(() => '');
                            
                            if (text && text.trim().length > 0 && (href || onClick || text.includes('다운로드') || text.includes('파일'))) {
                                result.supplements = true;
                                result.details.supplementCount = count;
                                break;
                            }
                        }
                    }
                    if (result.supplements) break;
                }
            } catch (e) {}
        }

        // 페이지 전체에서 파일 관련 요소 확인
        if (!result.attachments && !result.supplements) {
            try {
                const fileElements = page.locator('//a[contains(@href, "/download")], //a[contains(@href, "/file")], //button[contains(@onclick, "download")], //button[contains(@onclick, "file")]');
                const fileCount = await fileElements.count();
                if (fileCount > 0) {
                    result.attachments = true;
                    result.details.fileElementCount = fileCount;
                }
            } catch (e) {}
        }

    } catch (error) {
        console.error('문서 확인 중 오류:', error);
        result.error = error.message;
    }

    return result;
}

// CSV 파일로 결과 저장 (요청 기업별로 분리)
async function saveResultsToCSV(results, screenshotDir) {
    try {
        // 요청 기업별로 데이터 그룹화
        const companyGroups = {};
        
        results.details.forEach(detail => {
            const company = detail.requestCompany || '기업명 없음';
            if (!companyGroups[company]) {
                companyGroups[company] = [];
            }
            companyGroups[company].push(detail);
        });

        const timestamp = getFormattedTimestamp().replace(/:/g, '_');
        
        // 각 요청 기업별로 CSV 파일 생성
        for (const [companyName, details] of Object.entries(companyGroups)) {
            // 파일명에서 특수문자 제거
            const safeCompanyName = companyName.replace(/[<>:"/\\|?*]/g, '_').trim();
            const csvFileName = `${safeCompanyName}_${timestamp}.csv`;
            const csvPath = path.join(screenshotDir, csvFileName);

            // CSV 헤더
            const headers = ['관리번호', '계약서 여부', '첨부/별첨 여부'];
            const csvRows = [headers.join(',')];

            // 데이터 행 추가
            details.forEach(detail => {
                const managementNumber = detail.managementNumber || '';
                const hasContract = detail.documentCheck?.contractDocument ? '있음' : '없음';
                const hasAttachment = (detail.documentCheck?.attachments || detail.documentCheck?.supplements) ? '있음' : '없음';
                
                // CSV 값에 쉼표나 따옴표가 있으면 따옴표로 감싸고 내부 따옴표는 이스케이프
                const escapeCSV = (value) => {
                    if (value.includes(',') || value.includes('"') || value.includes('\n')) {
                        return `"${value.replace(/"/g, '""')}"`;
                    }
                    return value;
                };

                csvRows.push([
                    escapeCSV(managementNumber),
                    escapeCSV(hasContract),
                    escapeCSV(hasAttachment)
                ].join(','));
            });

            // CSV 파일 저장
            const csvContent = csvRows.join('\n');
            fs.writeFileSync(csvPath, '\uFEFF' + csvContent, 'utf-8'); // BOM 추가로 Excel에서 한글 깨짐 방지
            
            console.log(`\nCSV 파일 저장: ${csvFileName} (${details.length}건)`);
        }

        console.log(`\n총 ${Object.keys(companyGroups).length}개의 요청 기업별 CSV 파일이 생성되었습니다.`);

    } catch (error) {
        console.error('CSV 파일 저장 중 오류:', error);
    }
}

// 메인 함수
async function main() {
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 100
    });
    const context = await browser.newContext();
    const page = await context.newPage();

    const screenshotDir = ensureScreenshotDir();
    const results = {
        total: 0,
        checked: 0,
        success: 0,
        failed: 0,
        details: []
    };

    try {
        console.log('로그인 중...');
        const loginResult = await loginWithAccount(page, LOGIN_EMAIL, LOGIN_PASSWORD, BASE_URL);
        
        if (!loginResult.success) {
            console.error('로그인 실패:', loginResult.message);
            return;
        }
        console.log('로그인 성공');

        // 로그인 후 스크린샷
        const loginScreenshotPath = path.join(screenshotDir, `login_${getFormattedTimestamp().replace(/:/g, '_')}.png`);
        await page.screenshot({ path: loginScreenshotPath, fullPage: true });
        console.log(`로그인 스크린샷 저장: ${loginScreenshotPath}`);

        // 체결 계약서 조회 메뉴로 이동
        console.log('\n체결 계약서 조회 메뉴로 이동 중...');
        const navigateResult = await navigateToContractList(page, BASE_URL);
        
        if (!navigateResult.success) {
            console.error('체결 계약서 조회 페이지 이동 실패:', navigateResult.message);
            return;
        }
        console.log('체결 계약서 조회 페이지로 이동 성공');

        // 계약서 목록 페이지 스크린샷
        const listScreenshotPath = path.join(screenshotDir, `contract_list_${getFormattedTimestamp().replace(/:/g, '_')}.png`);
        await page.screenshot({ path: listScreenshotPath, fullPage: true });
        console.log(`계약서 목록 스크린샷 저장: ${listScreenshotPath}`);

        // 계약명 목록 가져오기
        console.log('\n계약명 목록 가져오는 중...');
        const contractNames = await getContractNames(page);
        console.log(`총 ${contractNames.length}개의 계약서를 찾았습니다.`);

        if (contractNames.length === 0) {
            console.log('계약서를 찾을 수 없습니다.');
            return;
        }

        results.total = contractNames.length;

        // 각 계약서에 대해 확인
        for (let i = 0; i < contractNames.length; i++) {
            const contract = contractNames[i];
            const timestamp = getFormattedTimestamp().replace(/:/g, '_');
            
            console.log(`\n[${i + 1}/${contractNames.length}] 계약서 확인: ${contract.name}`);

            try {
                // 계약서 목록 페이지로 돌아가기 (첫 번째가 아니면)
                if (i > 0) {
                    await page.goto(`${BASE_URL}/clm/complete`, { waitUntil: 'networkidle' });
                    await page.waitForTimeout(2000);
                }

                // 계약명 클릭하여 상세 페이지로 이동
                const clicked = await clickContractName(page, contract.name, contract.index);
                
                if (!clicked) {
                    console.log(`  ✗ 계약명 클릭 실패`);
                    results.failed++;
                results.details.push({
                    contractName: contract.name,
                    managementNumber: '',
                    requestCompany: '',
                    status: 'failed',
                    error: '계약명 클릭 실패'
                });
                    continue;
                }

                console.log(`  → 상세 페이지로 이동 성공`);

                // 계약서 정보 추출 (관리번호, 요청 기업)
                const contractInfo = await extractContractInfo(page);
                console.log(`  계약서 정보:`);
                console.log(`    관리번호: ${contractInfo.managementNumber || 'N/A'}`);
                console.log(`    요청 기업: ${contractInfo.requestCompany || 'N/A'}`);

                // 문서 확인
                const documentCheck = await checkDocuments(page);
                results.checked++;

                // 결과 출력
                console.log(`  문서 확인 결과:`);
                console.log(`    계약서 문서: ${documentCheck.contractDocument ? '✓ 있음' : '✗ 없음'}`);
                console.log(`    첨부 문서: ${documentCheck.attachments ? '✓ 있음' : '✗ 없음'}`);
                console.log(`    별첨 문서: ${documentCheck.supplements ? '✓ 있음' : '✗ 없음'}`);

                // 스크린샷 저장
                const detailScreenshotPath = path.join(screenshotDir, `${timestamp}_${contract.name.replace(/[^a-zA-Z0-9가-힣]/g, '_')}_detail.png`);
                await page.screenshot({ path: detailScreenshotPath, fullPage: true });
                console.log(`  스크린샷 저장: ${detailScreenshotPath}`);

                // 결과 저장
                const hasDocuments = documentCheck.contractDocument || documentCheck.attachments || documentCheck.supplements;
                if (hasDocuments) {
                    results.success++;
                } else {
                    results.failed++;
                }

                results.details.push({
                    contractName: contract.name,
                    managementNumber: contractInfo.managementNumber || '',
                    requestCompany: contractInfo.requestCompany || '',
                    status: hasDocuments ? 'success' : 'no_documents',
                    documentCheck: documentCheck
                });

            } catch (error) {
                console.error(`  ✗ 오류 발생: ${error.message}`);
                results.failed++;
                results.details.push({
                    contractName: contract.name,
                    managementNumber: '',
                    requestCompany: '',
                    status: 'error',
                    error: error.message
                });
            }
        }

        // 결과 요약 출력
        console.log('\n' + '='.repeat(60));
        console.log('테스트 결과 요약');
        console.log('='.repeat(60));
        console.log(`총 계약서 수: ${results.total}`);
        console.log(`확인 완료: ${results.checked}`);
        console.log(`문서 있음: ${results.success}`);
        console.log(`문서 없음/실패: ${results.failed}`);
        console.log('='.repeat(60));

        // 결과를 JSON 파일로 저장
        const resultPath = path.join(screenshotDir, `test_results_${getFormattedTimestamp().replace(/:/g, '_')}.json`);
        fs.writeFileSync(resultPath, JSON.stringify(results, null, 2), 'utf-8');
        console.log(`\n상세 결과가 저장되었습니다: ${resultPath}`);

        // CSV 파일로 저장 (요청 기업별로 분리)
        await saveResultsToCSV(results, screenshotDir);

    } catch (error) {
        console.error('테스트 실행 중 오류:', error);
    } finally {
        await browser.close();
    }
}

// 스크립트 실행
main().catch(console.error);
