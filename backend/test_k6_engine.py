#!/usr/bin/env python3
"""
k6 엔진 경로 계산 테스트 스크립트
"""

import os
import sys

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.engines.k6_engine import K6Engine

def test_path_calculation():
    """k6 엔진의 경로 계산을 테스트합니다."""
    print("=== k6 엔진 경로 계산 테스트 ===")
    
    # k6 엔진 인스턴스 생성
    engine = K6Engine()
    
    # 테스트할 스크립트 경로들
    test_paths = [
        'simple_http_test.js',
        'scripts/test-scripts/performance/simple_http_test.js',
        'clm_draft.js'
    ]
    
    for test_path in test_paths:
        print(f"\n--- 테스트 경로: {test_path} ---")
        
        # execute_test 메서드 호출 (실제 k6 실행 없이 경로 계산만)
        try:
            # 경로 계산 로직만 실행
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(base_dir, '..')
            project_root = os.path.abspath(project_root)
            
            print(f"현재 디렉토리: {os.getcwd()}")
            print(f"k6 엔진 파일 위치: {base_dir}")
            print(f"계산된 프로젝트 루트: {project_root}")
            
            # 여러 경로 시도
            attempts = [
                os.path.join(project_root, test_path),
                os.path.join(project_root, 'scripts', 'test-scripts', 'performance', test_path),
                os.path.join(project_root, 'scripts', 'test-scripts', 'performance', os.path.basename(test_path)),
                os.path.join(os.getcwd(), 'scripts', 'test-scripts', 'performance', os.path.basename(test_path))
            ]
            
            for i, attempt in enumerate(attempts, 1):
                exists = os.path.exists(attempt)
                print(f"시도 {i}: {attempt} - 존재: {exists}")
                if exists:
                    print(f"✅ 파일 발견: {attempt}")
                    break
            else:
                print(f"❌ 모든 시도 실패")
                
        except Exception as e:
            print(f"오류 발생: {e}")

if __name__ == "__main__":
    test_path_calculation()
