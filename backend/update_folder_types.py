#!/usr/bin/env python3
"""
기존 폴더들의 타입을 실제 용도에 맞게 업데이트하는 스크립트
"""

from app import app, db, Folder
from sqlalchemy import text

def update_folder_types():
    """기존 폴더들의 타입을 실제 용도에 맞게 업데이트"""
    with app.app_context():
        try:
            # 환경별 폴더들
            env_folders = ['DEV 환경', 'ALPHA 환경', 'PRODUCTION 환경']
            for folder_name in env_folders:
                folder = Folder.query.filter_by(folder_name=folder_name).first()
                if folder:
                    folder.folder_type = 'environment'
                    folder.environment = folder_name.split(' ')[0].lower()
                    print(f"✅ {folder_name}: 환경 타입으로 설정 (환경: {folder.environment})")
            
            # 배포일자 폴더들
            date_folders = ['2025-08-13']
            for folder_name in date_folders:
                folder = Folder.query.filter_by(folder_name=folder_name).first()
                if folder:
                    folder.folder_type = 'deployment_date'
                    folder.environment = 'dev'  # 기본값
                    print(f"✅ {folder_name}: 배포일자 타입으로 설정")
            
            # 기능별 폴더들
            feature_folders = [
                'CLM/Draft', 'CLM/Review', 'CLM/Sign', 'CLM/Process',
                'Litigation/Draft', 'Litigation/Schedule', 'Dashboard/Setting'
            ]
            for folder_name in feature_folders:
                folder = Folder.query.filter_by(folder_name=folder_name).first()
                if folder:
                    folder.folder_type = 'feature'
                    folder.environment = 'dev'  # 기본값
                    print(f"✅ {folder_name}: 기능명 타입으로 설정")
            
            # 변경사항 커밋
            db.session.commit()
            print("✅ 폴더 타입 업데이트 완료!")
            
            # 결과 확인
            folders = Folder.query.all()
            print(f"\n📁 업데이트된 폴더 목록:")
            for folder in folders:
                print(f"  - {folder.folder_name} (타입: {folder.folder_type}, 환경: {folder.environment})")
                
        except Exception as e:
            print(f"❌ 폴더 타입 업데이트 오류: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    print("🚀 폴더 타입 업데이트 시작...")
    update_folder_types()
    print("🎉 폴더 타입 업데이트 완료!")
