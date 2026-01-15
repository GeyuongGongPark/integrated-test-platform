import type { Reporter, FullConfig, Suite, TestCase, TestResult, FullResult  } from '@playwright/test/reporter';
import path from 'path';

const getSlackMessage = ({
    all,
    passed,
    failed,
    skipped,
    duration,
    result,
    hasFailures,
}) => {
    // Slack Block Kit 구조
    const blocks: any[] = [
        {
            type: 'header',
            text: {
                type: 'plain_text',
                text: '🧪 Playwright Test Report',
            },
        },
        {
            type: 'divider',
        },
        {
            type: 'section',
            fields: [
                {
                    type: 'mrkdwn',
                    text: `*총 테스트:*\n${all}`,
                },
                {
                    type: 'mrkdwn',
                    text: `*소요 시간:*\n${duration}`,
                },
                {
                    type: 'mrkdwn',
                    text: `*✅ 통과:*\n${passed}`,
                },
                {
                    type: 'mrkdwn',
                    text: `*❌ 실패:*\n${failed}`,
                },
            ],
        },
    ];

    // 스킵된 테스트가 있을 경우에만 표시
    if (skipped !== '0개' && skipped !== '0') {
        blocks.push({
            type: 'section',
            fields: [
                {
                    type: 'mrkdwn',
                    text: `*⚠️ 스킵:*\n${skipped}`,
                },
            ],
        });
    }

    blocks.push({
        type: 'divider',
    });

    // 결과 섹션
    if (hasFailures) {
        blocks.push({
            type: 'section',
            text: {
                type: 'mrkdwn',
                text: `*❌ 테스트 결과:*\n\`\`\`${result}\`\`\``,
            },
        });
    } else {
        blocks.push({
            type: 'section',
            text: {
                type: 'mrkdwn',
                text: `*✅ ${result}*`,
            },
        });
    }

    return { blocks };
};

class MyReporter implements Reporter {
    all = 0;
    passed = 0;
    failed = 0;
    skipped = 0;
    failMessages = '';

    onBegin(_: FullConfig, suite: Suite) {
        this.all = suite.allTests().length;
    }

    onTestEnd(test: TestCase, result: TestResult) {
        const testDuration = `${(result.duration / 1000).toFixed(1)}s`;
        const fileName = path.basename(test.location.file);
        const testTitle = test.title;

        switch (result.status) {
            case 'failed':
            case 'timedOut':
                this.addFailMessage(
                    `❌ ${fileName}:${test.location.line}:${test.location.column} > ${testTitle} ${testDuration}`,
                );
                this.failed += 1;
                break;
            case 'skipped':
                this.addFailMessage(
                    `⚠️ ${fileName}:${test.location.line}:${test.location.column} > ${testTitle} ${testDuration}`,
                );
                this.skipped += 1;
                break;
            case 'passed':
                this.passed += 1;
                break;
            default:
                break;
        }
    }

    async onEnd(result: FullResult) {
        const blockKit = await this.getBlockKit(result);
        const webhookUrl = process.env.SLACK_WEBHOOK_URL;

        if (!webhookUrl) {
            console.error('SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.');
            return;
        }

        try {
            const response = await fetch(webhookUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(blockKit),
            });
    
            if (!response.ok) {
                console.error('Slack 메시지 전송 실패:', response.statusText);
            } else {
                console.log('Slack 메시지 전송 성공');
            }
        } catch (error) {
            console.error('Slack 메시지 전송 중 에러 발생:', error);
        }
    }

    private addFailMessage(message: string) {
        this.failMessages += `\n${message}`;
    }
    private async getBlockKit(result: FullResult){
        const { duration } = result;
        const hasFailures = this.failed > 0 || this.skipped > 0;

        const resultBlockKit = getSlackMessage({
            all: `${this.all}개`,
            passed: `${this.passed}개`,
            failed: `${this.failed}개`,
            skipped: `${this.skipped}개`,
            duration: `${(duration / 1000).toFixed(1)}초`,
            result: hasFailures 
                ? `통과하지 못한 테스트:${this.failMessages}` 
                : `모든 테스트 통과! 🎉`,
            hasFailures,
        });

        return resultBlockKit;
    }
}

export default MyReporter;