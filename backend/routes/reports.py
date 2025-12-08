"""
고급 리포트 및 대시보드 API
"""
from flask import Blueprint, request, jsonify, send_file
from models import db, CustomReport, ReportExecution
from utils.cors import add_cors_headers
from utils.auth_decorators import user_required, guest_allowed
from utils.logger import get_logger
from services.report_service import report_service
import os

logger = get_logger(__name__)

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_reports():
    """리포트 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        report_type = request.args.get('report_type')
        project_id = request.args.get('project_id', type=int)
        
        query = CustomReport.query
        
        if report_type:
            query = query.filter(CustomReport.report_type == report_type)
        if project_id:
            query = query.filter(CustomReport.project_id == project_id)
        
        # 공개 리포트 또는 사용자가 생성한 리포트만 조회
        if hasattr(request, 'user') and request.user:
            query = query.filter(
                db.or_(
                    CustomReport.is_public == True,
                    CustomReport.created_by == request.user.id
                )
            )
        else:
            query = query.filter(CustomReport.is_public == True)
        
        reports = query.order_by(CustomReport.created_at.desc()).all()
        
        data = [r.to_dict() for r in reports]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"리포트 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@reports_bp.route('/reports/<int:id>', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_report(id):
    """리포트 상세 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        report = CustomReport.query.get_or_404(id)
        
        # 권한 확인
        if not report.is_public:
            if not hasattr(request, 'user') or not request.user or report.created_by != request.user.id:
                response = jsonify({'error': '리포트에 접근할 권한이 없습니다'})
                return add_cors_headers(response), 403
        
        response = jsonify(report.to_dict())
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"리포트 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@reports_bp.route('/reports', methods=['POST', 'OPTIONS'])
@user_required
def create_report():
    """리포트 생성"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('report_type') or not data.get('config'):
            response = jsonify({'error': 'name, report_type, config는 필수입니다'})
            return add_cors_headers(response), 400
        
        report = report_service.create_report(
            name=data['name'],
            report_type=data['report_type'],
            config=data['config'],
            created_by=request.user.id,
            description=data.get('description'),
            template=data.get('template'),
            output_format=data.get('output_format', 'html'),
            filters=data.get('filters'),
            project_id=data.get('project_id')
        )
        
        response = jsonify({
            'message': '리포트가 생성되었습니다',
            'report': report.to_dict()
        })
        return add_cors_headers(response), 201
        
    except Exception as e:
        logger.error(f"리포트 생성 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@reports_bp.route('/reports/<int:id>', methods=['PUT', 'OPTIONS'])
@user_required
def update_report(id):
    """리포트 수정"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        report = CustomReport.query.get_or_404(id)
        
        # 권한 확인
        if report.created_by != request.user.id:
            response = jsonify({'error': '리포트를 수정할 권한이 없습니다'})
            return add_cors_headers(response), 403
        
        data = request.get_json()
        import json
        
        if 'name' in data:
            report.name = data['name']
        if 'description' in data:
            report.description = data['description']
        if 'config' in data:
            report.config = json.dumps(data['config'])
        if 'template' in data:
            report.template = data['template']
        if 'output_format' in data:
            report.output_format = data['output_format']
        if 'filters' in data:
            report.filters = json.dumps(data['filters'])
        if 'is_public' in data:
            report.is_public = data['is_public']
        
        db.session.commit()
        
        response = jsonify({
            'message': '리포트가 수정되었습니다',
            'report': report.to_dict()
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"리포트 수정 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@reports_bp.route('/reports/<int:id>', methods=['DELETE', 'OPTIONS'])
@user_required
def delete_report(id):
    """리포트 삭제"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        report = CustomReport.query.get_or_404(id)
        
        # 권한 확인
        if report.created_by != request.user.id:
            response = jsonify({'error': '리포트를 삭제할 권한이 없습니다'})
            return add_cors_headers(response), 403
        
        db.session.delete(report)
        db.session.commit()
        
        response = jsonify({'message': '리포트가 삭제되었습니다'})
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"리포트 삭제 오류: {str(e)}")
        db.session.rollback()
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@reports_bp.route('/reports/<int:id>/generate', methods=['POST', 'OPTIONS'])
@user_required
def generate_report(id):
    """리포트 생성 및 실행"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        data = request.get_json() or {}
        execution_params = data.get('execution_params', {})
        
        execution = report_service.generate_report(
            report_id=id,
            execution_params=execution_params,
            executed_by=request.user.id
        )
        
        response = jsonify({
            'message': '리포트 생성이 시작되었습니다',
            'execution': execution.to_dict()
        })
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"리포트 생성 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@reports_bp.route('/reports/executions/<int:execution_id>', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_report_execution(execution_id):
    """리포트 실행 기록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        execution = ReportExecution.query.get_or_404(execution_id)
        
        response = jsonify(execution.to_dict())
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"리포트 실행 기록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@reports_bp.route('/reports/executions/<int:execution_id>/download', methods=['GET', 'OPTIONS'])
@guest_allowed
def download_report(execution_id):
    """리포트 파일 다운로드"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        execution = ReportExecution.query.get_or_404(execution_id)
        
        if execution.status != 'completed' or not execution.result_file_path:
            response = jsonify({'error': '리포트가 아직 생성되지 않았습니다'})
            return add_cors_headers(response), 400
        
        if not os.path.exists(execution.result_file_path):
            response = jsonify({'error': '리포트 파일을 찾을 수 없습니다'})
            return add_cors_headers(response), 404
        
        return send_file(
            execution.result_file_path,
            as_attachment=True,
            download_name=os.path.basename(execution.result_file_path)
        )
        
    except Exception as e:
        logger.error(f"리포트 다운로드 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@reports_bp.route('/reports/<int:id>/executions', methods=['GET', 'OPTIONS'])
@guest_allowed
def get_report_executions(id):
    """리포트의 실행 기록 목록 조회"""
    if request.method == 'OPTIONS':
        from app import handle_options_request
        return handle_options_request()
    
    try:
        executions = ReportExecution.query.filter_by(report_id=id).order_by(
            ReportExecution.started_at.desc()
        ).all()
        
        data = [e.to_dict() for e in executions]
        
        response = jsonify(data)
        return add_cors_headers(response), 200
        
    except Exception as e:
        logger.error(f"리포트 실행 기록 목록 조회 오류: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

