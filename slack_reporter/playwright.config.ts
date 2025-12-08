import { defineConfig } from '@playwright/test';

export default defineConfig({
    reporter: [['./slack_reporter/slack_reporter.ts', { webhookUrl: process.env.SLACK_WEBHOOK_URL }]], //slack reporter 사용
});