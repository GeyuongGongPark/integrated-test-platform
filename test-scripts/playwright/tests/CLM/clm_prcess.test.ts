import { test } from '@playwright/test';
import clm_process from '../../Base_Code/clm/clm_process.js';

test('계약 검토 요청 시나리오', async ({page}) => {
    await clm_process(page, { 
        DRAFT_TYPE: 'new', 
        EDITER_USE: 'use',
        CONTRACT_TYPE: 'my',
        CONTRACT_SELECT: 'my',
        SECURITY_TYPE: 'all',
        REVIEW_TYPE: 'none',
        APPROVAL_SET: 'none'
    });
})
