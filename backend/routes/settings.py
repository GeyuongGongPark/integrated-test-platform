# -*- coding: utf-8 -*-
"""시스템 설정 API (AI TC 기본 프롬프트 등)"""
from flask import Blueprint, request, jsonify
from models import db, SystemConfig
from utils.cors import add_cors_headers
from utils.auth_decorators import admin_required, user_required
from utils.common_helpers import handle_options_request

# AI TC 기본 프롬프트 키
TC_PROMPT_CONFIG_KEY = 'tc_default_prompt'

# 기본 프롬프트 (txt 파일 형식과 동일)
DEFAULT_TC_PROMPT = """###############################################
공용 단위 테스트케이스(TC) 생성 프롬프트
###############################################
# 목적
# - 여러 소프트웨어가 섞인 환경에서도
# 테스트케이스 구조를 일관되게 생성하기 위한
# "구조 중심" 프롬프트 예시
# - 실제 제품, UI, 내부 정책은 포함하지 않음
################################################
# [0] 글로벌 공통 설정 (Global Context)
################################################
/context.global
TC_ID_PREFIX = "TC"
TC_ID_PAD = 3
################################################
# [1] 테스트케이스 생성 공통 규칙
################################################
/tc.rules
A. 사전 조건은 "준비 상태"만 포함한다
B. 테스트 과정는 반드시 1 → N 순서로 작성한다
C. 한 단계에는 하나의 사용자 행동만 포함한다
D. 각 단계는 완전한 문장으로 끝난다
E. 예상 결과는 검증 포인트 1개만 작성한다
F. 우선순위는 P1, P2, P3 중 하나만 선택한다
G. 하나의 문장에 기능이 2개 이상 포함되면 TC를 분리한다
H. 입력에 없는 내용을 임의로 추정하지 않는다
################################################
# [2] 우선순위 정의 (Priority Policy)
################################################
/tc.priority
P1 = 핵심 기능 (미동작 시 서비스 사용 불가)
P2 = 주요 기능 (업무 품질에 영향)
P3 = 부가 기능 (편의/UI 요소)
################################################
# [3] 출력 컬럼 고정
################################################
/tc.columns
- TC No.
- 카테고리
- 1 Depth
- 2 Depth
- 3 Depth
- 4 Depth
- 확인기능
- 사전 조건
- 테스트 과정
- 기대결과
- priority
- result
- 비고
################################################
# [4] 입력 형식 (기존 체크리스트 재사용)
################################################
/tc.input
<<<
|No|Module/Feature|Checklist Item|
|1|Settings/Input|Saving succeeds when minimum value is entered|
>>>
################################################
# [5] 생성 결과 예시 (Sample Output)
################################################
TC No.: TC_001
카테고리: 인증/보안
1 Depth: 최초로그인
2 Depth: 승인요청
3 Depth: 이메일 발송
4 Depth:
확인기능: 로그인
사전조건:
1. 신규 가입 대상자 계정 상태
테스트 과정:
1. 서비스에서 최초 SSO 로그인 및 IP 인증 완료
2. 2차 이메일 인증 완료 후 대기
"""

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings/tc-prompt', methods=['GET', 'OPTIONS'])
@user_required
def get_tc_prompt():
    """AI TC 기본 프롬프트 조회 (로그인 사용자)"""
    if request.method == 'OPTIONS':
        return handle_options_request()

    row = SystemConfig.query.filter_by(key=TC_PROMPT_CONFIG_KEY).first()
    content = (row.value if row else None) or DEFAULT_TC_PROMPT
    response = jsonify({'content': content})
    return add_cors_headers(response), 200


@settings_bp.route('/settings/tc-prompt', methods=['PUT', 'OPTIONS'])
@admin_required
def update_tc_prompt():
    """AI TC 기본 프롬프트 저장 (관리자 전용)"""
    if request.method == 'OPTIONS':
        return handle_options_request()

    data = request.get_json() or {}
    content = data.get('content', '').strip()

    row = SystemConfig.query.filter_by(key=TC_PROMPT_CONFIG_KEY).first()
    if row:
        row.value = content if content else None
    else:
        row = SystemConfig(key=TC_PROMPT_CONFIG_KEY, value=content if content else None)
        db.session.add(row)
    db.session.commit()

    response = jsonify({'message': '저장되었습니다.', 'content': row.value or ''})
    return add_cors_headers(response), 200
