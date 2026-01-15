/*
[사전 조건]
1. 요청자 계정
2. 마스터 계정

[이슈 재현과정]
1. 요청자 계정으로 로그인
2. 요청자 계정으로 계약 검토 요청 : Option -> 편집기 사용 여부 : 사용(true)
3. 생성된 계약 검토 URL 복사 : https://alpha.business.lfdev.io/clm/{계약 검토 요청 번호}
4. 마스터 계정으로 로그인
5. 3에서 복사된 계약 검토 URL 접속
6. 편집기 사용 여부 변경 : 사용(true) -> 사용 안함(false)
7. 마스터 계정으로 계약서 변경
8. 마스터 계정으로 법무 검토 담당자 배정 시도

[이슈 현상]
법무 검토 담당자 지정 시 Serializer Null 오류 발생

[기대 결과]
법무 검토 담당자 배정이 가능해야함
*/

import { getFormattedTimestamp } from "../../Base_Code/business/common/utils.js";
import { loadAccountEnv } from "../../Account/Account_env.js";

const DEFAULT_ACCOUNT_KEY = "blue";
const DEFAULT_ENV = "DEV";
const WAIT_OPTIONS = { waitUntil: "networkidle" };

function getNewTimestamp() {
    return getFormattedTimestamp().replace(/:/g, "_");
}

async function loginWithCredentials(page, baseUrl, email, password) {
    await page.goto(baseUrl, WAIT_OPTIONS);
    await page.goto(`${baseUrl}/login`, WAIT_OPTIONS);

    await page.waitForSelector('input[type="email"]', { timeout: 15000 });
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');

    await page.waitForURL(`${baseUrl}/dashboard`, { timeout: 30000 });
}

async function selectFirstContractFromLibrary(page, timestamp) {
    await page.waitForSelector('//label[.//div[text()="My계약서에서 불러오기"]]', { timeout: 15000 });
    await page.locator('//label[.//div[text()="My계약서에서 불러오기"]]').click();
    await page.screenshot({ path: `screenshots/${timestamp}_contract_source.png` });

    await page.waitForSelector('img[alt="불러오기 아이콘"]', { timeout: 15000 });
    await page.locator('img[alt="불러오기 아이콘"]').click();
    await page.waitForSelector('//div[text()="문서 불러오기"]', { timeout: 15000 });
    await page.waitForSelector('(//img[@alt="파일"]/ancestor::div[contains(@class,"cursor-pointer")])[1]', { timeout: 15000 });
    await page.locator('(//img[@alt="파일"]/ancestor::div[contains(@class,"cursor-pointer")])[1]').click();
    await page.screenshot({ path: `screenshots/${timestamp}_contract_selected.png` });
    await page.waitForSelector('//button[text()="선택"]', { timeout: 15000 });
    await page.locator('//button[text()="선택"]').click();

    try {
        await page.waitForSelector('//div[text()="문서 불러오기"]', { state: "hidden", timeout: 15000 });
    } catch (error) {
        console.warn("문서 불러오기 모달이 예상보다 오래 열려 있습니다:", error.message);
    }
}

async function createDraftRequest(page, baseUrl, options = {}) {
    const timestamp = getNewTimestamp();

    await page.goto(`${baseUrl}/clm/draft`, WAIT_OPTIONS);
    await page.screenshot({ path: `screenshots/${timestamp}_draft_page.png` });

    await page.waitForSelector('//button[text()="신규 검토 요청" and not(@disabled)]', { timeout: 20000 });
    await page.locator('//button[text()="신규 검토 요청"]').click();
    await page.waitForSelector('//div[contains(@class,"footer-safe-area")]//button[text()="확인" and not(@disabled)]', { timeout: 15000 });
    await page.locator('//div[contains(@class,"footer-safe-area")]//button[text()="확인"]').click();
    await page.waitForTimeout(500);

    await page.waitForSelector('//label[.//div[text()="신규"]]', { timeout: 15000 });
    await page.locator('//label[.//div[text()="신규"]]').click();

    if (options.useEditor === false) {
        await page.locator('//label[.//div[text()="사용 안 함" or text()="사용 안함"]]').click();
    } else {
        await page.locator('//label[.//div[text()="사용"]]').click();
    }
    await page.screenshot({ path: `screenshots/${timestamp}_editor_option.png` });

    if (options.attachFromLibrary !== false) {
        await selectFirstContractFromLibrary(page, timestamp);
    } else {
        await page.locator('//label[.//div[text()="파일로 첨부하기"]]').click();
        await page.screenshot({ path: `screenshots/${timestamp}_file_upload_selected.png` });
        // 실제 파일 업로드는 환경에 따라 달라질 수 있으므로 별도 구현 필요
    }

    const contractName = options.contractName ?? `자동 생성 계약_${timestamp}`;
    await page.waitForSelector('input[placeholder="계약명을 입력해 주세요"]', { timeout: 15000 });
    await page.fill('input[placeholder="계약명을 입력해 주세요"]', contractName);

    if (options.securityType === "refer") {
        await page.locator('//label[.//div[text()="참조인"]]').click();
    } else if (options.securityType === "private") {
        await page.locator('//label[.//div[text()="비공개"]]').click();
    } else {
        await page.locator('//label[.//div[text()="전체 공개"]]').click();
    }

    if (options.reviewRequired === false) {
        await page.locator('//label[.//div[text()="검토 불필요"]]').click();
    } else {
        await page.locator('//label[.//div[text()="검토 필요"]]').click();
    }

    await page.screenshot({ path: `screenshots/${timestamp}_draft_filled.png` });

    await page.locator('//div[text()="계약서 검토 요청"]').click();
    await page.waitForSelector('//div[contains(@class,"footer-safe-area")]//button[text()="확인" and not(@disabled)]', { timeout: 15000 });
    await page.locator('//div[contains(@class,"footer-safe-area")]//button[text()="확인"]').click();

    await page.waitForURL(/\/clm\/review\//, { timeout: 30000 });
    await page.screenshot({ path: `screenshots/${timestamp}_draft_complete.png` });

    return page.url();
}

async function toggleEditorUsageOnReview(page, enableEditor) {
    const timestamp = getNewTimestamp();
    const targetLabel = enableEditor ? "사용" : "사용 안 함";

    await page.waitForSelector(`//label[.//div[text()="${targetLabel}" or text()="${targetLabel.replace(" ", "")}"]]`, { timeout: 20000 });
    await page.locator(`//label[.//div[text()="${targetLabel}" or text()="${targetLabel.replace(" ", "")}"]]`).click();
    await page.screenshot({ path: `screenshots/${timestamp}_editor_toggle.png` });
}

async function attemptContractUpdate(page) {
    const timestamp = getNewTimestamp();

    try {
        await page.waitForSelector('//button[contains(text(),"계약서 변경")]', { timeout: 10000 });
        await page.locator('//button[contains(text(),"계약서 변경")]').click();
        await page.screenshot({ path: `screenshots/${timestamp}_contract_change_clicked.png` });
    } catch (error) {
        console.warn("계약서 변경 버튼을 찾지 못했습니다:", error.message);
    }
}

async function attemptAssignLegalReviewer(page) {
    const timestamp = getNewTimestamp();

    try {
        await page.waitForSelector('//button[contains(text(),"법무 검토 담당자")]', { timeout: 10000 });
        await page.locator('//button[contains(text(),"법무 검토 담당자")]').click();
        await page.screenshot({ path: `screenshots/${timestamp}_legal_assign_attempt.png` });
    } catch (error) {
        console.warn("법무 검토 담당자 배정 버튼을 찾지 못했습니다:", error.message);
    }
}

export default async function CS_BG_serializer_null(page, options = {}) {
    const accountKey = options.accountKey ?? process.env.ACCOUNT ?? DEFAULT_ACCOUNT_KEY;
    const env = options.env ?? process.env.ENV ?? DEFAULT_ENV;

    try {
        const { baseUrl, fullData } = await loadAccountEnv(accountKey, env, "master");
        const envKey = env.toUpperCase();
        const envData = fullData[envKey];

        if (!envData) {
            throw new Error(`선택한 ENV(${envKey})에 대한 계정 정보를 찾을 수 없습니다.`);
        }

        const requester = envData.user;
        const master = envData.master;

        if (!requester || !master) {
            throw new Error("요청자 또는 마스터 계정 정보가 존재하지 않습니다.");
        }

        await loginWithCredentials(page, baseUrl, requester.id, requester.password);
        const reviewUrl = await createDraftRequest(page, baseUrl, {
            useEditor: true,
            attachFromLibrary: true,
            securityType: options.securityType ?? "all",
            reviewRequired: options.reviewRequired ?? true,
            contractName: options.contractName
        });

        const context = page.context();
        const masterPage = await context.newPage();

        await loginWithCredentials(masterPage, baseUrl, master.id, master.password);
        await masterPage.goto(reviewUrl, WAIT_OPTIONS);
        await masterPage.screenshot({ path: `screenshots/${getNewTimestamp()}_review_opened.png` });

        await toggleEditorUsageOnReview(masterPage, false);
        await attemptContractUpdate(masterPage);
        await attemptAssignLegalReviewer(masterPage);

        return { reviewUrl };
    } catch (error) {
        console.error("CS_BG_serializer_null.js 실행 중 오류:", error);
        throw error;
    }
}