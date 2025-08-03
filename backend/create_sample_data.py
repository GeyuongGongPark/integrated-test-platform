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
        db.session.add(dev_folder)
        
        alpha_folder = Folder(
            folder_name='ALPHA 환경',
            folder_type='environment',
            environment='alpha'
        )
        db.session.add(alpha_folder)
        
        prod_folder = Folder(
            folder_name='PRODUCTION 환경',
            folder_type='environment',
            environment='production'
        )
        db.session.add(prod_folder)
        
        db.session.commit()
        
        # 배포일자별 폴더
        dev_deploy1 = Folder(
            folder_name='2024-01-15',
            folder_type='deployment_date',
            environment='dev',
            deployment_date=date(2024, 1, 15),
            parent_folder_id=dev_folder.id
        )
        db.session.add(dev_deploy1)
        
        alpha_deploy1 = Folder(
            folder_name='2024-01-20',
            folder_type='deployment_date',
            environment='alpha',
            deployment_date=date(2024, 1, 20),
            parent_folder_id=alpha_folder.id
        )
        db.session.add(alpha_deploy1)
        
        prod_deploy1 = Folder(
            folder_name='2024-01-25',
            folder_type='deployment_date',
            environment='production',
            deployment_date=date(2024, 1, 25),
            parent_folder_id=prod_folder.id
        )
        db.session.add(prod_deploy1)
        
        db.session.commit()
        
        # 3. 테스트 케이스 생성
        test_cases = [
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Draft',
                'detail_category': '기안 작성',
                'pre_condition': '로그인 완료',
                'description': 'CLM 기안 작성 기능 테스트',
                'result_status': 'Pass',
                'environment': 'dev',
                'deployment_date': date(2024, 1, 15),
                'folder_id': dev_deploy1.id,
                'automation_code_path': 'test-scripts/clm/draft.js',
                'automation_code_type': 'playwright'
            },
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Review',
                'detail_category': '검토',
                'pre_condition': '기안 작성 완료',
                'description': 'CLM 검토 기능 테스트',
                'result_status': 'Fail',
                'environment': 'dev',
                'deployment_date': date(2024, 1, 15),
                'folder_id': dev_deploy1.id,
                'automation_code_path': 'test-scripts/clm/review.js',
                'automation_code_type': 'selenium'
            },
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Sign',
                'detail_category': '전자서명',
                'pre_condition': '검토 완료',
                'description': 'CLM 전자서명 기능 테스트',
                'result_status': 'Pass',
                'environment': 'dev',
                'deployment_date': date(2024, 1, 15),
                'folder_id': dev_deploy1.id,
                'automation_code_path': 'test-scripts/clm/sign.js',
                'automation_code_type': 'playwright'
            },
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Financial',
                'detail_category': '재무 검토',
                'pre_condition': 'ALPHA 환경 접속',
                'description': 'CLM 재무 검토 기능 테스트',
                'result_status': 'Pass',
                'environment': 'alpha',
                'deployment_date': date(2024, 1, 20),
                'folder_id': alpha_deploy1.id,
                'automation_code_path': 'test-scripts/clm/financial.js',
                'automation_code_type': 'k6'
            },
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Legal',
                'detail_category': '법무 검토',
                'pre_condition': 'ALPHA 환경 접속',
                'description': 'CLM 법무 검토 기능 테스트',
                'result_status': 'Pass',
                'environment': 'alpha',
                'deployment_date': date(2024, 1, 20),
                'folder_id': alpha_deploy1.id,
                'automation_code_path': 'test-scripts/clm/legal.js',
                'automation_code_type': 'selenium'
            },
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Final',
                'detail_category': '최종 승인',
                'pre_condition': 'PRODUCTION 환경 접속',
                'description': 'CLM 최종 승인 기능 테스트',
                'result_status': 'Pass',
                'environment': 'production',
                'deployment_date': date(2024, 1, 25),
                'folder_id': prod_deploy1.id,
                'automation_code_path': 'test-scripts/clm/final.js',
                'automation_code_type': 'playwright'
            },
            {
                'project_id': project.id,
                'main_category': 'CLM',
                'sub_category': 'Seal',
                'detail_category': '도장 찍기',
                'pre_condition': 'PRODUCTION 환경 접속',
                'description': 'CLM 도장 찍기 기능 테스트',
                'result_status': 'Pass',
                'environment': 'production',
                'deployment_date': date(2024, 1, 25),
                'folder_id': prod_deploy1.id,
                'automation_code_path': 'test-scripts/clm/seal.js',
                'automation_code_type': 'selenium'
            }
        ]
        
        created_test_cases = []
        for tc_data in test_cases:
            test_case = TestCase(**tc_data)
            db.session.add(test_case)
            created_test_cases.append(test_case)
        
        db.session.commit()
        
        # 4. 테스트 결과 생성 (TestCase ID를 실제 생성된 ID로 사용)
        test_results = [
            {
                'test_case_id': created_test_cases[0].id,
                'result': 'Pass',
                'environment': 'dev',
                'execution_duration': 15.5,
                'notes': 'DEV 환경에서 정상 동작 확인'
            },
            {
                'test_case_id': created_test_cases[1].id,
                'result': 'Fail',
                'environment': 'dev',
                'execution_duration': 8.2,
                'error_message': '수정 버튼 클릭 시 JavaScript 오류 발생'
            },
            {
                'test_case_id': created_test_cases[2].id,
                'result': 'Pass',
                'environment': 'dev',
                'execution_duration': 12.1,
                'notes': '전자서명 기능 정상 동작'
            },
            
            # ALPHA 환경 결과
            {
                'test_case_id': created_test_cases[3].id,
                'result': 'Pass',
                'environment': 'alpha',
                'execution_duration': 14.3,
                'notes': 'ALPHA 환경에서 정상 동작 확인'
            },
            {
                'test_case_id': created_test_cases[4].id,
                'result': 'Pass',
                'environment': 'alpha',
                'execution_duration': 18.7,
                'notes': '재무 검토 기능 정상 동작'
            },
            
            # PRODUCTION 환경 결과
            {
                'test_case_id': created_test_cases[5].id,
                'result': 'Pass',
                'environment': 'production',
                'execution_duration': 16.2,
                'notes': 'PRODUCTION 환경에서 정상 동작 확인'
            },
            {
                'test_case_id': created_test_cases[6].id,
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