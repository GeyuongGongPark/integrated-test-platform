# Playwright 연동 가이드 (실행 버튼 + MCP)

## 요약

- **SaaS/플랫폼 사용자**: **실행 버튼**으로 **테스트 단계(JSON)만** 넣으면 별도 스크립트 없이 Playwright 자동화가 동작합니다. **(구현 완료)**
- **Cursor 사용자**: 테스트 케이스 ID만 말하면 에이전트가 API로 케이스를 조회한 뒤 Playwright MCP로 실행하는 스킬을 사용할 수 있습니다.

---

## 실행 버튼으로 테스트 단계만 실행 (권장, 구현 완료)

플랫폼 UI에서 **자동화 코드 경로 없이** 테스트 케이스의 **테스트 단계(test_steps)** 만으로 실행할 수 있습니다.

### 동작 방식

1. 테스트 케이스 편집 시 **테스트 단계 (JSON)** 필드에 단계 배열을 입력합니다.
2. **자동화 코드 경로**는 비워 둡니다.
3. **실행** 버튼을 누르면 백엔드가 `test-scripts/playwright/step-runner/run-steps.mjs`를 호출해 단계를 실행합니다.
4. 결과는 기존과 동일하게 Pass/Fail, 실행 시간, 에러 메시지로 저장·표시됩니다.

### test_steps JSON 형식

배열로 된 단계 목록입니다. 각 단계는 `action`과 그에 맞는 인자를 가집니다.

| action | 설명 | 예시 |
|--------|------|------|
| `navigate` / `goto` | URL 이동 | `{"action":"navigate","url":"/"}` 또는 `{"action":"goto","url":"https://example.com"}` |
| `click` | 클릭 | `{"action":"click","selector":"button[type=submit]"}` 또는 `{"action":"click","text":"로그인"}` |
| `fill` / `type` | 입력 | `{"action":"fill","selector":"#id","value":"admin"}` |
| `press` | 키 입력 | `{"action":"press","key":"Enter"}` 또는 `{"action":"press","selector":"#input","key":"Enter"}` |
| `waitForTimeout` | 대기(ms) | `{"action":"waitForTimeout","timeout":1000}` |
| `waitForSelector` | 요소 대기 | `{"action":"waitForSelector","selector":".loaded","timeout":5000}` |
| `assertText` | 텍스트 검증 | `{"action":"assertText","selector":"h1","text":"대시보드"}` 또는 `{"action":"assertText","text":"환영합니다"}` |
| `selectOption` | 셀렉트 선택 | `{"action":"selectOption","selector":"#env","values":["prod"]}` |

- 상대 URL은 환경변수 `BASE_URL` 또는 `PLAYWRIGHT_BASE_URL`(기본 `http://localhost:3000`)을 기준으로 해석됩니다.
- 실행 API POST body에 `baseUrl`을 넘기면 해당 URL을 기준으로 사용합니다.

### 예시

```json
[
  {"action":"navigate","url":"/"},
  {"action":"fill","selector":"#username","value":"admin"},
  {"action":"fill","selector":"#password","value":"secret"},
  {"action":"click","selector":"button[type=submit]"},
  {"action":"waitForSelector","selector":"[data-testid=dashboard]","timeout":5000},
  {"action":"assertText","text":"대시보드"}
]
```

### 관련 파일

- 러너 스크립트: `test-scripts/playwright/step-runner/run-steps.mjs`
- 백엔드 공통: `backend/utils/playwright_steps_runner.py`
- 실행 API: `backend/routes/testcases.py` (`execute_automation_code`), `backend/tasks.py` (`execute_test_case`)

---

## 현재 데이터 구조

| 구분 | 내용 |
|------|------|
| 테스트 케이스 | `TestCase`: name, description, pre_condition, expected_result, **test_steps**, automation_code_path, automation_code_type |
| 실행 우선순위 | 1) **test_steps**만 있으면 → 단계 러너 실행 2) **automation_code_path** 있으면 → 해당 스크립트 실행 |
| 제약 | 둘 다 없으면 "자동화 코드 경로 또는 테스트 단계를 설정해 주세요" 오류 |

---

## Playwright MCP (Cursor 전용)

- **Playwright MCP**는 Cursor(또는 MCP 클라이언트) 안에서만 동작합니다.
- 플랫폼 백엔드는 MCP를 직접 호출할 수 없으므로, **실행 버튼**은 위의 **테스트 단계 러너**를 사용합니다.
- Cursor에서 “테스트 케이스 N번 실행해줘”처럼 요청할 때는 `.cursor/skills/run-testcase-playwright-mcp/SKILL.md` 스킬이 API로 케이스를 조회한 뒤 MCP 도구로 실행합니다.

---

## API 참고

- 단일 테스트 케이스: `GET /api/testcases/<id>` → `test_steps` 포함.
- 실행: `POST /api/testcases/<id>/execute`  
  - Body(선택): `{"baseUrl": "http://localhost:3000"}`  
  - test_steps만 있어도 실행 가능.

---

## 관련 파일

- 테스트 케이스 실행: `backend/tasks.py`, `backend/routes/testcases.py`
- 테스트 케이스 모델: `backend/models.py` (`TestCase`, `test_steps` 컬럼)
- 단계 러너: `test-scripts/playwright/step-runner/run-steps.mjs`, `backend/utils/playwright_steps_runner.py`
- Cursor 스킬: `.cursor/skills/run-testcase-playwright-mcp/SKILL.md`
