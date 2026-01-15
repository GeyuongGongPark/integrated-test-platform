import { test, expect } from '@playwright/test';
import clm_draft from '../../Base_Code/clm/draft/clm_draft.js';

test('신규 계약 검토 요청 - 기본 플로우 (My계약서 불러오기)', async ({ page }) => {
  await clm_draft(page, {
    DRAFT_TYPE: 'new',        // 'new' | 'change' | 'stop'
    EDITER_USE: 'use',        // 'use' | 'none'
    CONTRAT_TYPE: 'my',       // 'file' | 'my'
    CONTRAT_SELECT: 'my',     // 'file' | 'my'
    SECURITY_TYPE: 'all',     // 'all' | 'refer' | 'hidden'
    REVIEW_TYPE: 'use',       // 'use' | 'none'
    APPROVAL_SET: 'none'      // 'use' | 'none'
  });

  // 간단한 사후 확인 (예: URL 포함 여부)
  await expect(page).toHaveURL(/clm\/draft/);
});