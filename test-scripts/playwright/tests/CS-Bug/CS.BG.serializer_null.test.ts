import { test, expect } from '@playwright/test';
import CS_BG_serializer_null from '../../Bug/CS_Bug/CS.BG.serializer_null.js';

test.use({ ignoreHTTPSErrors: true });

test('Serializer null 시나리오 재현 및 담당자 배정 가능 여부 확인', async ({ page }) => {
    const { reviewUrl } = await CS_BG_serializer_null(page);
    expect(reviewUrl).toContain('/clm/review/');
});