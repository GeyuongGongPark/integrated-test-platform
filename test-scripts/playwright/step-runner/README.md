# Playwright 단계 실행기

테스트 케이스의 `test_steps` JSON만으로 브라우저 자동화를 실행합니다. (별도 .spec 파일 불필요)

## 사용법

```bash
# 프로젝트 루트에서
cd test-scripts/playwright/step-runner
node run-steps.mjs steps.json

# 또는 stdin으로 JSON 전달
echo '[{"action":"navigate","url":"/"}]' | node run-steps.mjs
```

## 환경변수

- `BASE_URL` / `PLAYWRIGHT_BASE_URL`: 기본 URL (기본값 `http://localhost:3000`)
- `HEADLESS`: `false`면 브라우저 창 표시 (기본 `true`)
- `STEPS_FILE`: 단계 JSON 파일 경로 (인자 대신 사용 가능)

## 지원 action

navigate, goto, click, fill, type, press, waitForTimeout, waitForSelector, assertText, selectOption

자세한 형식은 프로젝트 루트 `docs/PLAYWRIGHT_MCP_INTEGRATION.md` 참고.
