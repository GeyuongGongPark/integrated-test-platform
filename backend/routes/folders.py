from flask import Blueprint, request, jsonify
from models import db, Folder, TestCase, Project
from utils.cors import add_cors_headers
from utils.auth_decorators import guest_allowed, user_required, admin_required
from utils.response_utils import (
    success_response, error_response, created_response, 
    validation_error_response, not_found_response
)
from utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

# Blueprint 생성
folders_bp = Blueprint('folders', __name__)

# 폴더 관리 API
@folders_bp.route('/folders', methods=['GET'])
@guest_allowed
def get_folders():
    try:
        folders = Folder.query.all()
        data = [{
            'id': f.id, 
            'folder_name': f.folder_name, 
            'parent_folder_id': f.parent_folder_id,
            'folder_type': f.folder_type,
            'environment': f.environment,
            'deployment_date': f.deployment_date.strftime('%Y-%m-%d') if f.deployment_date else None,
            'project_id': f.project_id,
            'created_at': f.created_at.isoformat() if f.created_at else None
        } for f in folders]
        
        response = success_response(data=data, message='폴더 목록을 성공적으로 조회했습니다.')
        return add_cors_headers(response[0]), response[1]
    except Exception as e:
        logger.error(f"폴더 조회 오류: {str(e)}")
        response = error_response('폴더 조회 중 오류가 발생했습니다.')
        return add_cors_headers(response[0]), response[1]

@folders_bp.route('/folders', methods=['POST'])
@user_required
def create_folder():
    try:
        data = request.get_json()
        parent_id = data.get('parent_folder_id')
        folder_type = data.get('folder_type', 'environment')
        
        # 필수 필드 검증
        if not data.get('folder_name'):
            response = jsonify({'error': '폴더명은 필수입니다'})
            return add_cors_headers(response), 400

        # 부모 폴더 검증 및 타입 제한
        parent_folder = None
        if parent_id:
            parent_folder = Folder.query.get_or_404(parent_id)
            if parent_folder.folder_type in (None, 'environment') and folder_type != 'deployment_date':
                return add_cors_headers(jsonify({'error': '환경 폴더 아래에는 배포일자 폴더만 생성할 수 있습니다.'})), 400
            if parent_folder.folder_type == 'deployment_date' and folder_type != 'feature':
                return add_cors_headers(jsonify({'error': '배포일자 폴더 아래에는 기능 폴더만 생성할 수 있습니다.'})), 400
            if parent_folder.folder_type == 'feature':
                return add_cors_headers(jsonify({'error': '기능 폴더 아래에는 더 이상 하위 폴더를 만들 수 없습니다.'})), 400

        # 프로젝트 결정: 부모 우선, 없으면 요청값, 최종 기본 2
        project_id = parent_folder.project_id if parent_folder else data.get('project_id') or 2

        # 환경 값 결정
        environment = data.get('environment')
        if parent_folder:
            environment = parent_folder.environment
        if folder_type == 'environment' and not environment:
            environment = 'dev'

        deployment_date = datetime.strptime(data.get('deployment_date'), '%Y-%m-%d').date() if data.get('deployment_date') else None
        
        folder = Folder(
            folder_name=data.get('folder_name'),
            parent_folder_id=parent_id,
            folder_type=folder_type,
            environment=environment,
            deployment_date=deployment_date,
            project_id=project_id
        )
        
        db.session.add(folder)
        db.session.commit()
        
        response = jsonify({
            'message': '폴더 생성 완료', 
            'id': folder.id,
            'folder_name': folder.folder_name,
            'folder_type': folder.folder_type,
            'environment': folder.environment
        })
        return add_cors_headers(response), 201
    except Exception as e:
        print(f"❌ 폴더 생성 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': '폴더 생성 오류', 'message': str(e)})
        return add_cors_headers(response), 500

@folders_bp.route('/folders/<int:id>', methods=['GET'])
@guest_allowed
def get_folder(id):
    try:
        folder = Folder.query.get_or_404(id)
        data = {
            'id': folder.id,
            'folder_name': folder.folder_name,
            'parent_folder_id': folder.parent_folder_id,
            'folder_type': folder.folder_type,
            'environment': folder.environment,
            'deployment_date': folder.deployment_date.strftime('%Y-%m-%d') if folder.deployment_date else None,
            'project_id': folder.project_id,
            'created_at': folder.created_at.isoformat() if folder.created_at else None
        }
        
        response = jsonify(data)
        return add_cors_headers(response), 200
    except Exception as e:
        print(f"❌ 폴더 조회 오류: {str(e)}")
        response = jsonify({'error': '폴더 조회 오류', 'message': str(e)})
        return add_cors_headers(response), 500

@folders_bp.route('/folders/<int:id>', methods=['PUT'])
@user_required
def update_folder(id):
    try:
        folder = Folder.query.get_or_404(id)
        data = request.get_json()

        parent_id = data.get('parent_folder_id', folder.parent_folder_id)
        parent_folder = Folder.query.get(parent_id) if parent_id else None
        new_folder_type = data.get('folder_type', folder.folder_type)

        # 타입 검증
        if parent_folder:
            if parent_folder.folder_type in (None, 'environment') and new_folder_type != 'deployment_date':
                return add_cors_headers(jsonify({'error': '환경 폴더 아래에는 배포일자 폴더만 둘 수 있습니다.'})), 400
            if parent_folder.folder_type == 'deployment_date' and new_folder_type != 'feature':
                return add_cors_headers(jsonify({'error': '배포일자 폴더 아래에는 기능 폴더만 둘 수 있습니다.'})), 400
            if parent_folder.folder_type == 'feature':
                return add_cors_headers(jsonify({'error': '기능 폴더 아래에는 더 이상 하위 폴더를 둘 수 없습니다.'})), 400

        folder.folder_name = data.get('folder_name', folder.folder_name)
        folder.parent_folder_id = parent_id
        folder.folder_type = new_folder_type

        if parent_folder:
            folder.project_id = parent_folder.project_id
            folder.environment = parent_folder.environment
        else:
            folder.project_id = data.get('project_id', folder.project_id or 2)
            folder.environment = data.get('environment', folder.environment)
        
        if data.get('deployment_date'):
            folder.deployment_date = datetime.strptime(data.get('deployment_date'), '%Y-%m-%d').date()
        
        db.session.commit()
        
        response = jsonify({'message': '폴더 업데이트 완료'})
        return add_cors_headers(response), 200
    except Exception as e:
        print(f"❌ 폴더 업데이트 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': '폴더 업데이트 오류', 'message': str(e)})
        return add_cors_headers(response), 500

@folders_bp.route('/folders/<int:id>', methods=['DELETE'])
@admin_required
def delete_folder(id):
    try:
        folder = Folder.query.get_or_404(id)
        
        # 하위 폴더가 있는지 확인
        child_folders = Folder.query.filter_by(parent_folder_id=id).all()
        if child_folders:
            response = jsonify({'error': '하위 폴더가 있어서 삭제할 수 없습니다. 먼저 하위 폴더를 삭제해주세요.'})
            return add_cors_headers(response), 400
        
        # 해당 폴더에 속한 테스트 케이스가 있는지 확인
        test_cases = TestCase.query.filter_by(folder_id=id).all()
        if test_cases:
            response = jsonify({'error': '테스트 케이스가 있어서 삭제할 수 없습니다. 먼저 테스트 케이스를 이동하거나 삭제해주세요.'})
            return add_cors_headers(response), 400
        
        db.session.delete(folder)
        db.session.commit()
        
        response = jsonify({'message': '폴더 삭제 완료'})
        return add_cors_headers(response), 200
    except Exception as e:
        print(f"❌ 폴더 삭제 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': '폴더 삭제 오류', 'message': str(e)})
        return add_cors_headers(response), 500

# 폴더 트리 구조 API
@folders_bp.route('/folders/tree', methods=['GET'])
@guest_allowed
def get_folder_tree():
    """프로젝트 → 환경 → 배포일자 → 기능 폴더 트리 구조 반환"""
    try:
        # 기존 project_id 없는 폴더는 기본 프로젝트(2)로 매칭
        legacy_folders = Folder.query.filter(Folder.project_id.is_(None)).all()
        if legacy_folders:
            for lf in legacy_folders:
                lf.project_id = 2
            db.session.commit()

        tree = []

        projects = Project.query.all()
        for project in projects:
            project_node = {
                'id': project.id,
                'name': project.name,
                'type': 'project',
                'children': []
            }

            environment_folders = Folder.query.filter(
                (Folder.project_id == project.id) &
                (Folder.parent_folder_id.is_(None)) &
                ((Folder.folder_type == 'environment') | (Folder.folder_type.is_(None)))
            ).all()

            for env_folder in environment_folders:
                env_node = {
                    'id': env_folder.id,
                    'name': env_folder.folder_name,
                    'type': 'environment',
                    'environment': env_folder.environment or 'dev',
                    'project_id': env_folder.project_id,
                    'children': []
                }

                deployment_folders = Folder.query.filter(
                    (Folder.parent_folder_id == env_folder.id) &
                    ((Folder.folder_type == 'deployment_date') | (Folder.folder_type.is_(None)))
                ).all()

                for dep_folder in deployment_folders:
                    dep_node = {
                        'id': dep_folder.id,
                        'name': dep_folder.folder_name,
                        'type': 'deployment_date',
                        'deployment_date': dep_folder.deployment_date.strftime('%Y-%m-%d') if dep_folder.deployment_date else (dep_folder.folder_name or 'Unknown'),
                        'project_id': dep_folder.project_id,
                        'children': []
                    }

                    feature_folders = Folder.query.filter(
                        (Folder.parent_folder_id == dep_folder.id) &
                        ((Folder.folder_type == 'feature') | (Folder.folder_type.is_(None)))
                    ).all()

                    for feature_folder in feature_folders:
                        feature_node = {
                            'id': feature_folder.id,
                            'name': feature_folder.folder_name,
                            'type': 'feature',
                            'project_id': feature_folder.project_id,
                            'children': []
                        }
                        dep_node['children'].append(feature_node)

                    env_node['children'].append(dep_node)

                project_node['children'].append(env_node)

            tree.append(project_node)

        response = jsonify(tree)
        return add_cors_headers(response), 200
        
    except Exception as e:
        print(f"❌ 폴더 트리 조회 오류: {str(e)}")
        response = jsonify({'error': '폴더 트리 조회 오류', 'message': str(e)})
        return add_cors_headers(response), 500 