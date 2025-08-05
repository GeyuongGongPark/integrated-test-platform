#!/usr/bin/env python3
"""
간단한 Neon Production DB를 Development DB로 마이그레이션 스크립트
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import pandas as pd

# .env 파일 로드
load_dotenv()

def migrate_neon_db():
    """Neon Production DB를 Development DB로 마이그레이션합니다."""
    
    # 환경 변수 확인
    prod_url = os.environ.get('PROD_DATABASE_URL')
    dev_url = os.environ.get('DEV_DATABASE_URL')
    
    if not prod_url or not dev_url:
        print("❌ PROD_DATABASE_URL 또는 DEV_DATABASE_URL이 설정되지 않았습니다.")
        print("📝 .env 파일에 데이터베이스 URL을 설정해주세요.")
        return False
    
    try:
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
        inspector = inspect(prod_engine)
        tables = inspector.get_table_names()
        
        print(f"📊 총 {len(tables)}개의 테이블을 발견했습니다: {', '.join(tables)}")
        
        success_count = 0
        total_count = len(tables)
        
        for table_name in tables:
            print(f"\n📦 {table_name} 테이블 마이그레이션 중...")
            
            try:
                # 데이터 읽기
                query = f'SELECT * FROM "{table_name}"'
                df = pd.read_sql(query, prod_engine)
                
                if df.empty:
                    print(f"ℹ️  {table_name} 테이블이 비어있습니다.")
                    success_count += 1
                    continue
                
                # Development DB에서 기존 데이터 삭제
                with dev_engine.connect() as conn:
                    conn.execute(text(f'DELETE FROM "{table_name}"'))
                    conn.commit()
                
                # 새 데이터 삽입
                df.to_sql(table_name, dev_engine, if_exists='append', index=False, method='multi')
                
                print(f"✅ {table_name} 테이블 마이그레이션 완료 ({len(df)} 행)")
                success_count += 1
                
            except Exception as e:
                print(f"❌ {table_name} 테이블 마이그레이션 실패: {str(e)}")
        
        print(f"\n🎉 마이그레이션 완료!")
        print(f"✅ 성공: {success_count}/{total_count} 테이블")
        
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
    if prod_url:
        masked_prod = prod_url.split('@')[0].split('://')[0] + '://***@' + prod_url.split('@')[1] if '@' in prod_url else prod_url
        print(f"Production DB: {masked_prod}")
    else:
        print("Production DB: Not set")
    
    if dev_url:
        masked_dev = dev_url.split('@')[0].split('://')[0] + '://***@' + dev_url.split('@')[1] if '@' in dev_url else dev_url
        print(f"Development DB: {masked_dev}")
    else:
        print("Development DB: Not set")
    
    if not prod_url or not dev_url:
        print("\n❌ 환경 변수가 설정되지 않았습니다.")
        print("📝 .env 파일에 다음을 추가해주세요:")
        print("- PROD_DATABASE_URL: Neon Production DB URL")
        print("- DEV_DATABASE_URL: Neon Development DB URL")
        return
    
    # 확인 메시지
    print("\n⚠️  주의사항:")
    print("- 이 작업은 Development DB의 기존 데이터를 덮어씁니다.")
    print("- Production DB의 모든 데이터가 Development DB로 복사됩니다.")
    
    confirm = input("\n계속하시겠습니까? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 마이그레이션이 취소되었습니다.")
        return
    
    # 마이그레이션 실행
    success = migrate_neon_db()
    
    if success:
        print("\n✅ 마이그레이션이 성공적으로 완료되었습니다!")
        print("🔍 Development DB에서 데이터를 확인해보세요.")
        sys.exit(0)
    else:
        print("\n❌ 마이그레이션이 실패했습니다.")
        print("📞 문제가 발생하면 로그를 확인하고 다시 시도해주세요.")
        sys.exit(1)

if __name__ == "__main__":
    main() 