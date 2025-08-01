#!/usr/bin/env python3
"""
SQLite에서 MySQL로 데이터 마이그레이션 스크립트
"""

import sqlite3
import pymysql
import json
from datetime import datetime

def connect_sqlite():
    """SQLite 데이터베이스 연결"""
    return sqlite3.connect('test_management.db')

def connect_mysql():
    """MySQL 데이터베이스 연결"""
    return pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        database='testmanager',
        charset='utf8mb4'
    )

def migrate_projects():
    """프로젝트 데이터 마이그레이션"""
    print("프로젝트 데이터 마이그레이션 시작...")
    
    sqlite_conn = connect_sqlite()
    mysql_conn = connect_mysql()
    
    try:
        # SQLite에서 프로젝트 데이터 조회
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT id, name, description FROM projects")
        projects = cursor.fetchall()
        
        # MySQL에 프로젝트 데이터 삽입
        mysql_cursor = mysql_conn.cursor()
        for project in projects:
            mysql_cursor.execute(
                "INSERT INTO projects (id, name, description) VALUES (%s, %s, %s)",
                project
            )
        
        mysql_conn.commit()
        print(f"✅ {len(projects)}개의 프로젝트 마이그레이션 완료")
        
    except Exception as e:
        print(f"❌ 프로젝트 마이그레이션 오류: {e}")
    finally:
        sqlite_conn.close()
        mysql_conn.close()

def migrate_test_cases():
    """테스트 케이스 데이터 마이그레이션"""
    print("테스트 케이스 데이터 마이그레이션 시작...")
    
    sqlite_conn = connect_sqlite()
    mysql_conn = connect_mysql()
    
    try:
        # SQLite에서 테스트 케이스 데이터 조회
        cursor = sqlite_conn.cursor()
        cursor.execute("""
            SELECT id, project_id, main_category, sub_category, detail_category, 
                   pre_condition, description, result_status, remark, created_at, updated_at 
            FROM TestCases
        """)
        test_cases = cursor.fetchall()
        
        # MySQL에 테스트 케이스 데이터 삽입
        mysql_cursor = mysql_conn.cursor()
        for test_case in test_cases:
            mysql_cursor.execute("""
                INSERT INTO TestCases (id, project_id, main_category, sub_category, detail_category,
                                     pre_condition, description, result_status, remark, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, test_case)
        
        mysql_conn.commit()
        print(f"✅ {len(test_cases)}개의 테스트 케이스 마이그레이션 완료")
        
    except Exception as e:
        print(f"❌ 테스트 케이스 마이그레이션 오류: {e}")
    finally:
        sqlite_conn.close()
        mysql_conn.close()

def migrate_test_results():
    """테스트 결과 데이터 마이그레이션"""
    print("테스트 결과 데이터 마이그레이션 시작...")
    
    sqlite_conn = connect_sqlite()
    mysql_conn = connect_mysql()
    
    try:
        # SQLite에서 테스트 결과 데이터 조회
        cursor = sqlite_conn.cursor()
        cursor.execute("""
            SELECT id, test_case_id, result, executed_at, notes, screenshot 
            FROM test_result
        """)
        test_results = cursor.fetchall()
        
        # MySQL에 테스트 결과 데이터 삽입
        mysql_cursor = mysql_conn.cursor()
        for test_result in test_results:
            mysql_cursor.execute("""
                INSERT INTO test_result (id, test_case_id, result, executed_at, notes, screenshot)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, test_result)
        
        mysql_conn.commit()
        print(f"✅ {len(test_results)}개의 테스트 결과 마이그레이션 완료")
        
    except Exception as e:
        print(f"❌ 테스트 결과 마이그레이션 오류: {e}")
    finally:
        sqlite_conn.close()
        mysql_conn.close()

def migrate_folders():
    """폴더 데이터 마이그레이션"""
    print("폴더 데이터 마이그레이션 시작...")
    
    sqlite_conn = connect_sqlite()
    mysql_conn = connect_mysql()
    
    try:
        # SQLite에서 폴더 데이터 조회
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT id, folder_name, parent_folder_id FROM Folders")
        folders = cursor.fetchall()
        
        # MySQL에 폴더 데이터 삽입
        mysql_cursor = mysql_conn.cursor()
        for folder in folders:
            mysql_cursor.execute("""
                INSERT INTO Folders (id, folder_name, parent_folder_id)
                VALUES (%s, %s, %s)
            """, folder)
        
        mysql_conn.commit()
        print(f"✅ {len(folders)}개의 폴더 마이그레이션 완료")
        
    except Exception as e:
        print(f"❌ 폴더 마이그레이션 오류: {e}")
    finally:
        sqlite_conn.close()
        mysql_conn.close()

def migrate_screenshots():
    """스크린샷 데이터 마이그레이션"""
    print("스크린샷 데이터 마이그레이션 시작...")
    
    sqlite_conn = connect_sqlite()
    mysql_conn = connect_mysql()
    
    try:
        # SQLite에서 스크린샷 데이터 조회
        cursor = sqlite_conn.cursor()
        cursor.execute("""
            SELECT id, test_case_id, screenshot_path, timestamp 
            FROM Screenshots
        """)
        screenshots = cursor.fetchall()
        
        # MySQL에 스크린샷 데이터 삽입
        mysql_cursor = mysql_conn.cursor()
        for screenshot in screenshots:
            mysql_cursor.execute("""
                INSERT INTO Screenshots (id, test_case_id, screenshot_path, timestamp)
                VALUES (%s, %s, %s, %s)
            """, screenshot)
        
        mysql_conn.commit()
        print(f"✅ {len(screenshots)}개의 스크린샷 마이그레이션 완료")
        
    except Exception as e:
        print(f"❌ 스크린샷 마이그레이션 오류: {e}")
    finally:
        sqlite_conn.close()
        mysql_conn.close()

def check_sqlite_data():
    """SQLite 데이터 확인"""
    print("SQLite 데이터 확인 중...")
    
    sqlite_conn = connect_sqlite()
    cursor = sqlite_conn.cursor()
    
    try:
        # 테이블 목록 조회
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 SQLite 테이블 목록: {[table[0] for table in tables]}")
        
        # 각 테이블의 데이터 개수 확인
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count}개 데이터")
            
    except Exception as e:
        print(f"❌ SQLite 데이터 확인 오류: {e}")
    finally:
        sqlite_conn.close()

def main():
    """메인 마이그레이션 함수"""
    print("🚀 SQLite → MySQL 데이터 마이그레이션 시작")
    print("=" * 50)
    
    # SQLite 데이터 확인
    check_sqlite_data()
    print()
    
    # 각 테이블별 마이그레이션 실행
    migrate_projects()
    migrate_test_cases()
    migrate_test_results()
    migrate_folders()
    migrate_screenshots()
    
    print("=" * 50)
    print("✅ 마이그레이션 완료!")
    print("이제 MySQL 데이터베이스를 사용합니다.")

if __name__ == "__main__":
    main() 