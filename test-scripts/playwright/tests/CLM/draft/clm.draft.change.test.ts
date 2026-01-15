import { test } from '@playwright/test';
import clm_draft_change from '../../../Base_Code/clm/draft/clm_draft.change.js';

test('변경 계약 검토 요청 시나리오', async ({page}) => {
    await clm_draft_change(page, { 
        DRAFT_TYPE: 'change', 
        EDITER_USE: 'use',
        CONTRACT_TYPE: 'my',
        CONTRACT_SELECT: 'my',
        SECURITY_TYPE: 'all',
        REVIEW_TYPE: 'use',
        APPROVAL_SET: 'use'
    });
})
