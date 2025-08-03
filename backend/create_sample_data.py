#!/usr/bin/env python3
"""
샘플 데이터 생성 스크립트
"""

from app import app, db, Project, TestCase, Folder, TestResult, DashboardSummary
from datetime import datetime, date
import json

def create_sample_data():
    """샘플 데이터 생성"""
    with app.app_context():
        print("샘플 데이터 생성 시작...")
        
        # 기존 데이터 삭제
        TestResult.query.delete()
        TestCase.query.delete()
        Folder.query.delete()
        DashboardSummary.query.delete()
        db.session.commit()
        
        # 1. 프로젝트 생성
        project = Project(name='LFBZ 통합 테스트', description='LFBZ 시스템 통합 테스트 프로젝트')
        db.session.add(project)
        db.session.commit()
        
        # 2. 폴더 구조 생성
        # 환경별 폴더
        dev_folder = Folder(
            folder_name='DEV 환경',
            folder_type='environment',
            environment='dev'
        )
        alpha_folder = Folder(
            folder_name='ALPHA 환경',
            folder_type='environment',
            environment='alpha'
        )
        prod_folder = Folder(
            folder_name='PRODUCTION 환경',
            folder_type='environment',
            environment='production'
        )
        
        db.session.add_all([dev_folder, alpha_folder, prod_folder])
        db.session.commit()
        
        # 배포일자별 폴더
        dev_dep1 = Folder(
            folder_name='2025-08-01 배포',
            folder_type='deployment_date',
            environment='dev',
            deployment_date=date(2025, 8, 1),
            parent_folder_id=dev_folder.id
        )
        dev_dep2 = Folder(
            folder_name='2025-08-03 배포',
            folder_type='deployment_date',
            environment='dev',
            deployment_date=date(2025, 8, 3),
            parent_folder_id=dev_folder.id
        )
        
        alpha_dep1 = Folder(
            folder_name='2025-08-02 배포',
            folder_type='deployment_date',
            environment='alpha',
            deployment_date=date(2025, 8, 2),
            parent_folder_id=alpha_folder.id
        )
        
        prod_dep1 = Folder(
            folder_name='2025-08-01 배포',
            folder_type='deployment_date',
            environment='production',
            deployment_date=date(2025, 8, 1),
            parent_folder_id=prod_folder.id
        )
        
        db.session.add_all([dev_dep1, dev_dep2, alpha_dep1, prod_dep1])
        db.session.commit()
        
        # 3. 테스트 케이스 생성
        test_cases = [
            # DEV 환경 테스트 케이스
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Draft',
                'detail_category': 'Create',
                'pre_condition': '로그인 완료',
                'description': 'DEV - CLM Draft 생성 테스트',
                'result_status': 'Pass',
                'remark': '정상 동작 확인',
                'environment': 'dev',
                'deployment_date': date(2025, 8, 1),
                'folder_id': dev_dep1.id,
                'automation_code_path': 'test-scripts/clm/dev_draft_create.js',
                'automation_code_type': 'playwright'
            },
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Draft',
                'detail_category': 'Edit',
                'pre_condition': 'Draft 생성 완료',
                'description': 'DEV - CLM Draft 수정 테스트',
                'result_status': 'Fail',
                'remark': '수정 버튼 클릭 시 오류 발생',
                'environment': 'dev',
                'deployment_date': date(2025, 8, 3),
                'folder_id': dev_dep2.id,
                'automation_code_path': 'test-scripts/clm/dev_draft_edit.js',
                'automation_code_type': 'playwright'
            },
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'E-Sign',
                'detail_category': 'Sign',
                'pre_condition': 'Draft 완료',
                'description': 'DEV - CLM E-Sign 테스트',
                'result_status': 'Pass',
                'remark': '전자서명 정상 동작',
                'environment': 'dev',
                'deployment_date': date(2025, 8, 1),
                'folder_id': dev_dep1.id,
                'automation_code_path': 'test-scripts/clm/dev_esign.js',
                'automation_code_type': 'playwright'
            },
            
            # ALPHA 환경 테스트 케이스
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Draft',
                'detail_category': 'Create',
                'pre_condition': '로그인 완료',
                'description': 'ALPHA - CLM Draft 생성 테스트',
                'result_status': 'Pass',
                'remark': '정상 동작 확인',
                'environment': 'alpha',
                'deployment_date': date(2025, 8, 2),
                'folder_id': alpha_dep1.id,
                'automation_code_path': 'test-scripts/clm/alpha_draft_create.js',
                'automation_code_type': 'playwright'
            },
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Financial',
                'detail_category': 'Review',
                'pre_condition': 'Draft 생성 완료',
                'description': 'ALPHA - CLM Financial Review 테스트',
                'result_status': 'Pass',
                'remark': '재무 검토 정상 동작',
                'environment': 'alpha',
                'deployment_date': date(2025, 8, 2),
                'folder_id': alpha_dep1.id,
                'automation_code_path': 'test-scripts/clm/alpha_financial_review.js',
                'automation_code_type': 'playwright'
            },
            
            # PRODUCTION 환경 테스트 케이스
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Draft',
                'detail_category': 'Create',
                'pre_condition': '로그인 완료',
                'description': 'PRODUCTION - CLM Draft 생성 테스트',
                'result_status': 'Pass',
                'remark': '정상 동작 확인',
                'environment': 'production',
                'deployment_date': date(2025, 8, 1),
                'folder_id': prod_dep1.id,
                'automation_code_path': 'test-scripts/clm/prod_draft_create.js',
                'automation_code_type': 'playwright'
            },
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Final',
                'detail_category': 'Approve',
                'pre_condition': '모든 검토 완료',
                'description': 'PRODUCTION - CLM Final Approval 테스트',
                'result_status': 'Pass',
                'remark': '최종 승인 정상 동작',
                'environment': 'production',
                'deployment_date': date(2025, 8, 1),
                'folder_id': prod_dep1.id,
                'automation_code_path': 'test-scripts/clm/prod_final_approve.js',
                'automation_code_type': 'playwright'
            }
        ]
        
        for tc_data in test_cases:
            test_case = TestCase(**tc_data)
            db.session.add(test_case)
        
        db.session.commit()
        
        # 4. 테스트 결과 생성
        test_results = [
            # DEV 환경 결과
            {
                'test_case_id': 1,
                'result': 'Pass',
                'environment': 'dev',
                'execution_duration': 15.5,
                'notes': 'DEV 환경에서 정상 동작 확인'
            },
            {
                'test_case_id': 2,
                'result': 'Fail',
                'environment': 'dev',
                'execution_duration': 8.2,
                'error_message': '수정 버튼 클릭 시 JavaScript 오류 발생'
            },
            {
                'test_case_id': 3,
                'result': 'Pass',
                'environment': 'dev',
                'execution_duration': 12.1,
                'notes': '전자서명 기능 정상 동작'
            },
            
            # ALPHA 환경 결과
            {
                'test_case_id': 4,
                'result': 'Pass',
                'environment': 'alpha',
                'execution_duration': 14.3,
                'notes': 'ALPHA 환경에서 정상 동작 확인'
            },
            {
                'test_case_id': 5,
                'result': 'Pass',
                'environment': 'alpha',
                'execution_duration': 18.7,
                'notes': '재무 검토 기능 정상 동작'
            },
            
            # PRODUCTION 환경 결과
            {
                'test_case_id': 6,
                'result': 'Pass',
                'environment': 'production',
                'execution_duration': 16.2,
                'notes': 'PRODUCTION 환경에서 정상 동작 확인'
            },
            {
                'test_case_id': 7,
                'result': 'Pass',
                'environment': 'production',
                'execution_duration': 22.1,
                'notes': '최종 승인 기능 정상 동작'
            }
        ]
        
        for tr_data in test_results:
            test_result = TestResult(**tr_data)
            db.session.add(test_result)
        
        db.session.commit()
        
        # 5. 대시보드 요약 생성
        summaries = [
            {
                'environment': 'dev',
                'total_tests': 3,
                'passed_tests': 2,
                'failed_tests': 1,
                'skipped_tests': 0,
                'pass_rate': 66.67
            },
            {
                'environment': 'alpha',
                'total_tests': 2,
                'passed_tests': 2,
                'failed_tests': 0,
                'skipped_tests': 0,
                'pass_rate': 100.0
            },
            {
                'environment': 'production',
                'total_tests': 2,
                'passed_tests': 2,
                'failed_tests': 0,
                'skipped_tests': 0,
                'pass_rate': 100.0
            }
        ]
        
        for summary_data in summaries:
            summary = DashboardSummary(**summary_data)
            db.session.add(summary)
        
        db.session.commit()
        
        print("✅ 샘플 데이터 생성 완료!")
        print(f"📁 폴더: {Folder.query.count()}개")
        print(f"📋 테스트 케이스: {TestCase.query.count()}개")
        print(f"📊 테스트 결과: {TestResult.query.count()}개")
        print(f"📈 대시보드 요약: {DashboardSummary.query.count()}개")

if __name__ == "__main__":
    create_sample_data() 