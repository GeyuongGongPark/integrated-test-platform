#!/usr/bin/env python3
"""
폴더 데이터의 누락된 필드들을 수정하고 데이터 일관성을 맞추는 스크립트
"""

from app import app, db, Folder
from sqlalchemy import text

def fix_folder_data():
    """폴더 데이터의 누락된 필드들을 수정"""
    with app.app_context():
        try:
            # 1. folder_name이 null인 폴더들 수정
            null_name_folders = db.session.execute(text("SELECT id, name FROM Folders WHERE folder_name IS NULL"))
            for row in null_name_folders:
                folder_id = row[0]
                old_name = row[1]
                if old_name:
                    db.session.execute(text("UPDATE Folders SET folder_name = %s WHERE id = %s"), (old_name, folder_id))
                    print(f"✅ 폴더 ID {folder_id}: folder_name을 '{old_name}'으로 설정")
            
            # 2. folder_type이 null인 폴더들 수정
            null_type_folders = db.session.execute(text("SELECT id, folder_name FROM Folders WHERE folder_type IS NULL"))
            for row in null_type_folders:
                folder_id = row[0]
                folder_name = row[1]
                
                # 폴더명을 기반으로 타입 추정
                if folder_name and '환경' in folder_name:
                    folder_type = 'environment'
                    if 'DEV' in folder_name.upper():
                        environment = 'dev'
                    elif 'ALPHA' in folder_name.upper():
                        environment = 'alpha'
                    elif 'PRODUCTION' in folder_name.upper():
                        environment = 'production'
                    else:
                        environment = 'dev'
                elif folder_name and any(char.isdigit() for char in folder_name) and '-' in folder_name:
                    folder_type = 'deployment_date'
                    environment = 'dev'
                else:
                    folder_type = 'feature'
                    environment = 'dev'
                
                db.session.execute(text("UPDATE Folders SET folder_type = %s, environment = %s WHERE id = %s"), 
                                 (folder_type, environment, folder_id))
                print(f"✅ 폴더 ID {folder_id}: 타입을 '{folder_type}', 환경을 '{environment}'으로 설정")
            
            # 3. environment가 null인 폴더들 수정
            null_env_folders = db.session.execute(text("SELECT id, folder_name, folder_type FROM Folders WHERE environment IS NULL"))
            for row in null_env_folders:
                folder_id = row[0]
                folder_name = row[1]
                folder_type = row[2]
                
                if folder_type == 'environment':
                    if 'DEV' in folder_name.upper():
                        environment = 'dev'
                    elif 'ALPHA' in folder_name.upper():
                        environment = 'alpha'
                    elif 'PRODUCTION' in folder_name.upper():
                        environment = 'production'
                    else:
                        environment = 'dev'
                else:
                    environment = 'dev'
                
                db.session.execute(text("UPDATE Folders SET environment = %s WHERE id = %s"), (environment, folder_id))
                print(f"✅ 폴더 ID {folder_id}: 환경을 '{environment}'으로 설정")
            
            # 4. parent_folder_id가 null이지만 실제로는 상위 폴더가 있는 폴더들 수정
            # (이 부분은 실제 데이터 구조에 따라 조정 필요)
            
            # 변경사항 커밋
            db.session.commit()
            print("✅ 폴더 데이터 수정 완료!")
            
            # 결과 확인
            folders = Folder.query.all()
            print(f"\n📁 수정된 폴더 목록:")
            for folder in folders:
                print(f"  - {folder.folder_name} (타입: {folder.folder_type}, 환경: {folder.environment})")
                
        except Exception as e:
            print(f"❌ 폴더 데이터 수정 오류: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    print("🚀 폴더 데이터 수정 시작...")
    fix_folder_data()
    print("🎉 폴더 데이터 수정 완료!")
