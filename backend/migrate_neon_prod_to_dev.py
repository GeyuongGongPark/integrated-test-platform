#!/usr/bin/env python3
"""
Neon Production DB를 Development DB로 마이그레이션하는 스크립트
"""

import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import pandas as pd

# .env 파일 로드
load_dotenv()

def get_database_urls():
    """Production과 Development 데이터베이스 URL을 가져옵니다."""
    prod_url = os.environ.get('PROD_DATABASE_URL')
    dev_url = os.environ.get('DEV_DATABASE_URL')
    
    if not prod_url:
        print("❌ PROD_DATABASE_URL이 설정되지 않았습니다.")
        return None, None
    
    if not dev_url:
        print("❌ DEV_DATABASE_URL이 설정되지 않았습니다.")
        return None, None
    
    return prod_url, dev_url

def get_table_names(engine):
    """데이터베이스의 모든 테이블 이름을 가져옵니다."""
    inspector = inspect(engine)
    return inspector.get_table_names()

def backup_table_data(prod_engine, table_name):
    """테이블의 모든 데이터를 백업합니다."""
    try:
        query = f'SELECT * FROM "{table_name}"'
        df = pd.read_sql(query, prod_engine)
        return df
    except Exception as e:
        print(f"⚠️  테이블 {table_name} 백업 중 오류: {str(e)}")
        return None

def migrate_table_data(dev_engine, table_name, df):
    """테이블 데이터를 development DB로 마이그레이션합니다."""
    try:
        # 기존 데이터 삭제 (선택사항)
        print(f"🔄 {table_name} 테이블의 기존 데이터를 삭제합니다...")
        dev_engine.execute(text(f'DELETE FROM "{table_name}"'))
        
        # 새 데이터 삽입
        print(f"🔄 {table_name} 테이블에 데이터를 삽입합니다...")
        df.to_sql(table_name, dev_engine, if_exists='append', index=False, method='multi')
        
        print(f"✅ {table_name} 테이블 마이그레이션 완료 ({len(df)} 행)")
        return True
    except Exception as e:
        print(f"❌ {table_name} 테이블 마이그레이션 중 오류: {str(e)}")
        return False

def create_migration_log(prod_url, dev_url, tables_migrated, success_count, total_count):
    """마이그레이션 로그를 생성합니다."""
    log_data = {
        'migration_date': datetime.now().isoformat(),
        'source_database': prod_url.split('@')[1].split('/')[0] if '@' in prod_url else 'unknown',
        'target_database': dev_url.split('@')[1].split('/')[0] if '@' in dev_url else 'unknown',
        'tables_migrated': tables_migrated,
        'success_count': success_count,
        'total_count': total_count,
        'status': 'success' if success_count == total_count else 'partial'
    }
    
    log_filename = f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_filename, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"📝 마이그레이션 로그가 {log_filename}에 저장되었습니다.")

def migrate_neon_prod_to_dev():
    """Neon Production DB를 Development DB로 마이그레이션합니다."""
    prod_url, dev_url = get_database_urls()
    if not prod_url or not dev_url:
        return False
    
    try:
        # 데이터베이스 연결
        print("🔗 데이터베이스에 연결 중...")
        prod_engine = create_engine(prod_url)
        dev_engine = create_engine(dev_url)
        
        # 연결 테스트
        with prod_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Production DB 연결 성공")
        
        with dev_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Development DB 연결 성공")
        
        # Production DB의 모든 테이블 가져오기
        print("📋 Production DB의 테이블 목록을 확인합니다...")
        tables = get_table_names(prod_engine)
        print(f"📊 총 {len(tables)}개의 테이블을 발견했습니다: {', '.join(tables)}")
        
        # 마이그레이션할 테이블 선택
        print("\n🔄 마이그레이션할 테이블을 선택하세요:")
        print("1. 모든 테이블")
        print("2. 특정 테이블만")
        print("3. 테이블별 개별 선택")
        
        choice = input("선택하세요 (1/2/3): ").strip()
        
        tables_to_migrate = []
        
        if choice == "1":
            tables_to_migrate = tables
        elif choice == "2":
            specific_tables = input("마이그레이션할 테이블 이름을 쉼표로 구분하여 입력하세요: ").strip()
            tables_to_migrate = [t.strip() for t in specific_tables.split(',')]
        elif choice == "3":
            for table in tables:
                migrate_this = input(f"{table} 테이블을 마이그레이션하시겠습니까? (y/N): ").strip().lower()
                if migrate_this == 'y':
                    tables_to_migrate.append(table)
        else:
            print("❌ 잘못된 선택입니다.")
            return False
        
        if not tables_to_migrate:
            print("❌ 마이그레이션할 테이블이 선택되지 않았습니다.")
            return False
        
        print(f"\n🚀 {len(tables_to_migrate)}개의 테이블을 마이그레이션합니다...")
        
        success_count = 0
        total_count = len(tables_to_migrate)
        migrated_tables = []
        
        for table_name in tables_to_migrate:
            print(f"\n📦 {table_name} 테이블 마이그레이션 중...")
            
            # 데이터 백업
            df = backup_table_data(prod_engine, table_name)
            if df is None:
                print(f"⚠️  {table_name} 테이블을 건너뜁니다.")
                continue
            
            if df.empty:
                print(f"ℹ️  {table_name} 테이블이 비어있습니다.")
                migrated_tables.append(table_name)
                success_count += 1
                continue
            
            # 데이터 마이그레이션
            if migrate_table_data(dev_engine, table_name, df):
                migrated_tables.append(table_name)
                success_count += 1
        
        # 마이그레이션 로그 생성
        create_migration_log(prod_url, dev_url, migrated_tables, success_count, total_count)
        
        print(f"\n🎉 마이그레이션 완료!")
        print(f"✅ 성공: {success_count}/{total_count} 테이블")
        print(f"📊 마이그레이션된 테이블: {', '.join(migrated_tables)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 마이그레이션 중 오류 발생: {str(e)}")
        return False

def main():
    """메인 함수"""
    print("🚀 Neon Production DB를 Development DB로 마이그레이션합니다...")
    print("=" * 60)
    
    # 환경 변수 확인
    prod_url = os.environ.get('PROD_DATABASE_URL')
    dev_url = os.environ.get('DEV_DATABASE_URL')
    
    print("📋 현재 설정:")
    print(f"Production DB: {prod_url.split('@')[1] if prod_url and '@' in prod_url else 'Not set'}")
    print(f"Development DB: {dev_url.split('@')[1] if dev_url and '@' in dev_url else 'Not set'}")
    
    if not prod_url or not dev_url:
        print("\n❌ 환경 변수가 설정되지 않았습니다.")
        print("다음 환경 변수를 설정해주세요:")
        print("- PROD_DATABASE_URL: Neon Production DB URL")
        print("- DEV_DATABASE_URL: Neon Development DB URL")
        return
    
    # 확인 메시지
    print("\n⚠️  주의사항:")
    print("- 이 작업은 Development DB의 기존 데이터를 덮어씁니다.")
    print("- Production DB의 데이터가 Development DB로 복사됩니다.")
    
    confirm = input("\n계속하시겠습니까? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 마이그레이션이 취소되었습니다.")
        return
    
    # 마이그레이션 실행
    success = migrate_neon_prod_to_dev()
    
    if success:
        print("\n✅ 마이그레이션이 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n❌ 마이그레이션이 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main() 