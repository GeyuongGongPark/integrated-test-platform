from flask import Blueprint, request, jsonify, send_file
from models import db, TestCase, TestResult, Screenshot, Project, Folder
from utils.cors import add_cors_headers
from datetime import datetime
import pandas as pd
from io import BytesIO
import os
import subprocess
import time
import json

# Blueprint 생성
testcases_bp = Blueprint('testcases', __name__)

# 기존 TCM API 엔드포인트들
@testcases_bp.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    data = [{
        'id': p.id,
        'name': p.name,
        'description': p.description
    } for p in projects]
    response = jsonify(data)
    return add_cors_headers(response), 200

@testcases_bp.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    project = Project(
        name=data.get('name'),
        description=data.get('description')
    )
    db.session.add(project)
    db.session.commit()
    response = jsonify({'message': '프로젝트 생성 완료', 'id': project.id})
    return add_cors_headers(response), 201

@testcases_bp.route('/testcases', methods=['GET'])
def get_testcases():
    try:
        testcases = TestCase.query.all()
        print(f"🧪 전체 테스트 케이스 수: {len(testcases)}")
        
        # 폴더 ID별 테스트 케이스 수 확인
        folder_counts = {}
        for tc in testcases:
            folder_id = tc.folder_id
            if folder_id not in folder_counts:
                folder_counts[folder_id] = 0
            folder_counts[folder_id] += 1
        
        print(f"📁 폴더별 테스트 케이스 수: {folder_counts}")
        
        data = [{
            'id': tc.id,
            'project_id': tc.project_id,
            'main_category': tc.main_category,
            'sub_category': tc.sub_category,
            'detail_category': tc.detail_category,
            'pre_condition': tc.pre_condition,
            'expected_result': tc.expected_result,
            'result_status': tc.result_status,
            'remark': tc.remark,
            'folder_id': tc.folder_id,
            'automation_code_path': tc.automation_code_path,
            'automation_code_type': tc.automation_code_type,
            'environment': tc.environment,
            'created_at': tc.created_at,
            'updated_at': tc.updated_at
        } for tc in testcases]
        response = jsonify(data)
        
        return add_cors_headers(response), 200
    except Exception as e:
        print(f"❌ TestCases 조회 오류: {str(e)}")
        response = jsonify({
            'error': '데이터베이스 연결 오류',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        })
        
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases/<int:id>', methods=['GET'])
def get_testcase(id):
    tc = TestCase.query.get_or_404(id)
    screenshots = Screenshot.query.filter_by(test_case_id=id).all()
    screenshot_data = [{'id': ss.id, 'screenshot_path': ss.screenshot_path, 'timestamp': ss.timestamp} for ss in screenshots]
    data = {
        'id': tc.id,
        'project_id': tc.project_id,
        'main_category': tc.main_category,
        'sub_category': tc.sub_category,
        'detail_category': tc.detail_category,
        'pre_condition': tc.pre_condition,
        'expected_result': tc.expected_result,
        'result_status': tc.result_status,
        'remark': tc.remark,
        'screenshots': screenshot_data,
        'created_at': tc.created_at,
        'updated_at': tc.updated_at
    }
    response = jsonify(data)
    return add_cors_headers(response), 200

@testcases_bp.route('/testcases', methods=['POST'])
def create_testcase():
    data = request.get_json()
    print("Received data:", data)
    print("자동화 코드 경로:", data.get('automation_code_path'))
    print("자동화 코드 타입:", data.get('automation_code_type'))
    
    # project_id가 없으면 기본 프로젝트 사용
    project_id = data.get('project_id')
    if not project_id:
        default_project = Project.query.filter_by(name='Test Management System').first()
        if default_project:
            project_id = default_project.id
        else:
            response = jsonify({'error': '기본 프로젝트가 없습니다. 먼저 프로젝트를 생성해주세요.'})
            return add_cors_headers(response), 400
    
    # folder_id가 없으면 기본 폴더 사용
    folder_id = data.get('folder_id')
    if not folder_id:
        # DEV 환경의 첫 번째 배포일자 폴더를 기본으로 사용
        dev_folder = Folder.query.filter_by(folder_type='environment', environment='dev').first()
        if dev_folder:
            default_deployment_folder = Folder.query.filter_by(
                folder_type='deployment_date', 
                parent_folder_id=dev_folder.id
            ).first()
            if default_deployment_folder:
                folder_id = default_deployment_folder.id
    
    tc = TestCase(
        project_id=project_id,
        main_category=data.get('main_category', ''),
        sub_category=data.get('sub_category', ''),
        detail_category=data.get('detail_category', ''),
        pre_condition=data.get('pre_condition', ''),
        expected_result=data.get('expected_result', ''),
        result_status=data.get('result_status', 'N/T'),
        remark=data.get('remark', ''),
        environment=data.get('environment', 'dev'),
        folder_id=folder_id,
        automation_code_path=data.get('automation_code_path', ''),
        automation_code_type=data.get('automation_code_type', 'playwright')
    )

    try:
        db.session.add(tc)
        db.session.commit()
        response = jsonify({'message': '테스트 케이스 생성 완료', 'id': tc.id})
        return add_cors_headers(response), 201
    except Exception as e:
        print("Error saving to database:", e)
        db.session.rollback()
        response = jsonify({'error': f'데이터베이스 오류: {str(e)}'})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases/<int:id>/status', methods=['PUT'])
def update_testcase_status(id):
    tc = TestCase.query.get_or_404(id)
    data = request.get_json()
    tc.result_status = data.get('status', tc.result_status)
    db.session.commit()
    response = jsonify({'message': '테스트 케이스 상태 업데이트 완료'})
    return add_cors_headers(response), 200

@testcases_bp.route('/testcases/<int:id>', methods=['PUT'])
def update_testcase(id):
    tc = TestCase.query.get_or_404(id)
    data = request.get_json()
    tc.main_category = data.get('main_category', tc.main_category)
    tc.sub_category = data.get('sub_category', tc.sub_category)
    tc.detail_category = data.get('detail_category', tc.detail_category)
    tc.pre_condition = data.get('pre_condition', tc.pre_condition)
    tc.expected_result = data.get('expected_result', tc.expected_result)
    tc.result_status = data.get('result_status', tc.result_status)
    tc.remark = data.get('remark', tc.remark)
    tc.environment = data.get('environment', tc.environment)
    tc.folder_id = data.get('folder_id', tc.folder_id)
    tc.automation_code_path = data.get('automation_code_path', tc.automation_code_path)
    tc.automation_code_type = data.get('automation_code_type', tc.automation_code_type)
    db.session.commit()
    response = jsonify({'message': '테스트 케이스 업데이트 완료'})
    return add_cors_headers(response), 200

@testcases_bp.route('/testcases/<int:id>', methods=['DELETE'])
def delete_testcase(id):
    tc = TestCase.query.get_or_404(id)
    db.session.delete(tc)
    db.session.commit()
    response = jsonify({'message': '테스트 케이스 삭제 완료'})
    return add_cors_headers(response), 200

@testcases_bp.route('/testresults/<int:test_case_id>', methods=['GET'])
def get_test_results(test_case_id):
    """특정 테스트 케이스의 실행 결과 조회"""
    try:
        results = TestResult.query.filter_by(test_case_id=test_case_id).order_by(TestResult.executed_at.desc()).all()
        
        result_list = []
        for result in results:
            result_data = {
                'id': result.id,
                'test_case_id': result.test_case_id,
                'result': result.result,
                'executed_at': result.executed_at.isoformat() if result.executed_at else None,
                'notes': result.notes,
                'screenshot': result.screenshot,
                'environment': result.environment,
                'execution_duration': result.execution_duration,
                'error_message': result.error_message
            }
            result_list.append(result_data)
        
        response = jsonify(result_list)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/testcases/<int:id>/screenshots', methods=['GET'])
def get_testcase_screenshots(id):
    """테스트 케이스의 스크린샷 목록 조회"""
    try:
        test_case = TestCase.query.get_or_404(id)
        screenshots = Screenshot.query.filter_by(test_case_id=id).order_by(Screenshot.timestamp.desc()).all()
        
        screenshot_list = []
        for screenshot in screenshots:
            screenshot_data = {
                'id': screenshot.id,
                'screenshot_path': screenshot.screenshot_path,
                'timestamp': screenshot.timestamp.isoformat() if screenshot.timestamp else None
            }
            screenshot_list.append(screenshot_data)
        
        response = jsonify(screenshot_list)
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/screenshots/<path:filename>', methods=['GET'])
def get_screenshot(filename):
    """스크린샷 파일 조회"""
    try:
        import os
        screenshot_path = os.path.join('screenshots', filename)
        if os.path.exists(screenshot_path):
            return send_file(screenshot_path, mimetype='image/png')
        else:
            response = jsonify({'error': '스크린샷 파일을 찾을 수 없습니다'})
            return add_cors_headers(response), 404
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@testcases_bp.route('/testresults', methods=['POST'])
def create_test_result():
    data = request.get_json()
    result = TestResult(
        test_case_id=data.get('test_case_id'),
        result=data.get('result'),
        notes=data.get('notes')
    )
    db.session.add(result)
    db.session.commit()
    response = jsonify({'message': '테스트 결과 생성 완료', 'id': result.id})
    return add_cors_headers(response), 201

# 엑셀 업로드 API
@testcases_bp.route('/testcases/upload', methods=['POST'])
def upload_testcases_excel():
    """엑셀 파일에서 테스트 케이스 업로드"""
    try:
        print("=== 파일 업로드 디버깅 ===")
        print(f"Content-Type: {request.headers.get('Content-Type')}")
        print(f"Files: {list(request.files.keys())}")
        print(f"Form data: {list(request.form.keys())}")
        
        if 'file' not in request.files:
            print("❌ 'file' 키가 request.files에 없음")
            print(f"사용 가능한 키들: {list(request.files.keys())}")
            response = jsonify({'error': '파일이 없습니다'})
            return add_cors_headers(response), 400
        
        file = request.files['file']
        print(f"파일명: {file.filename}")
        print(f"파일 크기: {len(file.read()) if file else 'N/A'}")
        file.seek(0)  # 파일 포인터를 다시 처음으로
        
        if file.filename == '':
            print("❌ 파일명이 비어있음")
            response = jsonify({'error': '파일이 선택되지 않았습니다'})
            return add_cors_headers(response), 400
        
        if not file.filename.endswith('.xlsx'):
            print(f"❌ 지원하지 않는 파일 형식: {file.filename}")
            response = jsonify({'error': '엑셀 파일(.xlsx)만 업로드 가능합니다'})
            return add_cors_headers(response), 400
        
        print("✅ 파일 검증 통과")
        
        # 엑셀 파일 읽기
        df = pd.read_excel(file)
        print(f"✅ 엑셀 파일 읽기 성공, 행 수: {len(df)}")
        print(f"📊 컬럼명: {list(df.columns)}")
        print(f"📋 첫 번째 행 데이터: {df.iloc[0].to_dict()}")
        
        created_count = 0
        for index, row in df.iterrows():
            print(f"🔍 처리 중인 행 {index + 1}: {row.to_dict()}")
            
            test_case = TestCase(
                project_id=row.get('project_id', 1),
                main_category=row.get('main_category', ''),
                sub_category=row.get('sub_category', ''),
                detail_category=row.get('detail_category', ''),
                pre_condition=row.get('pre_condition', ''),
                expected_result=row.get('expected_result', ''),
                result_status=row.get('result_status', 'N/T'),
                remark=row.get('remark', ''),
                environment=row.get('environment', 'dev'),
                automation_code_path=row.get('automation_code_path', ''),
                automation_code_type=row.get('automation_code_type', '')
            )
            
            print(f"📝 생성된 테스트 케이스: main_category='{test_case.main_category}', expected_result='{test_case.expected_result}'")
            
            db.session.add(test_case)
            created_count += 1
        
        try:
            db.session.commit()
            print(f"✅ {created_count}개의 테스트 케이스 생성 완료")
        except Exception as commit_error:
            print(f"❌ 데이터베이스 커밋 오류: {str(commit_error)}")
            db.session.rollback()
            raise commit_error
        
        response = jsonify({
            'message': f'{created_count}개의 테스트 케이스가 업로드되었습니다',
            'created_count': created_count
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        print(f"❌ 파일 업로드 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

# 엑셀 다운로드 API
@testcases_bp.route('/testcases/download', methods=['GET'])
def download_testcases_excel():
    """테스트 케이스를 엑셀 파일로 다운로드"""
    try:
        # 모든 테스트 케이스 조회
        test_cases = TestCase.query.all()
        
        # DataFrame 생성
        data = []
        for tc in test_cases:
            data.append({
                'id': tc.id,
                'project_id': tc.project_id,
                'main_category': tc.main_category,
                'sub_category': tc.sub_category,
                'detail_category': tc.detail_category,
                'pre_condition': tc.pre_condition,
                'expected_result': tc.expected_result,
                'result_status': tc.result_status,
                'remark': tc.remark,
                'environment': tc.environment,
                'automation_code_path': tc.automation_code_path,
                'automation_code_type': tc.automation_code_type,
                'created_at': tc.created_at.strftime('%Y-%m-%d %H:%M:%S') if tc.created_at else None
            })
        
        df = pd.DataFrame(data)
        
        # 엑셀 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='TestCases')
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'testcases_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
    except Exception as e:
        print(f"다운로드 에러: {str(e)}")
        response = jsonify({'error': f'파일 다운로드 중 오류가 발생했습니다: {str(e)}'})
        return add_cors_headers(response), 500

# 자동화 코드 실행 API
@testcases_bp.route('/testcases/<int:id>/execute', methods=['POST'])
def execute_automation_code(id):
    """테스트 케이스의 자동화 코드 실행"""
    try:
        test_case = TestCase.query.get_or_404(id)
        
        if not test_case.automation_code_path:
            response = jsonify({'error': '자동화 코드 경로가 설정되지 않았습니다'})
            return add_cors_headers(response), 400
        
        # 자동화 코드 실행
        script_path = test_case.automation_code_path
        script_type = test_case.automation_code_type or 'playwright'
        
        # 디버깅을 위한 로그 추가
        print(f"🔍 테스트 케이스 ID: {id}")
        print(f"🔍 자동화 코드 경로: {script_path}")
        print(f"🔍 자동화 코드 타입: {script_type}")
        
        # 스크립트 경로가 디렉토리인지 파일인지 확인
        if not script_path:
            response = jsonify({'error': '자동화 코드 경로가 설정되지 않았습니다'})
            return add_cors_headers(response), 400
        
        import time
        start_time = time.time()
        
        if script_type == 'k6':
            # k6 성능 테스트 실행
            from engines.k6_engine import k6_engine
            result = k6_engine.execute_test(script_path, {})
            execution_duration = time.time() - start_time
            
            # 실행 결과 저장
            test_result = TestResult(
                test_case_id=id,
                result=result['status'],
                environment=test_case.environment,
                execution_duration=execution_duration,
                error_message=result.get('error')
            )
            db.session.add(test_result)
            db.session.commit()
            
            response = jsonify({
                'message': '자동화 코드 실행 완료',
                'result': result['status'],
                'output': result.get('output', ''),
                'error': result.get('error', ''),
                'execution_duration': execution_duration
            })
            return add_cors_headers(response), 200
            
        elif script_type in ['selenium', 'playwright', 'k6']:
            # UI 테스트 실행
            if script_type == 'k6':
                # k6 실행
                import os
                # 스크립트 경로를 절대 경로로 변환
                if not os.path.isabs(script_path):
                    # 백엔드 디렉토리에서 상위 디렉토리로 이동
                    backend_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(backend_dir)
                    script_path = os.path.join(project_root, script_path)
                
                print(f"🔍 k6 실행 경로: {script_path}")
                print(f"📁 파일 존재 여부: {os.path.exists(script_path)}")
                print(f"📁 프로젝트 루트: {project_root}")
                print(f"📁 현재 작업 디렉토리: {os.getcwd()}")
                
                # 경로가 디렉토리인지 파일인지 확인
                if os.path.isdir(script_path):
                    # 디렉토리인 경우 해당 디렉토리에서 .js 파일 찾기
                    js_files = [f for f in os.listdir(script_path) if f.endswith('.js')]
                    if js_files:
                        script_path = os.path.join(script_path, js_files[0])
                        print(f"🔍 디렉토리에서 찾은 스크립트: {script_path}")
                    else:
                        response = jsonify({'error': f'디렉토리 {script_path}에서 .js 파일을 찾을 수 없습니다'})
                        return add_cors_headers(response), 400
                
                # 절대 경로 사용
                absolute_script_path = os.path.abspath(script_path)
                print(f"🔍 절대 경로: {absolute_script_path}")
                print(f"📁 절대 경로 파일 존재 여부: {os.path.exists(absolute_script_path)}")
                
                if not os.path.exists(absolute_script_path):
                    response = jsonify({'error': f'스크립트 파일을 찾을 수 없습니다: {absolute_script_path}'})
                    return add_cors_headers(response), 400
                
                # 환경 변수 설정
                env = os.environ.copy()
                env['K6_BROWSER_ENABLED'] = 'true'
                env['K6_BROWSER_HEADLESS'] = 'true'
                
                result = subprocess.run(
                    ['k6', 'run', absolute_script_path],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5분 타임아웃
                    cwd=project_root,  # 프로젝트 루트에서 실행
                    env=env
                )
            elif script_type == 'playwright':
                # Playwright 실행
                import os
                # 스크립트 경로를 절대 경로로 변환
                if not os.path.isabs(script_path):
                    backend_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(backend_dir)
                    script_path = os.path.join(project_root, script_path)
                
                # 경로가 디렉토리인지 파일인지 확인
                if os.path.isdir(script_path):
                    # 디렉토리인 경우 해당 디렉토리에서 .spec.js 파일 찾기
                    spec_files = [f for f in os.listdir(script_path) if f.endswith('.spec.js')]
                    if spec_files:
                        script_path = os.path.join(script_path, spec_files[0])
                        print(f"🔍 디렉토리에서 찾은 Playwright 스크립트: {script_path}")
                    else:
                        response = jsonify({'error': f'디렉토리 {script_path}에서 .spec.js 파일을 찾을 수 없습니다'})
                        return add_cors_headers(response), 400
                
                absolute_script_path = os.path.abspath(script_path)
                if not os.path.exists(absolute_script_path):
                    response = jsonify({'error': f'Playwright 스크립트 파일을 찾을 수 없습니다: {absolute_script_path}'})
                    return add_cors_headers(response), 400
                
                result = subprocess.run(
                    ['npx', 'playwright', 'test', absolute_script_path, '--reporter=json'],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5분 타임아웃
                    cwd=os.path.dirname(absolute_script_path) if os.path.dirname(absolute_script_path) else None
                )
            else:
                # Selenium 실행
                import os
                # 스크립트 경로를 절대 경로로 변환
                if not os.path.isabs(script_path):
                    backend_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(backend_dir)
                    script_path = os.path.join(project_root, script_path)
                
                # 경로가 디렉토리인지 파일인지 확인
                if os.path.isdir(script_path):
                    # 디렉토리인 경우 해당 디렉토리에서 .py 파일 찾기
                    py_files = [f for f in os.listdir(script_path) if f.endswith('.py')]
                    if py_files:
                        script_path = os.path.join(script_path, py_files[0])
                        print(f"🔍 디렉토리에서 찾은 Selenium 스크립트: {script_path}")
                    else:
                        response = jsonify({'error': f'디렉토리 {script_path}에서 .py 파일을 찾을 수 없습니다'})
                        return add_cors_headers(response), 400
                
                absolute_script_path = os.path.abspath(script_path)
                if not os.path.exists(absolute_script_path):
                    response = jsonify({'error': f'Selenium 스크립트 파일을 찾을 수 없습니다: {absolute_script_path}'})
                    return add_cors_headers(response), 400
                
                result = subprocess.run(
                    ['python', absolute_script_path],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5분 타임아웃
                    cwd=os.path.dirname(absolute_script_path) if os.path.dirname(absolute_script_path) else None
                )
            
            execution_duration = time.time() - start_time
            
            # 스크린샷 경로 생성 (Playwright의 경우)
            screenshot_path = None
            if script_type == 'playwright' and result.returncode == 0:
                # Playwright 테스트 결과에서 스크린샷 경로 추출
                try:
                    import json
                    import os
                    from datetime import datetime
                    
                    # 테스트 결과 디렉토리 생성
                    screenshot_dir = os.path.join('screenshots', f'testcase_{id}')
                    os.makedirs(screenshot_dir, exist_ok=True)
                    
                    # 스크린샷 파일명 생성
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    screenshot_path = os.path.join(screenshot_dir, f'screenshot_{timestamp}.png')
                    
                    # Playwright 실행 결과에서 스크린샷 복사 (실제 구현에서는 더 복잡)
                    if os.path.exists('test-results'):
                        import shutil
                        for root, dirs, files in os.walk('test-results'):
                            for file in files:
                                if file.endswith('.png'):
                                    shutil.copy2(os.path.join(root, file), screenshot_path)
                                    break
                except Exception as e:
                    print(f"스크린샷 처리 중 오류: {e}")
            
            # 실행 결과 저장
            test_result = TestResult(
                test_case_id=id,
                result='Pass' if result.returncode == 0 else 'Fail',
                environment=test_case.environment,
                execution_duration=execution_duration,
                error_message=result.stderr if result.returncode != 0 else None,
                screenshot=screenshot_path
            )
            db.session.add(test_result)
            db.session.commit()
            
            response = jsonify({
                'message': '자동화 코드 실행 완료',
                'result': 'Pass' if result.returncode == 0 else 'Fail',
                'output': result.stdout,
                'error': result.stderr,
                'execution_duration': execution_duration,
                'screenshot_path': screenshot_path
            })
            return add_cors_headers(response), 200
        else:
            response = jsonify({'error': '지원하지 않는 자동화 코드 타입입니다'})
            return add_cors_headers(response), 400
        
    except subprocess.TimeoutExpired:
        response = jsonify({'error': '자동화 코드 실행 시간이 초과되었습니다'})
        return add_cors_headers(response), 408
    except Exception as e:
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500 