#!/usr/bin/env python3
"""
Alpha DB에 기존 스크린샷 파일들을 저장하는 마이그레이션 스크립트
"""

import os
import sys
import base64
from datetime import datetime
from PIL import Image
import io

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Screenshot, TestCase, TestResult

def get_image_metadata(image_path):
    """이미지 파일의 메타데이터 추출"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            file_size = os.path.getsize(image_path)
            return {
                'width': width,
                'height': height,
                'file_size': file_size,
                'format': img.format.lower() if img.format else 'png'
            }
    except Exception as e:
        print(f"⚠️ 이미지 메타데이터 추출 실패: {image_path} - {e}")
        return None

def find_screenshot_files():
    """test-scripts 폴더에서 모든 스크린샷 파일 찾기"""
    screenshot_files = []
    test_scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test-scripts')
    
    for root, dirs, files in os.walk(test_scripts_dir):
        for file in files:
            if file.lower().endswith('.png'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, test_scripts_dir)
                screenshot_files.append({
                    'full_path': full_path,
                    'relative_path': rel_path,
                    'filename': file,
                    'directory': root
                })
    
    return screenshot_files

def create_test_case_for_screenshot(screenshot_info):
    """스크린샷을 위한 테스트 케이스 생성 (없는 경우)"""
    try:
        # 파일명에서 테스트 케이스명 추출
        filename = screenshot_info['filename']
        base_name = os.path.splitext(filename)[0]
        
        # 이미 존재하는 테스트 케이스 확인
        existing_case = TestCase.query.filter_by(name=base_name).first()
        if existing_case:
            return existing_case
        
        # 새 테스트 케이스 생성 (alpha DB 스키마에 맞춤)
        test_case = TestCase(
            name=base_name,
            description=f"자동 생성된 테스트 케이스 - {filename}",
            test_type='performance',
            script_path=screenshot_info['relative_path'],
            main_category='performance',
            sub_category='screenshot_migration',
            environment='alpha',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            priority='medium',
            status='active',
            result_status='pending'
        )
        
        db.session.add(test_case)
        db.session.commit()
        print(f"✅ 새 테스트 케이스 생성: {base_name}")
        return test_case
        
    except Exception as e:
        print(f"❌ 테스트 케이스 생성 실패: {e}")
        db.session.rollback()
        return None

def create_test_result_for_screenshot(test_case):
    """스크린샷을 위한 테스트 결과 생성"""
    try:
        # 새 테스트 결과 생성
        test_result = TestResult(
            test_case_id=test_case.id,
            result='Pass',
            execution_time=0.0,
            environment='alpha',
            executed_by='migration_script',
            executed_at=datetime.now(),
            notes='스크린샷 마이그레이션으로 생성된 테스트 결과'
        )
        
        db.session.add(test_result)
        db.session.commit()
        print(f"✅ 새 테스트 결과 생성: ID {test_result.id}")
        return test_result
        
    except Exception as e:
        print(f"❌ 테스트 결과 생성 실패: {e}")
        db.session.rollback()
        return None

def migrate_screenshots_to_alpha_db():
    """스크린샷 파일들을 Alpha DB로 마이그레이션"""
    print("🚀 Alpha DB 스크린샷 마이그레이션 시작...")
    
    # 스크린샷 파일들 찾기
    screenshot_files = find_screenshot_files()
    print(f"📸 발견된 스크린샷 파일 수: {len(screenshot_files)}")
    
    if not screenshot_files:
        print("❌ 스크린샷 파일을 찾을 수 없습니다.")
        return
    
    success_count = 0
    error_count = 0
    
    for i, screenshot_info in enumerate(screenshot_files, 1):
        print(f"\n🔍 처리 중 ({i}/{len(screenshot_files)}): {screenshot_info['filename']}")
        
        try:
            # 이미지 메타데이터 추출
            metadata = get_image_metadata(screenshot_info['full_path'])
            if not metadata:
                error_count += 1
                continue
            
            # 테스트 케이스 생성 또는 조회
            test_case = create_test_case_for_screenshot(screenshot_info)
            if not test_case:
                error_count += 1
                continue
            
            # 테스트 결과 생성
            test_result = create_test_result_for_screenshot(test_case)
            if not test_result:
                error_count += 1
                continue
            
            # 기존 스크린샷 확인 (중복 방지)
            existing_screenshot = Screenshot.query.filter_by(
                test_result_id=test_result.id,
                file_path=screenshot_info['relative_path']
            ).first()
            
            if existing_screenshot:
                print(f"⏭️ 이미 존재하는 스크린샷: {screenshot_info['filename']}")
                continue
            
            # 새 스크린샷 생성 (alpha DB 스키마에 맞춤)
            screenshot = Screenshot(
                test_result_id=test_result.id,
                file_path=screenshot_info['relative_path'],
                created_at=datetime.now()
            )
            
            db.session.add(screenshot)
            db.session.commit()
            
            print(f"✅ 스크린샷 저장 완료: {screenshot_info['filename']}")
            print(f"   - 크기: {metadata['width']}x{metadata['height']}")
            print(f"   - 파일 크기: {metadata['file_size']} bytes")
            print(f"   - 테스트 케이스: {test_case.name}")
            print(f"   - 테스트 결과: ID {test_result.id}")
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ 스크린샷 처리 실패: {screenshot_info['filename']} - {e}")
            db.session.rollback()
            error_count += 1
    
    print(f"\n🎉 Alpha DB 마이그레이션 완료!")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {error_count}개")
    print(f"📊 총 처리: {len(screenshot_files)}개")

def cleanup_duplicate_screenshots():
    """중복된 스크린샷 정리"""
    print("\n🧹 중복 스크린샷 정리 중...")
    
    try:
        # 같은 file_path를 가진 중복 스크린샷 찾기
        from sqlalchemy import func
        
        duplicates = db.session.query(
            Screenshot.file_path,
            func.count(Screenshot.id).label('count')
        ).group_by(Screenshot.file_path).having(func.count(Screenshot.id) > 1).all()
        
        if not duplicates:
            print("✅ 중복 스크린샷이 없습니다.")
            return
        
        print(f"🔍 중복 스크린샷 발견: {len(duplicates)}개")
        
        for file_path, count in duplicates:
            print(f"   - {file_path}: {count}개")
            
            # 가장 최근 것만 남기고 나머지 삭제
            screenshots = Screenshot.query.filter_by(file_path=file_path).order_by(Screenshot.created_at.desc()).all()
            
            for screenshot in screenshots[1:]:  # 첫 번째 이후 모두 삭제
                db.session.delete(screenshot)
                print(f"     삭제: ID {screenshot.id}")
            
            db.session.commit()
            print(f"     ✅ {file_path} 중복 제거 완료")
    
    except Exception as e:
        print(f"❌ 중복 정리 실패: {e}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        try:
            # 스크린샷 마이그레이션 실행
            migrate_screenshots_to_alpha_db()
            
            # 중복 정리
            cleanup_duplicate_screenshots()
            
            print("\n🎯 Alpha DB 마이그레이션 스크립트 실행 완료!")
            
        except Exception as e:
            print(f"❌ 마이그레이션 실패: {e}")
            sys.exit(1)
