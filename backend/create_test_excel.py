import pandas as pd

# 테스트 데이터 생성
test_data = [
    {
        'project_id': 1,
        'main_category': 'CLM 시스템',
        'sub_category': '기안 작성',
        'detail_category': '기본 기안 작성',
        'pre_condition': '사용자가 로그인되어 있음',
        'expected_result': '기안이 성공적으로 작성됨',
        'result_status': 'N/T',
        'remark': '테스트용 데이터',
        'environment': 'dev',
        'automation_code_path': 'test-scripts/playwright/clm_draft.js',
        'automation_code_type': 'playwright'
    },
    {
        'project_id': 1,
        'main_category': 'CLM 시스템',
        'sub_category': '검토',
        'detail_category': '법무 검토',
        'pre_condition': '기안이 작성되어 있음',
        'expected_result': '법무 검토가 완료됨',
        'result_status': 'N/T',
        'remark': '테스트용 데이터',
        'environment': 'dev',
        'automation_code_path': 'test-scripts/playwright/clm_lagel.js',
        'automation_code_type': 'playwright'
    },
    {
        'project_id': 1,
        'main_category': 'CLM 시스템',
        'sub_category': '재무 검토',
        'detail_category': '재무 검토',
        'pre_condition': '기안이 작성되어 있음',
        'expected_result': '재무 검토가 완료됨',
        'result_status': 'N/T',
        'remark': '테스트용 데이터',
        'environment': 'dev',
        'automation_code_path': 'test-scripts/playwright/clm_financial.js',
        'automation_code_type': 'playwright'
    }
]

# DataFrame 생성
df = pd.DataFrame(test_data)

# Excel 파일로 저장
df.to_excel('test_upload.xlsx', index=False, sheet_name='TestCases')

print("테스트용 Excel 파일이 생성되었습니다: test_upload.xlsx")
print("파일 내용:")
print(df) 