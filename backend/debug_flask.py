#!/usr/bin/env python3
"""
Flask 애플리케이션 데이터 디버그 스크립트
"""

import os
from dotenv import load_dotenv
from app import app, db, TestCase, Project, TestResult

# 환경 변수 로드
load_dotenv()

def debug_data():
    """Flask 애플리케이션에서 데이터 확인"""
    print("🔍 Flask 애플리케이션 데이터 확인 중...")
    
    with app.app_context():
        # 데이터베이스 URI 확인
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        print(f"📊 데이터베이스 URI: {db_uri}")
        
        # TestCase 데이터 확인
        try:
            test_cases = TestCase.query.all()
            print(f"\n🧪 TestCase 데이터: {len(test_cases)}개")
            for tc in test_cases:
                print(f"  - ID: {tc.id}, 프로젝트: {tc.project_id}, 카테고리: {tc.main_category}/{tc.sub_category}/{tc.detail_category}, 상태: {tc.result_status}")
        except Exception as e:
            print(f"❌ TestCase 조회 오류: {e}")
        
        # Project 데이터 확인
        try:
            projects = Project.query.all()
            print(f"\n📋 Project 데이터: {len(projects)}개")
            for p in projects:
                print(f"  - ID: {p.id}, 이름: {p.name}, 설명: {p.description}")
        except Exception as e:
            print(f"❌ Project 조회 오류: {e}")
        
        # TestResult 데이터 확인
        try:
            test_results = TestResult.query.all()
            print(f"\n📈 TestResult 데이터: {len(test_results)}개")
            for tr in test_results:
                print(f"  - ID: {tr.id}, 테스트케이스: {tr.test_case_id}, 결과: {tr.result}, 실행시간: {tr.executed_at}")
        except Exception as e:
            print(f"❌ TestResult 조회 오류: {e}")
        
        # 모든 테이블 목록 확인
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\n📋 Flask에서 인식하는 테이블 목록:")
            for table in tables:
                print(f"  - {table}")
        except Exception as e:
            print(f"❌ 테이블 목록 조회 오류: {e}")

if __name__ == "__main__":
    debug_data() 