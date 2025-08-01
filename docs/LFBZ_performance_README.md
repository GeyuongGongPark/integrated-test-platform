# LFBZ_performance
LFBZ 웹 성능 테스트 관리 레포
## 사용 방법

### 1. 기본 사용법 (CLI)
- `clm/clm_draft.js` 실행 시 `_ENV.js` 설정 값 확인하여 실행 필요
- ex.
    - 계약 구분 : 신규
    - 편집기 사용 여부 : 사용 안함
    - 계약서 첨부 방식 : My계약서에서 불러오기
    - 보안 여부 : 전체 공개
    - 검토 진행 여부 : 검토 필요
    - `clm/clm_draft.js` 실행 명령어
    - k6 run -e DRAFT_TYPE=new -e SECURITY_TYPE=all -e REVIEW_TYPE=use clm/clm_draft.js

### 2. 기본 사용법 (GUI)
- `python/k6_gui.py` 다운로드
    - windows 사용자는 `k6_gui.exe` 다운로드
- `python3 k6_gui.py` 명령어로 python 코드 실행
- 실행된 문서 생성기 화면에서 생성 필요한 옵션(combobox) 선택