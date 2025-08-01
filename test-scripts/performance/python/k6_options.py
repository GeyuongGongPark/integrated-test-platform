# LFBZ_performance/python/k6_options.py

# 환경
ENV_TYPE_OPTIONS = {
    "알파": "alpha",
    "운영": "prod",
    "계열사(지주)": "multi1",
    "계열사(중간)": "multi2",
    "계열사(최하위)": "multi3"
}

# 문서 타입
DOCUMENT_TYPE_OPTIONS = {
    "계약 검토": "clm",
    "법률 자문": "advice",
    "송무": "litigation"
}
# 검토 구분
DRAFT_TYPE_OPTIONS = {
    "신규": "new",
    "변경": "change",
    "해지": "stop"
}
 # 계약서 업로드 여부 (검토 구분 : 해지)
CONTRACT_UPLOAD_OPTIONS = {
    "사용": "use",
    "사용 안함": "not_use"
}
# 편집기 사용 여부
EDITOR_USE_OPTIONS = {
    "사용": "use",
    "사용 안함": "not_use"
}
# 문서 첨부 방식
CONTRACT_TYPE_OPTIONS = {
    "파일로 첨부하기": "file",
    "My계약서에서 불러오기": "my"
}
#보안 여부
SECURITY_TYPE_OPTIONS = {
    "전체 공개": "all",
    "참고인 공개": "refrt",
    "비공개": "secur"
}
# 검토 여부
REVIEW_TYPE_OPTIONS = {
    "검토 필요": "review",
    "검토 불필요": "not_review"
}

#법률 자문
ADVICE_TYPE_OPTIONS = {
    "개인정보": "pi", # persinal information (Personal Information)
    "계약": "cn", # contract (Contract)
    "공정거래": "ft", # fair trade (Fair Trade)
    "기업인수/합병": "ma", # M&A (Mergers & Acquisitions)
    "민사": "ci", # civil (Civil)
    "세법": "tl", # tax law (Tax Law)
    "소송/중재": "la", # litigation/arbitration (Litigation/Arbitration)
    "인사/노무": "hr", # HR/labor (HR/Labor)
    "기업법무": "cole", # corporate legal affairs (Corporate Legal Affairs)
    "해외법무": "overle", # overseas legal affairs (Overseas Legal Affairs)
    "기타": "etc" # etc (Etcetera)
}