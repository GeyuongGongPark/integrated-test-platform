# Slack 리포트 발송 기능

Playwright 테스트 결과를 Slack으로 자동 발송하는 리포터입니다.

## 📋 기능

- 테스트 실행 결과를 Slack으로 자동 전송
- 총 테스트 수, 통과/실패/스킵된 테스트 수 표시
- 실행 시간 표시
- 실패한 테스트 상세 정보 포함

## 🚀 설정 방법

### 1. Slack Webhook URL 생성

1. Slack 워크스페이스에 로그인
2. [Slack Apps](https://api.slack.com/apps)에서 새 앱 생성
3. "Incoming Webhooks" 기능 활성화
4. 웹훅 URL 생성 및 복사

### 2. 환경 변수 설정

```bash
# .env 파일에 추가
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

또는 실행 시 직접 지정:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL npx playwright test
```

### 3. Playwright 설정

`playwright.config.ts` 파일에서 리포터를 설정합니다:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
    reporter: [
        ['list'], // 기본 콘솔 출력
        ['./slack_reporter.ts'], // 슬랙 리포터
    ],
    // ... 기타 설정
});
```

## 📝 사용 방법

### 기본 사용

```bash
# 환경 변수 설정 후 테스트 실행
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL npx playwright test
```

### CI/CD에서 사용

```yaml
# GitHub Actions 예시
- name: Run Playwright tests
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  run: npx playwright test
```

## 📊 리포트 형식

Slack 리포트는 다음 정보를 포함합니다:

- **Total Tests**: 전체 테스트 수
- **Passed Tests**: 통과한 테스트 수
- **Failed Tests**: 실패한 테스트 수
- **Skipped Tests**: 스킵된 테스트 수
- **Duration**: 실행 시간
- **Result**: 실패한 테스트 상세 정보 (있는 경우)

## ⚙️ 커스터마이징

리포트 형식을 변경하려면 `slack_reporter.ts` 파일의 `getSlackMessage` 함수를 수정하세요.

## 🔍 문제 해결

### Slack 메시지가 전송되지 않는 경우

1. `SLACK_WEBHOOK_URL` 환경 변수가 올바르게 설정되었는지 확인
2. 웹훅 URL이 유효한지 확인
3. 콘솔 로그에서 오류 메시지 확인

### 리포트가 표시되지 않는 경우

- Playwright 테스트가 정상적으로 실행되었는지 확인
- `playwright.config.ts`에서 리포터 설정이 올바른지 확인

