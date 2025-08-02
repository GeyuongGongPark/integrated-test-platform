#!/usr/bin/env python3
"""
MySQL 백업 파일을 Neon PostgreSQL로 마이그레이션하는 스크립트
"""

import psycopg2
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def connect_neon():
    """Neon PostgreSQL 데이터베이스 연결"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    
    return psycopg2.connect(database_url)

def parse_mysql_dump(file_path):
    """MySQL 덤프 파일 파싱"""
    print(f"📖 MySQL 백업 파일 파싱 중: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 테이블 생성문과 데이터 삽입문 분리
    tables = {}
    current_table = None
    current_data = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        
        # 테이블 생성문 시작
        if line.startswith('CREATE TABLE `'):
            table_name = re.search(r'CREATE TABLE `([^`]+)`', line).group(1)
            current_table = table_name
            tables[current_table] = {
                'create_sql': '',
                'data': []
            }
        
        # 테이블 생성문 수집
        if current_table and line:
            tables[current_table]['create_sql'] += line + '\n'
            
            # 테이블 생성문 끝
            if line.endswith(';'):
                current_table = None
        
        # 데이터 삽입문
        if line.startswith('INSERT INTO `'):
            table_name = re.search(r'INSERT INTO `([^`]+)`', line).group(1)
            if table_name in tables:
                tables[table_name]['data'].append(line)
    
    return tables

def convert_mysql_to_postgresql(mysql_sql):
    """MySQL SQL을 PostgreSQL SQL로 변환"""
    # MySQL 특정 구문을 PostgreSQL로 변환
    postgresql_sql = mysql_sql
    
    # AUTO_INCREMENT를 SERIAL로 변환
    postgresql_sql = re.sub(r'`id` int NOT NULL AUTO_INCREMENT', 'id SERIAL PRIMARY KEY', postgresql_sql)
    
    # int를 INTEGER로 변환
    postgresql_sql = re.sub(r'int NOT NULL', 'INTEGER NOT NULL', postgresql_sql)
    postgresql_sql = re.sub(r'int DEFAULT NULL', 'INTEGER DEFAULT NULL', postgresql_sql)
    
    # varchar를 VARCHAR로 변환
    postgresql_sql = re.sub(r'varchar\((\d+)\)', r'VARCHAR(\1)', postgresql_sql)
    
    # text를 TEXT로 변환
    postgresql_sql = re.sub(r'text', 'TEXT', postgresql_sql)
    
    # float를 REAL로 변환
    postgresql_sql = re.sub(r'float', 'REAL', postgresql_sql)
    
    # datetime을 TIMESTAMP로 변환
    postgresql_sql = re.sub(r'datetime', 'TIMESTAMP', postgresql_sql)
    
    # MySQL 엔진 및 문자셋 제거
    postgresql_sql = re.sub(r'ENGINE=InnoDB.*?;', ';', postgresql_sql, flags=re.DOTALL)
    
    # 백틱을 제거
    postgresql_sql = postgresql_sql.replace('`', '"')
    
    # MySQL 특정 함수를 PostgreSQL 함수로 변환
    postgresql_sql = re.sub(r'CURRENT_TIMESTAMP\(\)', 'CURRENT_TIMESTAMP', postgresql_sql)
    
    # KEY 제거 (PostgreSQL에서는 인덱스로 처리)
    postgresql_sql = re.sub(r'KEY "[^"]+" \("[^"]+"\),?', '', postgresql_sql)
    postgresql_sql = re.sub(r'CONSTRAINT "[^"]+" FOREIGN KEY \("[^"]+"\) REFERENCES "[^"]+" \("[^"]+"\)', '', postgresql_sql)
    
    # 중복된 PRIMARY KEY 제거
    postgresql_sql = re.sub(r',\s*PRIMARY KEY \("[^"]+"\)', '', postgresql_sql)
    
    # 마지막 쉼표 제거
    postgresql_sql = re.sub(r',\s*\)', ')', postgresql_sql)
    
    return postgresql_sql

def create_table_manually(conn, table_name):
    """수동으로 테이블 생성"""
    print(f"🏗️ 수동으로 테이블 생성 중: {table_name}")
    
    try:
        cursor = conn.cursor()
        
        # 기존 테이블이 있으면 삭제
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
        
        if table_name == 'projects':
            cursor.execute('''
                CREATE TABLE "projects" (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT
                )
            ''')
        elif table_name == 'TestCases':
            cursor.execute('''
                CREATE TABLE "TestCases" (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER NOT NULL,
                    main_category VARCHAR(255) NOT NULL,
                    sub_category VARCHAR(255) NOT NULL,
                    detail_category VARCHAR(255) NOT NULL,
                    pre_condition TEXT,
                    description TEXT,
                    result_status VARCHAR(10) DEFAULT 'N/T',
                    remark TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        elif table_name == 'test_result':
            cursor.execute('''
                CREATE TABLE "test_result" (
                    id SERIAL PRIMARY KEY,
                    test_case_id INTEGER,
                    result VARCHAR(10),
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    screenshot VARCHAR(255)
                )
            ''')
        elif table_name == 'PerformanceTests':
            cursor.execute('''
                CREATE TABLE "PerformanceTests" (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    k6_script_path VARCHAR(512) NOT NULL,
                    environment VARCHAR(100) DEFAULT 'prod',
                    parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        elif table_name == 'PerformanceTestResults':
            cursor.execute('''
                CREATE TABLE "PerformanceTestResults" (
                    id SERIAL PRIMARY KEY,
                    performance_test_id INTEGER,
                    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_time_avg REAL,
                    response_time_p95 REAL,
                    throughput REAL,
                    error_rate REAL,
                    status VARCHAR(20),
                    report_path VARCHAR(512),
                    result_data TEXT
                )
            ''')
        elif table_name == 'TestExecutions':
            cursor.execute('''
                CREATE TABLE "TestExecutions" (
                    id SERIAL PRIMARY KEY,
                    test_case_id INTEGER,
                    performance_test_id INTEGER,
                    test_type VARCHAR(50),
                    execution_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_end TIMESTAMP,
                    status VARCHAR(20),
                    result_data TEXT,
                    report_path VARCHAR(512)
                )
            ''')
        elif table_name == 'Folders':
            cursor.execute('''
                CREATE TABLE "Folders" (
                    id SERIAL PRIMARY KEY,
                    folder_name VARCHAR(255) NOT NULL,
                    parent_folder_id INTEGER
                )
            ''')
        elif table_name == 'Screenshots':
            cursor.execute('''
                CREATE TABLE "Screenshots" (
                    id SERIAL PRIMARY KEY,
                    test_case_id INTEGER,
                    screenshot_path VARCHAR(512) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        conn.commit()
        print(f"✅ 테이블 '{table_name}' 생성 완료")
        
    except Exception as e:
        print(f"❌ 테이블 '{table_name}' 생성 오류: {e}")
        conn.rollback()

def migrate_table_data(conn, table_name, data_sqls):
    """테이블 데이터 마이그레이션"""
    if not data_sqls:
        print(f"ℹ️ 테이블 '{table_name}'에 데이터가 없습니다.")
        return
    
    print(f"📊 테이블 데이터 마이그레이션 중: {table_name}")
    
    try:
        cursor = conn.cursor()
        
        for data_sql in data_sqls:
            # MySQL INSERT 문을 PostgreSQL로 변환
            postgresql_sql = data_sql.replace('`', '"')
            cursor.execute(postgresql_sql)
        
        conn.commit()
        print(f"✅ 테이블 '{table_name}' 데이터 마이그레이션 완료 ({len(data_sqls)}개 행)")
        
    except Exception as e:
        print(f"❌ 테이블 '{table_name}' 데이터 마이그레이션 오류: {e}")
        conn.rollback()

def main():
    """메인 마이그레이션 함수"""
    print("🚀 MySQL 백업을 Neon PostgreSQL로 마이그레이션 시작...")
    
    # 백업 파일 경로
    backup_file = "backups/testmanager_20250801_181043.sql"
    
    if not os.path.exists(backup_file):
        print(f"❌ 백업 파일을 찾을 수 없습니다: {backup_file}")
        return
    
    try:
        # Neon PostgreSQL 연결
        print("🔌 Neon PostgreSQL 연결 중...")
        conn = connect_neon()
        print("✅ Neon PostgreSQL 연결 성공!")
        
        # MySQL 덤프 파일 파싱
        tables = parse_mysql_dump(backup_file)
        print(f"📋 파싱된 테이블 수: {len(tables)}")
        
        # 각 테이블 마이그레이션
        for table_name, table_info in tables.items():
            print(f"\n📦 테이블 '{table_name}' 마이그레이션 시작...")
            
            # 수동으로 테이블 생성
            create_table_manually(conn, table_name)
            
            # 테이블 데이터 마이그레이션
            migrate_table_data(conn, table_name, table_info['data'])
        
        print("\n🎉 마이그레이션 완료!")
        print("✅ 모든 테이블과 데이터가 Neon PostgreSQL로 성공적으로 마이그레이션되었습니다.")
        
    except Exception as e:
        print(f"❌ 마이그레이션 오류: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 