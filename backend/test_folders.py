#!/usr/bin/env python3
"""
폴더 API의 오류를 진단하기 위한 테스트 스크립트
"""

from app import app, db, Folder
from sqlalchemy import text

def test_folders():
    """폴더 데이터와 API를 테스트"""
    with app.app_context():
        try:
            print("🔍 데이터베이스 연결 테스트...")
            
            # 1. 테이블 구조 확인
            print("\n📋 테이블 구조 확인:")
            result = db.session.execute(text("DESCRIBE Folders"))
            columns = [row[0] for row in result]
            for col in columns:
                print(f"  - {col}")
            
            # 2. 폴더 데이터 확인
            print("\n📁 폴더 데이터 확인:")
            folders = Folder.query.all()
            print(f"총 {len(folders)}개의 폴더:")
            for folder in folders:
                print(f"  - ID: {folder.id}")
                print(f"    이름: {folder.folder_name}")
                print(f"    타입: {folder.folder_type}")
                print(f"    환경: {folder.environment}")
                print(f"    배포일자: {folder.deployment_date}")
                print(f"    상위폴더: {folder.parent_folder_id}")
                print("    ---")
            
            # 3. API 응답 시뮬레이션
            print("\n🔧 API 응답 시뮬레이션:")
            try:
                # get_folders() 시뮬레이션
                folders_data = [{
                    'id': f.id, 
                    'folder_name': f.folder_name, 
                    'parent_folder_id': f.parent_folder_id,
                    'folder_type': f.folder_type,
                    'environment': f.environment,
                    'deployment_date': f.deployment_date.strftime('%Y-%m-%d') if f.deployment_date else None,
                    'created_at': f.created_at.strftime('%Y-%m-%d %H:%M:%S') if f.created_at else None
                } for f in folders]
                print("✅ get_folders() 성공")
                
                # get_folders_tree() 시뮬레이션
                environment_folders = Folder.query.filter(
                    (Folder.folder_type == 'environment') | 
                    ((Folder.folder_type.is_(None)) & (Folder.parent_folder_id.is_(None)))
                ).all()
                print(f"✅ get_folders_tree() 성공 - 환경 폴더 {len(environment_folders)}개")
                
            except Exception as e:
                print(f"❌ API 시뮬레이션 오류: {str(e)}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"❌ 테스트 오류: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 폴더 API 테스트 시작...")
    test_folders()
    print("🎉 테스트 완료!")
