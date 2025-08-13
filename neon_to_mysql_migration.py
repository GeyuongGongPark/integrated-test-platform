#!/usr/bin/env python3
"""
Neon DB에서 MySQL로 데이터 마이그레이션 스크립트
"""

import os
import psycopg
import pymysql
import json
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Neon DB 연결 정보 (환경 변수에서 가져오기)
NEON_DATABASE_URL = os.getenv('NEON_DATABASE_URL')

# MySQL 연결 정보
MYSQL_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '1q2w#E$R',
    'database': 'test_management',
    'charset': 'utf8mb4'
}

def connect_neon_db():
    """Neon DB에 연결"""
    try:
        neon_url = os.environ.get('NEON_DATABASE_URL') or NEON_DATABASE_URL
        if not neon_url:
            raise ValueError("NEON_DATABASE_URL 환경 변수가 설정되지 않았습니다.")
        
        conn = psycopg.connect(neon_url)
        print("✅ Neon DB 연결 성공")
        return conn
    except Exception as e:
        print(f"❌ Neon DB 연결 실패: {e}")
        return None

def connect_mysql_db():
    """MySQL DB에 연결"""
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        print("✅ MySQL DB 연결 성공")
        return conn
    except Exception as e:
        print(f"❌ MySQL DB 연결 실패: {e}")
        return None

def create_mysql_tables(mysql_conn):
    """MySQL에 테이블 생성"""
    cursor = mysql_conn.cursor()
    
    # 테이블 생성 SQL (실제 Neon DB 구조에 맞게 수정)
    tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS `projects` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(100) NOT NULL,
            `description` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS `Folders` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(100) NOT NULL,
            `parent_id` INT NULL,
            `project_id` INT NULL,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`parent_id`) REFERENCES `Folders`(`id`) ON DELETE SET NULL,
            FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS `TestCases` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(200) NOT NULL,
            `description` TEXT,
            `test_type` VARCHAR(50),
            `script_path` VARCHAR(500),
            `folder_id` INT NULL,
            
            # 원래 기획에 있던 필드들 추가
            `main_category` VARCHAR(100),
            `sub_category` VARCHAR(100),
            `detail_category` VARCHAR(100),
            `pre_condition` TEXT,
            `expected_result` TEXT,
            `remark` TEXT,
            `automation_code_path` VARCHAR(500),
            `environment` VARCHAR(50),
            
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (`folder_id`) REFERENCES `Folders`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS `test_result` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `test_case_id` INT NULL,
            `status` VARCHAR(20),
            `execution_time` FLOAT,
            `result_data` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`test_case_id`) REFERENCES `TestCases`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS `Screenshots` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `test_result_id` INT NULL,
            `file_path` VARCHAR(500),
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`test_result_id`) REFERENCES `test_result`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS `PerformanceTests` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(200) NOT NULL,
            `description` TEXT,
            `script_path` VARCHAR(500),
            `environment` VARCHAR(100),
            `parameters` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS `PerformanceTestResults` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `test_id` INT NULL,
            `status` VARCHAR(20),
            `execution_time` FLOAT,
            `result_data` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`test_id`) REFERENCES `PerformanceTests`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS `AutomationTests` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(200) NOT NULL,
            `description` TEXT,
            `test_type` VARCHAR(50),
            `script_path` VARCHAR(500),
            `environment` VARCHAR(100),
            `parameters` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS `AutomationTestResults` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `test_id` INT NULL,
            `status` VARCHAR(20),
            `execution_time` FLOAT,
            `result_data` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`test_id`) REFERENCES `AutomationTests`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS `TestExecutions` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `test_case_id` INT NULL,
            `status` VARCHAR(20),
            `execution_time` FLOAT,
            `result_data` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`test_case_id`) REFERENCES `TestCases`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        """
        CREATE TABLE IF NOT EXISTS `DashboardSummaries` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `summary_data` TEXT,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    ]
    
    try:
        for sql in tables_sql:
            cursor.execute(sql)
            print(f"✅ 테이블 생성 완료")
        
        mysql_conn.commit()
        print("✅ 모든 테이블 생성 완료")
        
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        mysql_conn.rollback()
    finally:
        cursor.close()

def migrate_data(neon_conn, mysql_conn):
    """데이터 마이그레이션 실행"""
    neon_cursor = neon_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    try:
        # 1. projects 테이블 마이그레이션
        print("\n🔄 projects 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, name, description FROM "projects"')
        projects = neon_cursor.fetchall()
        
        for project in projects:
            mysql_cursor.execute("""
                INSERT INTO `projects` (name, description) 
                VALUES (%s, %s)
            """, (project[1], project[2]))
        
        print(f"✅ projects 테이블: {len(projects)}개 레코드 마이그레이션 완료")
        
        # 2. Folders 테이블 마이그레이션
        print("\n🔄 Folders 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, folder_name, parent_folder_id, project_id, created_at FROM "Folders"')
        folders = neon_cursor.fetchall()
        
        for folder in folders:
            mysql_cursor.execute("""
                INSERT INTO `Folders` (id, name, parent_id, project_id, created_at) 
                VALUES (%s, %s, %s, %s, %s)
            """, folder)
        
        print(f"✅ Folders 테이블: {len(folders)}개 레코드 마이그레이션 완료")
        
        # 3. TestCases 테이블 마이그레이션
        print("\n🔄 TestCases 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, project_id, main_category, sub_category, detail_category, pre_condition, result_status, remark, created_at, updated_at, environment, deployment_date, folder_id, automation_code_path, automation_code_type, expected_result FROM "TestCases"')
        test_cases = neon_cursor.fetchall()
        
        for test_case in test_cases:
            mysql_cursor.execute("""
                INSERT INTO `TestCases` (id, name, description, test_type, script_path, folder_id, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                test_case[0],  # id
                f"{test_case[2]}/{test_case[3]}/{test_case[4]}" if test_case[2] and test_case[3] and test_case[4] else "Test Case",  # name (카테고리 조합)
                test_case[5] or "",  # description (pre_condition)
                test_case[15] or "Unknown",  # test_type (automation_code_type)
                test_case[13] or "",  # script_path (automation_code_path)
                test_case[12],  # folder_id
                test_case[8],  # created_at
                test_case[9]  # updated_at
            ))
        
        print(f"✅ TestCases 테이블: {len(test_cases)}개 레코드 마이그레이션 완료")
        
        # 4. test_result 테이블 마이그레이션
        print("\n🔄 test_result 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, test_case_id, result, executed_at, notes, screenshot, environment, execution_duration, error_message FROM "test_result"')
        test_results = neon_cursor.fetchall()
        
        for test_result in test_results:
            mysql_cursor.execute("""
                INSERT INTO `test_result` (id, test_case_id, status, execution_time, result_data, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                test_result[0],  # id
                test_result[1],  # test_case_id
                test_result[2] or "Unknown",  # status (result)
                test_result[7] or 0.0,  # execution_time (execution_duration)
                f"Notes: {test_result[4] or ''}, Screenshot: {test_result[5] or ''}, Environment: {test_result[6] or ''}, Error: {test_result[8] or ''}",  # result_data (조합)
                test_result[3]  # created_at (executed_at)
            ))
        
        print(f"✅ test_result 테이블: {len(test_results)}개 레코드 마이그레이션 완료")
        
        # 5. Screenshots 테이블 마이그레이션
        print("\n🔄 Screenshots 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, test_case_id, screenshot_path, timestamp FROM "Screenshots"')
        screenshots = neon_cursor.fetchall()
        
        for screenshot in screenshots:
            mysql_cursor.execute("""
                INSERT INTO `Screenshots` (id, test_result_id, file_path, created_at) 
                VALUES (%s, %s, %s, %s)
            """, (
                screenshot[0],  # id
                screenshot[1],  # test_result_id (test_case_id로 매핑)
                screenshot[2],  # file_path (screenshot_path)
                screenshot[3]   # created_at (timestamp)
            ))
        
        print(f"✅ Screenshots 테이블: {len(screenshots)}개 레코드 마이그레이션 완료")
        
        # 6. PerformanceTests 테이블 마이그레이션
        print("\n🔄 PerformanceTests 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, name, description, k6_script_path, environment, parameters, created_at, updated_at FROM "PerformanceTests"')
        performance_tests = neon_cursor.fetchall()
        
        for perf_test in performance_tests:
            mysql_cursor.execute("""
                INSERT INTO `PerformanceTests` (id, name, description, script_path, environment, parameters, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, perf_test)
        
        print(f"✅ PerformanceTests 테이블: {len(performance_tests)}개 레코드 마이그레이션 완료")
        
        # 7. PerformanceTestResults 테이블 마이그레이션
        print("\n🔄 PerformanceTestResults 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, performance_test_id, status, execution_start, execution_end, execution_duration, output, error_message, result_data, environment, notes FROM "PerformanceTestResults"')
        perf_results = neon_cursor.fetchall()
        
        for perf_result in perf_results:
            mysql_cursor.execute("""
                INSERT INTO `PerformanceTestResults` (id, test_id, status, execution_time, result_data, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                perf_result[0],  # id
                perf_result[1],  # test_id (performance_test_id)
                perf_result[2] or "Unknown",  # status
                perf_result[5] or 0.0,  # execution_time (execution_duration)
                f"Output: {perf_result[6] or ''}, Error: {perf_result[7] or ''}, Data: {perf_result[8] or ''}, Environment: {perf_result[9] or ''}, Notes: {perf_result[10] or ''}",  # result_data (조합)
                perf_result[3]  # created_at (execution_start)
            ))
        
        print(f"✅ PerformanceTestResults 테이블: {len(perf_results)}개 레코드 마이그레이션 완료")
        
        # 8. AutomationTests 테이블 마이그레이션
        print("\n🔄 AutomationTests 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, name, description, script_path, created_at, updated_at FROM "AutomationTests"')
        automation_tests = neon_cursor.fetchall()
        
        for auto_test in automation_tests:
            mysql_cursor.execute("""
                INSERT INTO `AutomationTests` (id, name, description, test_type, script_path, environment, parameters, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                auto_test[0],  # id
                auto_test[1],  # name
                auto_test[2] or "",  # description
                "Automation",  # test_type (기본값)
                auto_test[3] or "",  # script_path
                "Default",  # environment (기본값)
                "",  # parameters (빈 문자열)
                auto_test[4],  # created_at
                auto_test[5]   # updated_at
            ))
        
        print(f"✅ AutomationTests 테이블: {len(automation_tests)}개 레코드 마이그레이션 완료")
        
        # 9. AutomationTestResults 테이블 마이그레이션
        print("\n🔄 AutomationTestResults 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, automation_test_id, status, execution_start, execution_end, execution_duration, output, error_message, screenshot_path, result_data, environment, notes FROM "AutomationTestResults"')
        auto_results = neon_cursor.fetchall()
        
        for auto_result in auto_results:
            mysql_cursor.execute("""
                INSERT INTO `AutomationTestResults` (id, test_id, status, execution_time, result_data, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                auto_result[0],  # id
                auto_result[1],  # test_id (automation_test_id)
                auto_result[2] or "Unknown",  # status
                auto_result[5] or 0.0,  # execution_time (execution_duration)
                f"Output: {auto_result[6] or ''}, Error: {auto_result[7] or ''}, Screenshot: {auto_result[8] or ''}, Data: {auto_result[9] or ''}, Environment: {auto_result[10] or ''}, Notes: {auto_result[11] or ''}",  # result_data (조합)
                auto_result[3]  # created_at (execution_start)
            ))
        
        print(f"✅ AutomationTestResults 테이블: {len(auto_results)}개 레코드 마이그레이션 완료")
        
        # 10. TestExecutions 테이블 마이그레이션
        print("\n🔄 TestExecutions 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, test_case_id, performance_test_id, test_type, execution_start, execution_end, status, result_data, report_path FROM "TestExecutions"')
        test_executions = neon_cursor.fetchall()
        
        for test_execution in test_executions:
            # execution_duration 계산
            execution_duration = 0.0
            if test_execution[4] and test_execution[5]:  # execution_start와 execution_end가 모두 있는 경우
                duration = test_execution[5] - test_execution[4]
                execution_duration = duration.total_seconds()
            
            mysql_cursor.execute("""
                INSERT INTO `TestExecutions` (id, test_case_id, status, execution_time, result_data, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                test_execution[0],  # id
                test_execution[1],  # test_case_id
                test_execution[6] or "Unknown",  # status
                execution_duration,  # execution_time (계산된 duration)
                f"Type: {test_execution[3] or ''}, Data: {test_execution[7] or ''}, Report: {test_execution[8] or ''}",  # result_data (조합)
                test_execution[4]  # created_at (execution_start)
            ))
        
        print(f"✅ TestExecutions 테이블: {len(test_executions)}개 레코드 마이그레이션 완료")
        
        # 11. DashboardSummaries 테이블 마이그레이션
        print("\n🔄 DashboardSummaries 테이블 마이그레이션 시작...")
        neon_cursor.execute('SELECT id, total_tests, passed_tests, failed_tests, not_tested, last_updated FROM "DashboardSummaries"')
        dashboard_summaries = neon_cursor.fetchall()
        
        for dashboard_summary in dashboard_summaries:
            mysql_cursor.execute("""
                INSERT INTO `DashboardSummaries` (id, summary_data, created_at) 
                VALUES (%s, %s, %s)
            """, (
                dashboard_summary[0],  # id
                f"Total: {dashboard_summary[1]}, Passed: {dashboard_summary[2]}, Failed: {dashboard_summary[3]}, Not Tested: {dashboard_summary[4]}",  # summary_data (조합)
                dashboard_summary[5]   # created_at (last_updated)
            ))
        
        print(f"✅ DashboardSummaries 테이블: {len(dashboard_summaries)}개 레코드 마이그레이션 완료")
        
        mysql_conn.commit()
        print("\n🎉 모든 데이터 마이그레이션 완료!")
        
    except Exception as e:
        print(f"❌ 데이터 마이그레이션 실패: {e}")
        mysql_conn.rollback()
    finally:
        neon_cursor.close()
        mysql_cursor.close()

def verify_migration(mysql_conn):
    """마이그레이션 결과 검증"""
    cursor = mysql_conn.cursor()
    
    tables = [
        'projects', 'Folders', 'TestCases', 'test_result', 'Screenshots',
        'PerformanceTests', 'PerformanceTestResults', 'AutomationTests', 
        'AutomationTestResults', 'TestExecutions', 'DashboardSummaries'
    ]
    
    print("\n🔍 마이그레이션 결과 검증:")
    print("-" * 50)
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            print(f"✅ {table}: {count}개 레코드")
        except Exception as e:
            print(f"❌ {table}: 검증 실패 - {e}")
    
    cursor.close()

def main():
    """메인 함수"""
    print("🚀 Neon DB에서 MySQL로 마이그레이션을 시작합니다...")
    print("=" * 60)
    
    # Neon DB 연결
    neon_conn = connect_neon_db()
    if not neon_conn:
        print("❌ Neon DB 연결 실패로 마이그레이션을 중단합니다.")
        return
    
    # MySQL DB 연결
    mysql_conn = connect_mysql_db()
    if not mysql_conn:
        print("❌ MySQL DB 연결 실패로 마이그레이션을 중단합니다.")
        neon_conn.close()
        return
    
    try:
        # 1. MySQL 테이블 생성
        print("\n📋 MySQL 테이블 생성 중...")
        create_mysql_tables(mysql_conn)
        
        # 2. 데이터 마이그레이션
        print("\n🔄 데이터 마이그레이션 중...")
        migrate_data(neon_conn, mysql_conn)
        
        # 3. 마이그레이션 결과 검증
        verify_migration(mysql_conn)
        
        print("\n🎉 마이그레이션이 성공적으로 완료되었습니다!")
        print("\n📝 다음 단계:")
        print("1. 백엔드 앱을 재시작하세요")
        print("2. 환경 변수 DATABASE_URL을 MySQL 연결 문자열로 업데이트하세요")
        print("3. Flask-Migrate로 데이터베이스 스키마를 동기화하세요")
        
    except Exception as e:
        print(f"❌ 마이그레이션 중 오류 발생: {e}")
    finally:
        neon_conn.close()
        mysql_conn.close()
        print("\n🔌 데이터베이스 연결을 종료했습니다.")

if __name__ == "__main__":
    main()
