#!/usr/bin/env python3
"""
샘플 데이터 생성 스크립트
"""

from app import app, db, Project, TestCase, Folder, TestResult, DashboardSummary, User
from datetime import datetime, date
import json
import random

def create_sample_data():
    """샘플 데이터 생성"""
    with app.app_context():
        print("샘플 데이터 생성 시작...")
        
        try:
            # 기존 데이터 삭제
            db.session.query(DashboardSummary).delete()
            db.session.query(TestResult).delete()
            db.session.query(TestCase).delete()
            db.session.query(Folder).delete()
            db.session.query(Project).delete()
            db.session.query(User).delete()
            
            # 사용자 생성
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash='admin123',  # 실제로는 해시된 비밀번호
                role='Administrator',
                is_active=True
            )
            
            user1 = User(
                username='user1',
                email='user1@example.com',
                password_hash='user123',
                role='User',
                is_active=True
            )
            
            user2 = User(
                username='user2',
                email='user2@example.com',
                password_hash='user123',
                role='User',
                is_active=True
            )
            
            db.session.add_all([admin_user, user1, user2])
            db.session.commit()
            
            # 프로젝트 생성
            project = Project(
                name='Test Management System',
                description='통합 테스트 관리 시스템'
            )
            db.session.add(project)
            db.session.commit()
            
            # 폴더 생성
            dev_folder = Folder(
                folder_name='DEV',
                folder_type='environment',
                environment='dev'
            )
            
            alpha_folder = Folder(
                folder_name='ALPHA',
                folder_type='environment',
                environment='alpha'
            )
            
            prod_folder = Folder(
                folder_name='PRODUCTION',
                folder_type='environment',
                environment='production'
            )
            
            db.session.add_all([dev_folder, alpha_folder, prod_folder])
            db.session.commit()
            
            # 배포일자 폴더 생성
            dev_deploy1 = Folder(
                folder_name='2024-01-15',
                folder_type='deployment_date',
                environment='dev',
                parent_folder_id=dev_folder.id,
                deployment_date=datetime(2024, 1, 15).date()
            )
            
            dev_deploy2 = Folder(
                folder_name='2024-01-20',
                folder_type='deployment_date',
                environment='dev',
                parent_folder_id=dev_folder.id,
                deployment_date=datetime(2024, 1, 20).date()
            )
            
            alpha_deploy1 = Folder(
                folder_name='2024-01-10',
                folder_type='deployment_date',
                environment='alpha',
                parent_folder_id=alpha_folder.id,
                deployment_date=datetime(2024, 1, 10).date()
            )
            
            prod_deploy1 = Folder(
                folder_name='2024-01-05',
                folder_type='deployment_date',
                environment='production',
                parent_folder_id=prod_folder.id,
                deployment_date=datetime(2024, 1, 5).date()
            )
            
            db.session.add_all([dev_deploy1, dev_deploy2, alpha_deploy1, prod_deploy1])
            db.session.commit()
            
            # 테스트 케이스 생성
            testcases = [
                TestCase(
                    project_id=project.id,
                    main_category='로그인',
                    sub_category='일반 로그인',
                    detail_category='정상 로그인',
                    pre_condition='유효한 계정 정보가 있다',
                    expected_result='로그인이 성공한다',
                    result_status='Pass',
                    environment='dev',
                    folder_id=dev_deploy1.id
                ),
                TestCase(
                    project_id=project.id,
                    main_category='로그인',
                    sub_category='일반 로그인',
                    detail_category='잘못된 비밀번호',
                    pre_condition='잘못된 비밀번호를 입력한다',
                    expected_result='로그인 실패 메시지가 표시된다',
                    result_status='Fail',
                    environment='dev',
                    folder_id=dev_deploy1.id
                ),
                TestCase(
                    project_id=project.id,
                    main_category='대시보드',
                    sub_category='데이터 표시',
                    detail_category='차트 렌더링',
                    pre_condition='대시보드 페이지에 접속한다',
                    expected_result='차트가 정상적으로 표시된다',
                    result_status='Pass',
                    environment='dev',
                    folder_id=dev_deploy2.id
                ),
                TestCase(
                    project_id=project.id,
                    main_category='사용자 관리',
                    sub_category='사용자 추가',
                    detail_category='새 사용자 생성',
                    pre_condition='관리자 권한으로 접속한다',
                    expected_result='새 사용자가 생성된다',
                    result_status='Pass',
                    environment='alpha',
                    folder_id=alpha_deploy1.id
                ),
                TestCase(
                    project_id=project.id,
                    main_category='사용자 관리',
                    sub_category='권한 관리',
                    detail_category='역할 변경',
                    pre_condition='사용자 정보를 수정한다',
                    expected_result='역할이 변경된다',
                    result_status='Pass',
                    environment='alpha',
                    folder_id=alpha_deploy1.id
                ),
                TestCase(
                    project_id=project.id,
                    main_category='보고서',
                    sub_category='테스트 결과',
                    detail_category='결과 내보내기',
                    pre_condition='테스트 결과가 있다',
                    expected_result='엑셀 파일이 다운로드된다',
                    result_status='Pass',
                    environment='production',
                    folder_id=prod_deploy1.id
                ),
                TestCase(
                    project_id=project.id,
                    main_category='보고서',
                    sub_category='통계',
                    detail_category='성공률 계산',
                    pre_condition='테스트 데이터가 있다',
                    expected_result='성공률이 정확히 계산된다',
                    result_status='Pass',
                    environment='production',
                    folder_id=prod_deploy1.id
                )
            ]
            
            db.session.add_all(testcases)
            db.session.commit()
            
            # 테스트 결과 생성
            for tc in testcases:
                result = TestResult(
                    test_case_id=tc.id,
                    result=tc.result_status,
                    environment=tc.environment,
                    executed_at=datetime.utcnow(),
                    execution_duration=random.uniform(1.0, 5.0)
                )
                db.session.add(result)
            
            db.session.commit()
            
            # 대시보드 요약 생성
            summaries = [
                DashboardSummary(
                    environment='dev',
                    total_tests=3,
                    passed_tests=2,
                    failed_tests=1,
                    skipped_tests=0,
                    pass_rate=66.67
                ),
                DashboardSummary(
                    environment='alpha',
                    total_tests=2,
                    passed_tests=2,
                    failed_tests=0,
                    skipped_tests=0,
                    pass_rate=100.0
                ),
                DashboardSummary(
                    environment='production',
                    total_tests=2,
                    passed_tests=2,
                    failed_tests=0,
                    skipped_tests=0,
                    pass_rate=100.0
                )
            ]
            
            db.session.add_all(summaries)
            db.session.commit()
            
            print("✅ 샘플 데이터 생성 완료!")
            print(f"👥 사용자: {len([admin_user, user1, user2])}개")
            print(f"📁 폴더: {len([dev_folder, alpha_folder, prod_folder, dev_deploy1, dev_deploy2, alpha_deploy1, prod_deploy1])}개")
            print(f"📋 테스트 케이스: {len(testcases)}개")
            print(f"📊 테스트 결과: {len(testcases)}개")
            print(f"📈 대시보드 요약: {len(summaries)}개")
            
        except Exception as e:
            print(f"❌ 샘플 데이터 생성 중 오류 발생: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    create_sample_data() 