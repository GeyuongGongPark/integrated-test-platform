import { browser } from 'k6/browser';

export const options = {
  scenarios: {
    ui: {
      executor: 'shared-iterations',
      options: {
        browser: {
          type: 'chromium',
          defaultViewport: {
            width: 1920,
            height: 1080,
          },
        },
      },
    },
  },
  thresholds: {
    checks: ['rate==1.0'],
  },
};

export default async function () {
  const page = await browser.newPage();
  
  try {
    await page.goto('https://business.lawform.io');
    console.log('페이지 로드 성공');
    
    // 간단한 스크린샷
    await page.screenshot({path: 'screenshots/simple_test.png'});
    
    return page;
  } finally {
    await page.close();
  }
} 