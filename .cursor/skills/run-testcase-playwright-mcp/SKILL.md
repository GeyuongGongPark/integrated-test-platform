---
name: run-testcase-playwright-mcp
description: 테스트 케이스 ID만으로 플랫폼 API에서 케이스를 조회한 뒤, 별도 스크립트 없이 Playwright MCP 도구로 자동화를 실행한다.
---

# 테스트 케이스 → Playwright MCP 실행

## 사용 시점

- 사용자가 "테스트 케이스 N번 실행해줘", "테스트 케이스 ID 5 실행", "이 테스트 케이스 자동화로 돌려줘" 등 **테스트 케이스만 지정하고 실행**을 요청할 때 적용한다.
- **자동화 코드 경로(automation_code_path)가 없어도** 동작한다. 테스트 케이스의 이름·사전조건·기대결과를 해석해 Playwright MCP로 실행한다.

## 전제 조건

- 백엔드 API가 떠 있어야 한다 (예: `http://localhost:5001` 또는 프로젝트 `.env`/설정에 정의된 URL).
- Playwright MCP가 사용 가능한 환경(Cursor 등)에서 실행한다.

## 실행 절차

1. **테스트 케이스 ID 확인**
   - 사용자 메시지에서 테스트 케이스 ID(숫자)를 추출한다. 없으면 "몇 번 테스트 케이스를 실행할까요?"라고 물어본다.

2. **API로 테스트 케이스 조회**
   - 백엔드 URL은 프로젝트 루트 `.env`의 `FLASK_APP`/서버 주소, 또는 일반적인 `http://localhost:5001`을 사용한다. 필요 시 `BACKEND_URL` 등이 있으면 그걸 쓴다.
   - `GET {API_BASE}/api/testcases/{id}` 로 단일 테스트 케이스를 조회한다. 터미널에서 `curl -s "http://localhost:5001/api/testcases/{id}"` 로 호출해 JSON을 받을 수 있다.
   - (인증이 필요하면 요청 헤더에 `Authorization: Bearer <token>` 등을 넣는다.)
   - 응답에서 `name`, `pre_condition`, `expected_result`, `remark` 를 꺼낸다.

3. **실행 단계 해석**
   - 위 필드들을 조합해 "무엇을 할지" 단계로 정리한다.
   - 예: "로그인 페이지 이동" → navigate, "ID 입력" → 텍스트 입력, "로그인 버튼 클릭" → click 등.
   - URL이 필요하면 사전조건/비고에서 추출하거나, 테스트 대상 앱의 기본 URL(예: 프론트엔드 주소)을 사용한다.

4. **Playwright MCP로 실행**
   - `mcp_playwright_browser_navigate`: 시작 URL 이동.
   - `mcp_playwright_browser_snapshot`: 필요 시 페이지 구조 확인.
   - `mcp_playwright_browser_click`, `mcp_playwright_browser_type`, `mcp_playwright_browser_fill_form` 등으로 단계 수행.
   - 각 단계 후 필요하면 스냅샷으로 결과 확인.

5. **기대결과 검증 및 보고**
   - `expected_result`에 맞는지 스냅샷/결과를 비교해 Pass/Fail 여부를 판단한다.
   - 사용자에게 실행 결과(성공/실패, 실패 시 원인)를 요약해서 전달한다.

## API 응답 참고

- `GET /api/testcases/<id>` 응답 예: `id`, `name`, `main_category`, `sub_category`, `detail_category`, `pre_condition`, `expected_result`, `remark`, `automation_code_path`, `automation_code_type`, ...
- `automation_code_path`가 비어 있어도 이 스킬은 **테스트 케이스 내용만**으로 Playwright MCP를 사용해 실행한다.

## 주의사항

- 테스트 케이스 내용이 모호하면(예: "정상 동작 확인") 구체적인 URL·선택자·입력값을 사용자에게 한 번 더 물어본다.
- 타임아웃·네트워크 오류가 나면 재시도 또는 실패 사유를 명확히 보고한다.
