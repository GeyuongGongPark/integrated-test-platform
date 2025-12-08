import type { Reporter, FullConfig, Suite, TestCase, TestResult, FullResult  } from '@playwright/test/reporter';
import path from 'path';

const getSlackMessage = ({
    all,
    passed,
    failed,
    skipped,
    duration,
    result,
}) => {1
    //slack block kit
    return {
        blocks: [
            {
                type: 'header',
                text: {
                    type: 'plain_text',
                    text: 'Playwright Test Report',
                },
            },
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `*Total Tests: ${all}*`,
                },
            },
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `*Passed Tests: ${passed}*`,
                },
            },
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `*Failed Tests: ${failed}*`,
                },
            },
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `*Skipped Tests: ${skipped}*`,
                },
            },
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `*Duration: ${duration}*`,
                },
            },
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `*Result: ${result}*`,
                },
            },
        ],
    };
};

class MyReporter implements Reporter {
    all = 0;
    passed = 0;
    failed = 0;
    skipped = 0;
    failMessages = '';

    onBeing(_: FullConfig, suite: Suite) {
        this.all = suite.allTests().length;
    }

    onTestEnd(test: TestCase, result: TestResult) {
        const testDuration = '${result.duration / 1000).toFixed(1)}s';
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
        const webhookUrl = await process.env.SLACK_WEBHOOK_URL;

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

        const resultBlockKit = getSlackMessage({
            all: `${this.all}`,
            passed: `${this.passed}개`,
            failed: `${this.failed}개`,
            skipped: `${this.skipped}개`,
            duration: `${(duration / 1000).toFixed(1)}s`,
            result: `${this.failMessages ? `통과하지 못한 테스트\n${this.failMessages}` : `모든 테스트 통과!`}`,
        });

        return resultBlockKit;
    }
}

export default MyReporter;