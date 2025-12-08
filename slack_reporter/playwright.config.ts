import { defineConfig } from '@playwright/test';

export default defineConfig({
    // 테스트 디렉토리 설정
    testDir: '../test-scripts/playwright',
    
    // 슬랙 리포터 설정
    reporter: [
        ['list'], // 기본 콘솔 출력
        ['./slack_reporter.ts'], // 슬랙 리포터
    ],
    
    // 테스트 설정
    use: {
        baseURL: process.env.BASE_URL || 'http://localhost:3000',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
    },
    
    // 프로젝트 설정
    projects: [
        {
            name: 'chromium',
            use: { 
                viewport: { width: 1280, height: 720 },
            },
        },
    ],
});