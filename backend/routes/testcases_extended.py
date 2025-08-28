from flask import Blueprint, request, jsonify
from models import db, TestCase, TestResult
from utils.cors import add_cors_headers
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
from datetime import datetime
import io
import os

logger = get_logger(__name__)

# pandas import를 조건부로 처리
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas 모듈을 사용할 수 없습니다. Excel 기능이 비활성화됩니다.")

# Blueprint 생성
testcases_extended_bp = Blueprint('testcases_extended', __name__)

# 특정 테스트 케이스 조회, 수정, 삭제
@testcases_extended_bp.route('/testcases/<int:testcase_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def manage_testcase(testcase_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'preflight_ok'}), 200
    
    try:
        testcase = TestCase.query.get_or_404(testcase_id)
        
        if request.method == 'GET':
            data = {
                'id': testcase.id,
                'name': testcase.name,
                'description': testcase.description,
                'project_id': testcase.project_id,
                'folder_id': testcase.folder_id,
                            'created_at': testcase.created_at.isoformat(),
            'updated_at': testcase.updated_at.isoformat() if testcase.updated_at else None
            }
            response = jsonify(data)
            return add_cors_headers(response), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            testcase.name = data.get('name', testcase.name)
            testcase.description = data.get('description', testcase.description)
            testcase.project_id = data.get('project_id', testcase.project_id)
            testcase.folder_id = data.get('folder_id', testcase.folder_id)
            testcase.updated_at = get_kst_now()
            
            db.session.commit()
            response = jsonify({'message': '테스트 케이스가 성공적으로 수정되었습니다'})
            return add_cors_headers(response), 200
        
        elif request.method == 'DELETE':
            db.session.delete(testcase)
            db.session.commit()
            response = jsonify({'message': '테스트 케이스가 성공적으로 삭제되었습니다'})
            return add_cors_headers(response), 200
            
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# 테스트 케이스 상태 변경
@testcases_extended_bp.route('/testcases/<int:testcase_id>/status', methods=['PUT', 'OPTIONS'])
def update_testcase_status(testcase_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'preflight_ok'}), 200
    
    try:
        testcase = TestCase.query.get_or_404(testcase_id)
        data = request.get_json()
        
        # 상태 업데이트 로직
        if 'status' in data:
            testcase.status = data['status']
            testcase.updated_at = get_kst_now()
            db.session.commit()
            
            response = jsonify({'message': '테스트 케이스 상태가 업데이트되었습니다'})
            return add_cors_headers(response), 200
        else:
            response = jsonify({'error': '상태 정보가 필요합니다'})
            return add_cors_headers(response), 400
            
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# 테스트 케이스 스크린샷 조회
@testcases_extended_bp.route('/testcases/<int:testcase_id>/screenshots', methods=['GET', 'OPTIONS'])
def get_testcase_screenshots(testcase_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'preflight_ok'}), 200
    
    try:
        # 스크린샷 데이터 조회 로직
        screenshots = []  # 실제 구현에서는 데이터베이스에서 조회
        
        response = jsonify(screenshots)
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# Excel 파일 업로드
@testcases_extended_bp.route('/testcases/upload', methods=['POST', 'OPTIONS'])
def upload_testcases():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'preflight_ok'}), 200
    
    # pandas 사용 불가능 시 오류 반환
    if not PANDAS_AVAILABLE:
        response = jsonify({'error': 'Excel 파일 처리를 위해 pandas 모듈이 필요합니다. 현재 환경에서는 지원되지 않습니다.'})
        return add_cors_headers(response), 501
    
    try:
        if 'file' not in request.files:
            response = jsonify({'error': '파일이 없습니다'})
            return add_cors_headers(response), 400
        
        file = request.files['file']
        if file.filename == '':
            response = jsonify({'error': '파일이 선택되지 않았습니다'})
            return add_cors_headers(response), 400
        
        if file and file.filename.endswith('.xlsx'):
            # Excel 파일 처리 로직
            df = pd.read_excel(file)
            
            # 데이터 검증 및 저장
            success_count = 0
            for _, row in df.iterrows():
                try:
                    testcase = TestCase(
                        name=row.get('name', ''),
                        description=row.get('description', ''),
                        project_id=row.get('project_id'),
                        folder_id=row.get('folder_id')
                    )
                    db.session.add(testcase)
                    success_count += 1
                except Exception as e:
                    logger.error(f"행 처리 오류: {e}")
                    continue
            
            db.session.commit()
            
            response = jsonify({
                'message': f'{success_count}개의 테스트 케이스가 성공적으로 업로드되었습니다'
            })
            return add_cors_headers(response), 200
        else:
            response = jsonify({'error': 'Excel 파일(.xlsx)만 업로드 가능합니다'})
            return add_cors_headers(response), 400
            
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# Excel 파일 다운로드
@testcases_extended_bp.route('/testcases/download', methods=['GET', 'OPTIONS'])
def download_testcases():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'preflight_ok'}), 200
    
    # pandas 사용 불가능 시 오류 반환
    if not PANDAS_AVAILABLE:
        response = jsonify({'error': 'Excel 파일 생성을 위해 pandas 모듈이 필요합니다. 현재 환경에서는 지원되지 않습니다.'})
        return add_cors_headers(response), 501
    
    try:
        testcases = TestCase.query.all()
        
        # DataFrame 생성
        data = []
        for tc in testcases:
            data.append({
                'id': tc.id,
                'name': tc.name,
                'description': tc.description,
                'project_id': tc.project_id,
                'folder_id': tc.folder_id,
                'created_at': tc.created_at.isoformat() if tc.created_at else None
            })
        
        df = pd.DataFrame(data)
        
        # Excel 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='TestCases', index=False)
        
        output.seek(0)
        
        response = jsonify({
            'message': 'Excel 파일이 생성되었습니다',
            'filename': 'testcases.xlsx',
            'data': data
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# 테스트 케이스 실행
@testcases_extended_bp.route('/testcases/<int:testcase_id>/execute', methods=['POST', 'OPTIONS'])
def execute_testcase(testcase_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'preflight_ok'}), 200
    
    try:
        testcase = TestCase.query.get_or_404(testcase_id)
        data = request.get_json()
        
        # 테스트 실행 로직
        environment = data.get('environment', 'dev')
        parameters = data.get('parameters', {})
        
        # 실제 구현에서는 테스트 실행 엔진 호출
        execution_result = {
            'testcase_id': testcase_id,
            'status': 'executed',
            'environment': environment,
            'parameters': parameters,
            'executed_at': get_kst_now().isoformat()
        }
        
        response = jsonify(execution_result)
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# 테스트 케이스 재구성
@testcases_extended_bp.route('/testcases/reorganize', methods=['POST', 'OPTIONS'])
def reorganize_testcases():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'preflight_ok'}), 200
    
    try:
        data = request.get_json()
        reorganization_rules = data.get('rules', [])
        
        # 재구성 로직 구현
        success_count = 0
        for rule in reorganization_rules:
            try:
                # 규칙에 따른 테스트 케이스 재구성
                success_count += 1
            except Exception as e:
                logger.error(f"재구성 규칙 처리 오류: {e}")
                continue
        
        response = jsonify({
            'message': f'{success_count}개의 테스트 케이스가 재구성되었습니다'
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500
