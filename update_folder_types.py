#!/usr/bin/env python3
"""
기존 폴더들의 타입을 올바르게 설정하는 스크립트
"""

import requests
import json

def update_folder_types():
    """API를 통해 기존 폴더들의 타입을 올바르게 설정"""
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. 현재 폴더 목록 가져오기
        response = requests.get(f"{base_url}/folders")
        if response.status_code != 200:
            print(f"❌ 폴더 목록 조회 실패: {response.status_code}")
            return
        
        folders = response.json()
        print(f"📋 총 {len(folders)}개의 폴더 발견")
        
        # 2. 각 폴더 타입 업데이트
        for folder in folders:
            folder_id = folder['id']
            folder_name = folder['folder_name']
            current_type = folder['folder_type']
            
            # 이미 올바른 타입이면 건너뛰기
            if current_type in ['environment', 'deployment_date', 'feature']:
                print(f"✅ {folder_name} (ID: {folder_id}) - 이미 올바른 타입: {current_type}")
                continue
            
            # 폴더 타입 결정
            new_type = None
            environment = None
            deployment_date = None
            
            if '환경' in folder_name:
                new_type = 'environment'
                if 'DEV' in folder_name:
                    environment = 'dev'
                elif 'ALPHA' in folder_name:
                    environment = 'alpha'
                elif 'PRODUCTION' in folder_name:
                    environment = 'production'
            elif folder_name.startswith('2025-'):
                new_type = 'deployment_date'
                deployment_date = folder_name
            elif current_type == 'feature':
                new_type = 'feature'
                environment = folder.get('environment')
                deployment_date = folder.get('deployment_date')
            
            if new_type:
                # 폴더 업데이트
                update_data = {
                    'folder_name': folder_name,
                    'folder_type': new_type,
                    'parent_folder_id': folder.get('parent_folder_id'),
                    'environment': environment,
                    'deployment_date': deployment_date
                }
                
                response = requests.put(
                    f"{base_url}/folders/{folder_id}",
                    json=update_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    print(f"✅ {folder_name} (ID: {folder_id}) - 타입 업데이트: {current_type} -> {new_type}")
                else:
                    print(f"❌ {folder_name} (ID: {folder_id}) - 업데이트 실패: {response.status_code}")
            else:
                print(f"⚠️ {folder_name} (ID: {folder_id}) - 타입 결정 불가: {current_type}")
        
        print("\n✅ 폴더 타입 업데이트 완료!")
        
        # 3. 업데이트된 폴더 목록 확인
        response = requests.get(f"{base_url}/folders")
        if response.status_code == 200:
            updated_folders = response.json()
            print("\n📋 업데이트된 폴더 목록:")
            for folder in updated_folders:
                print(f"  - {folder['folder_name']} (타입: {folder['folder_type']}, 환경: {folder['environment']}, 배포일자: {folder['deployment_date']})")
                
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == '__main__':
    update_folder_types()
