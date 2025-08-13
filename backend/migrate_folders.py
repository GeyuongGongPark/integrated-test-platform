#!/usr/bin/env python3
"""
기존 폴더 데이터를 새로운 스키마로 마이그레이션하는 스크립트
"""

from app import app, db, Folder
from sqlalchemy import text

def migrate_folders():
    """기존 폴더 데이터를 새로운 스키마로 마이그레이션"""
    with app.app_context():
        try:
            # 기존 테이블 구조 확인
            result = db.session.execute(text("DESCRIBE Folders"))
            columns = [row[0] for row in result]
            print(f"현재 테이블 컬럼: {columns}")
            
            # 필요한 컬럼이 없으면 추가
            if 'folder_name' not in columns:
                print("folder_name 컬럼 추가 중...")
                db.session.execute(text("ALTER TABLE Folders ADD COLUMN folder_name VARCHAR(100)"))
                db.session.execute(text("UPDATE Folders SET folder_name = name WHERE folder_name IS NULL"))
                db.session.execute(text("ALTER TABLE Folders MODIFY COLUMN folder_name VARCHAR(100) NOT NULL"))
                print("✅ folder_name 컬럼 추가 완료")
            
            if 'folder_type' not in columns:
                print("folder_type 컬럼 추가 중...")
                db.session.execute(text("ALTER TABLE Folders ADD COLUMN folder_type VARCHAR(50) DEFAULT 'environment'"))
                print("✅ folder_type 컬럼 추가 완료")
            
            if 'environment' not in columns:
                print("environment 컬럼 추가 중...")
                db.session.execute(text("ALTER TABLE Folders ADD COLUMN environment VARCHAR(50) DEFAULT 'dev'"))
                print("✅ environment 컬럼 추가 완료")
            
            if 'deployment_date' not in columns:
                print("deployment_date 컬럼 추가 중...")
                db.session.execute(text("ALTER TABLE Folders ADD COLUMN deployment_date DATE"))
                print("✅ deployment_date 컬럼 추가 완료")
            
            if 'parent_folder_id' not in columns:
                print("parent_folder_id 컬럼 추가 중...")
                db.session.execute(text("ALTER TABLE Folders ADD COLUMN parent_folder_id INT"))
                # 기존 parent_id가 있다면 복사
                if 'parent_id' in columns:
                    db.session.execute(text("UPDATE Folders SET parent_folder_id = parent_id"))
                print("✅ parent_folder_id 컬럼 추가 완료")
            
            # 변경사항 커밋
            db.session.commit()
            print("✅ 마이그레이션 완료!")
            
            # 결과 확인
            folders = Folder.query.all()
            print(f"총 {len(folders)}개의 폴더가 있습니다:")
            for folder in folders:
                print(f"  - {folder.folder_name} (타입: {folder.folder_type}, 환경: {folder.environment})")
                
        except Exception as e:
            print(f"❌ 마이그레이션 오류: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    print("🚀 폴더 마이그레이션 시작...")
    migrate_folders()
    print("🎉 마이그레이션 완료!")
