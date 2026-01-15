import { test } from '@playwright/test';
import LFBZFullTest from '../Base_Code/lfbz.js';

test('LFBZ 전체 시나리오', async ({page}) => {
    await LFBZFullTest(page);
});

