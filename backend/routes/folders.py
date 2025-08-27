from flask import Blueprint, request, jsonify
from models import db, Folder, TestCase
from utils.cors import add_cors_headers
from utils.auth_decorators import guest_allowed, user_required, admin_required
from datetime import datetime

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
            'created_at': f.created_at.isoformat() if f.created_at else None
        } for f in folders]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
    except Exception as e:
        print(f"❌ 폴더 조회 오류: {str(e)}")
        response = jsonify({'error': '폴더 조회 오류', 'message': str(e)})
        return add_cors_headers(response), 500

@folders_bp.route('/folders', methods=['POST'])
@user_required
def create_folder():
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('folder_name'):
            response = jsonify({'error': '폴더명은 필수입니다'})
            return add_cors_headers(response), 400
        
        folder = Folder(
            folder_name=data.get('folder_name'),
            parent_folder_id=data.get('parent_folder_id'),
            folder_type=data.get('folder_type', 'environment'),
            environment=data.get('environment'),
            deployment_date=datetime.strptime(data.get('deployment_date'), '%Y-%m-%d').date() if data.get('deployment_date') else None
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
        
        folder.folder_name = data.get('folder_name', folder.folder_name)
        folder.parent_folder_id = data.get('parent_folder_id', folder.parent_folder_id)
        folder.folder_type = data.get('folder_type', folder.folder_type)
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
    """환경별 → 배포일자별 → 기능명별 폴더 트리 구조 반환"""
    try:
        # 환경별 폴더 조회 (folder_type이 'environment'이거나 null인 상위 폴더들)
        environment_folders = Folder.query.filter(
            (Folder.folder_type == 'environment') | 
            ((Folder.folder_type.is_(None)) & (Folder.parent_folder_id.is_(None)))
        ).all()
        
        print(f"🔍 환경 폴더 수: {len(environment_folders)}")
        
        tree = []
        for env_folder in environment_folders:
            # folder_type이 null인 경우 환경 이름에서 타입 추정
            folder_type = env_folder.folder_type
            if folder_type is None:
                if 'DEV' in env_folder.folder_name.upper():
                    folder_type = 'environment'
                    env_folder.environment = 'dev'
                elif 'ALPHA' in env_folder.folder_name.upper():
                    folder_type = 'environment'
                    env_folder.environment = 'alpha'
                elif 'PRODUCTION' in env_folder.folder_name.upper():
                    folder_type = 'environment'
                    env_folder.environment = 'production'
                else:
                    folder_type = 'environment'
                    env_folder.environment = 'unknown'
            
            env_node = {
                'id': env_folder.id,
                'name': env_folder.folder_name,
                'type': 'environment',
                'environment': env_folder.environment,
                'children': []
            }
            
            print(f"🌍 환경 폴더: {env_folder.folder_name} (ID: {env_folder.id})")
            
            # 해당 환경의 배포일자별 폴더 조회 (folder_type이 'deployment_date'이거나 null인 하위 폴더들)
            deployment_folders = Folder.query.filter(
                ((Folder.folder_type == 'deployment_date') | (Folder.folder_type.is_(None))) &
                (Folder.parent_folder_id == env_folder.id)
            ).all()
            
            print(f"📅 배포일자 폴더 수: {len(deployment_folders)}")
            
            for dep_folder in deployment_folders:
                # folder_type이 null인 경우 배포일자로 추정
                dep_folder_type = dep_folder.folder_type
                if dep_folder_type is None:
                    dep_folder_type = 'deployment_date'
                
                dep_node = {
                    'id': dep_folder.id,
                    'name': dep_folder.folder_name,
                    'type': 'deployment_date',
                    'deployment_date': dep_folder.deployment_date.strftime('%Y-%m-%d') if dep_folder.deployment_date else (dep_folder.folder_name or 'Unknown'),
                    'children': []
                }
                
                print(f"📅 배포일자 폴더: {dep_folder.folder_name} (ID: {dep_folder.id})")
                
                # 해당 배포일자의 기능명별 폴더 조회 (folder_type이 'feature'이거나 null인 하위 폴더들)
                feature_folders = Folder.query.filter(
                    ((Folder.folder_type == 'feature') | (Folder.folder_type.is_(None))) &
                    (Folder.parent_folder_id == dep_folder.id)
                ).all()
                
                print(f"🔧 기능명 폴더 수: {len(feature_folders)}")
                
                for feature_folder in feature_folders:
                    # folder_type이 null인 경우 기능명으로 추정
                    feature_folder_type = feature_folder.folder_type
                    if feature_folder_type is None:
                        feature_folder_type = 'feature'
                    
                    feature_node = {
                        'id': feature_folder.id,
                        'name': feature_folder.folder_name,
                        'type': 'feature',
                        'children': []
                    }
                    
                    print(f"🔧 기능명 폴더: {feature_folder.folder_name} (ID: {feature_folder.id})")
                    
                    # 기능명 폴더에 하위 폴더가 있을 수 있지만, 여기서는 3단계까지만 표시
                    dep_node['children'].append(feature_node)
                
                # 테스트 케이스는 제외하고 폴더만 반환
                env_node['children'].append(dep_node)
            
            tree.append(env_node)
        
        response = jsonify(tree)
        return add_cors_headers(response), 200
        
    except Exception as e:
        print(f"❌ 폴더 트리 조회 오류: {str(e)}")
        response = jsonify({'error': '폴더 트리 조회 오류', 'message': str(e)})
        return add_cors_headers(response), 500 