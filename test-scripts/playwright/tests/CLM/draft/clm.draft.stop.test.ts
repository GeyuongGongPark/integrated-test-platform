import { test } from '@playwright/test';
import clm_draft_stop from '../../../Base_Code/clm/draft/clm_draft.stop.js';

test('해지 계약 검토 요청 시나리오', async ({page}) => {
    await clm_draft_stop(page, { 
        DRAFT_TYPE: 'stop', 
        EDITER_USE: 'use',
        CONTRACT_TYPE: 'file',
        CONTRACT_SELECT: 'file',
        SECURITY_TYPE: 'all',
        REVIEW_TYPE: 'use',
        APPROVAL_SET: 'use'
    });
})
