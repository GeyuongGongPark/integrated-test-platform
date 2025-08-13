#!/usr/bin/env python3
"""
중복된 컬럼들을 정리하고 데이터 일관성을 맞추는 스크립트
"""

from app import app, db, Folder
from sqlalchemy import text

def cleanup_duplicate_columns():
    """중복된 컬럼들을 정리"""
    with app.app_context():
        try:
            print("🧹 중복 컬럼 정리 시작...")
            
            # 1. parent_folder_id가 잘못 설정된 폴더들 수정
            print("\n🔧 parent_folder_id 수정:")
            
            # 배포일자 폴더들은 환경 폴더의 하위에 있어야 함
            deployment_folders = db.session.execute(text("SELECT id, folder_name FROM Folders WHERE folder_type = 'deployment_date'"))
            for row in deployment_folders:
                folder_id = row[0]
                folder_name = row[1]
                
                # 2025-08-13 폴더는 DEV 환경의 하위에 배치
                if '2025-08-13' in folder_name:
                    db.session.execute(text("UPDATE Folders SET parent_folder_id = 1 WHERE id = :folder_id"), {"folder_id": folder_id})
                    print(f"✅ 폴더 ID {folder_id} ({folder_name}): DEV 환경 하위로 이동")
            
            # 기능 폴더들은 적절한 배포일자 폴더의 하위에 배치
            feature_folders = db.session.execute(text("SELECT id, folder_name, parent_folder_id FROM Folders WHERE folder_type = 'feature'"))
            for row in feature_folders:
                folder_id = row[0]
                folder_name = row[1]
                current_parent = row[2]
                
                # CLM 관련 폴더들은 2025-08-13 (ID: 4) 하위에
                if 'CLM' in folder_name and current_parent != 4:
                    db.session.execute(text("UPDATE Folders SET parent_folder_id = 4 WHERE id = :folder_id"), {"folder_id": folder_id})
                    print(f"✅ 폴더 ID {folder_id} ({folder_name}): 2025-08-13 하위로 이동")
                
                # Litigation 관련 폴더들은 2025-08-13 (ID: 5) 하위에
                elif 'Litigation' in folder_name and current_parent != 5:
                    db.session.execute(text("UPDATE Folders SET parent_folder_id = 5 WHERE id = :folder_id"), {"folder_id": folder_id})
                    print(f"✅ 폴더 ID {folder_id} ({folder_name}): 2025-08-13 하위로 이동")
                
                # Dashboard 관련 폴더들은 2025-08-13 (ID: 6) 하위에
                elif 'Dashboard' in folder_name and current_parent != 6:
                    db.session.execute(text("UPDATE Folders SET parent_folder_id = 6 WHERE id = :folder_id"), {"folder_id": folder_id})
                    print(f"✅ 폴더 ID {folder_id} ({folder_name}): 2025-08-13 하위로 이동")
            
            # 2. 중복된 컬럼들 정리 (필요한 경우)
            print("\n🗑️ 중복 컬럼 정리:")
            
            # name 컬럼이 folder_name과 다른 경우 folder_name으로 통일
            name_diff_folders = db.session.execute(text("SELECT id, name, folder_name FROM Folders WHERE name != folder_name"))
            for row in name_diff_folders:
                folder_id = row[0]
                old_name = row[1]
                new_name = row[2]
                if new_name:
                    db.session.execute(text("UPDATE Folders SET name = :new_name WHERE id = :folder_id"), {"new_name": new_name, "folder_id": folder_id})
                    print(f"✅ 폴더 ID {folder_id}: name을 '{new_name}'으로 통일")
            
            # parent_id 컬럼이 parent_folder_id와 다른 경우 parent_folder_id로 통일
            parent_diff_folders = db.session.execute(text("SELECT id, parent_id, parent_folder_id FROM Folders WHERE parent_id != parent_folder_id OR (parent_id IS NULL AND parent_folder_id IS NOT NULL) OR (parent_id IS NOT NULL AND parent_folder_id IS NULL)"))
            for row in parent_diff_folders:
                folder_id = row[0]
                old_parent = row[1]
                new_parent = row[2]
                if new_parent is not None:
                    db.session.execute(text("UPDATE Folders SET parent_id = :new_parent WHERE id = :folder_id"), {"new_parent": new_parent, "folder_id": folder_id})
                    print(f"✅ 폴더 ID {folder_id}: parent_id를 {new_parent}로 통일")
            
            # 변경사항 커밋
            db.session.commit()
            print("\n✅ 중복 컬럼 정리 완료!")
            
            # 결과 확인
            print("\n📁 정리된 폴더 구조:")
            folders = Folder.query.all()
            for folder in folders:
                print(f"  - {folder.folder_name} (ID: {folder.id}, 타입: {folder.folder_type}, 상위: {folder.parent_folder_id})")
                
        except Exception as e:
            print(f"❌ 중복 컬럼 정리 오류: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 중복 컬럼 정리 시작...")
    cleanup_duplicate_columns()
    print("🎉 정리 완료!")
