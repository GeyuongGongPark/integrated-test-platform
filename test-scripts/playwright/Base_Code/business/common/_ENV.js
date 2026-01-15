export default async function ENVFlow(page, options = {}) {
    // 옵션에서 값 읽기 (기존/새 키 모두 허용)
    const draftType = options.DRAFT_TYPE ?? options.draftType ?? "new"; // 기본값 "new"
    const contractUpload = options.CONTRACT_UPLOAD ?? options.CONTRAT_UPLOAD ?? "use"; // 기본값 "use"
    const editorUse = options.EDITOR_USE ?? options.EDITER_USE ?? "use"; // 기본값 "use"
    const contractype = options.CONTRACT_TYPE ?? options.CONTRAT_TYPE ?? "file";
    const contractSelect = options.CONTRACT_SELECT ?? options.CONTRAT_SELECT ?? "file";
    const security = options.SECURITY_TYPE ?? "all";
    const revivew = options.REVIEW_TYPE ?? "use";
    const approval = options.APPROVAL_SET ?? "use";
    const advice = options.ADVICE_TYPE ?? "pi";
    
    // 계약 구분
    if (draftType === "new") {
      // 신규 계약 처리
    await page.locator('//label[.//div[text()="신규"]').click();
    } else if (draftType === "change") {
      // 변경 계약 처리
    await page.locator('//label[.//div[text()="변경"]').click();
    } else {
      // 계약 구분 : 해지
        await page.locator('//label[.//div[text()="해지"]').click();
    }
    // 계약서 업로드 여부 (계약 검토 : 해지)
    if (contractUpload === "use") {
      // 계약서 업로드 사용
    await page.locator('//label[.//div[text()="사용"]').click();
    } else {
      // 계약서 업로드 사용 안함
    await page.locator('//label[.//div[text()="사용 안 함" or text()="사용 안함"]').click();
    }
    // 편집기 사용 여부
    if (editorUse === "use") {
        await page.locator('//label[.//div[text()="사용"]').click();
    } else {
        await page.locator('//label[.//div[text()="사용 안 함" or text()="사용 안함"]').click();
    }
    // 계약서 첨부 방식
    if (contractype === "file") {
        await page.locator('//label[.//div[text()="파일로 첨부하기"]').click();
    } else {
        await page.locator('//label[.//div[text()="My계약서에서 불러오기"]').click();
    }
    // 계약서
    if (contractSelect === "file") {
        await page.locator('img[alt="파일 업로드"]').click();
    } else {
        await page.locator('img[alt="불러오기 아이콘"]').click();
    }
    //보안여부
    if (security === "all") {
        await page.locator('//label[.//div[text()="전체 공개"]]').click();
    } else if (security === "refer") {
        await page.locator('//label[.//div[text()="참조인"]]').click();
    } else {
        await page.locator('//label[.//div[text()="비공개"]').click();
    }
    // 검토 진행 여부
    if (revivew === "use") {
        await page.locator('//label[.//div[text()="검토 필요"]]').click();
    } else {
        await page.locator('//label[.//div[text()="검토 불필요"]]').click();
    }
    // 내부 결재선
    if (approval === "use") {
        await page.locator('img[alt="결재자 추가하기"]').click();
    } else {
        
    }

    // 법률 자문 구분
    if (advice === "pi") {
  
    } else if (advice === "cn") {
  
    } else if (advice === "ft") {
  
    } else if (advice === "ma") {
  
    } else if (advice === "ci") {
  
    } else if (advice === "tl") {
  
    } else if (advice === "la") {
  
    } else if (advice === "hr") {
  
    } else if (advice === "cole") {
  
    } else if (advice === "overle") {
  
    } else {
      
    }
}
