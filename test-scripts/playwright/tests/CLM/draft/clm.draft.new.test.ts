import { test } from '@playwright/test';
import clm_draft_new from '../../../Base_Code/clm/draft/clm_draft.new.js';

test('신규 계약 검토 요청 시나리오', async ({page}) => {
    await clm_draft_new(page, { 
        DRAFT_TYPE: 'new', 
        EDITER_USE: 'use',
        CONTRACT_TYPE: 'file',
        CONTRACT_SELECT: 'file',
        SECURITY_TYPE: 'all',
        REVIEW_TYPE: 'use',
        APPROVAL_SET: 'use'
    });
})
