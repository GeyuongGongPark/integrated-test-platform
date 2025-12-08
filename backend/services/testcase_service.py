"""
테스트 케이스 서비스 레이어
"""
from models import db, TestCase, TestResult, Folder
from utils.serializers import serialize_testcase
from utils.logger import get_logger
from sqlalchemy import func

logger = get_logger(__name__)


class TestCaseService:
    """테스트 케이스 관련 비즈니스 로직"""
    
    @staticmethod
    def get_testcases(page=None, per_page=None, include_relations=False):
        """테스트 케이스 목록 조회"""
        if page is None or per_page is None:
            testcases = TestCase.query.all()
            return [serialize_testcase(tc, include_relations) for tc in testcases], None
        
        # 페이징 처리
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        total_count = TestCase.query.count()
        offset = (page - 1) * per_page
        testcases = TestCase.query.offset(offset).limit(per_page).all()
        
        total_pages = (total_count + per_page - 1) // per_page
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total_count,
            'pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'next_num': page + 1 if page < total_pages else None,
            'prev_num': page - 1 if page > 1 else None
        }
        
        data = [serialize_testcase(tc, include_relations) for tc in testcases]
        return data, pagination
    
    @staticmethod
    def get_testcase_by_id(testcase_id):
        """테스트 케이스 단일 조회"""
        testcase = TestCase.query.get_or_404(testcase_id)
        return serialize_testcase(testcase, include_relations=True)
    
    @staticmethod
    def create_testcase(data, user_id=None):
        """테스트 케이스 생성"""
        from utils.common_helpers import get_or_create_default_project, get_or_create_default_folder
        
        # 프로젝트 ID 설정
        project_id = data.get('project_id')
        if not project_id:
            default_project = get_or_create_default_project()
            project_id = default_project.id
        
        # 폴더 ID 설정
        folder_id = data.get('folder_id')
        if not folder_id:
            default_folder = get_or_create_default_folder()
            if default_folder:
                folder_id = default_folder.id
        
        # 폴더의 환경 정보 가져오기
        folder_environment = 'dev'
        if folder_id:
            folder = Folder.query.get(folder_id)
            if folder:
                folder_environment = folder.environment
        
        testcase = TestCase(
            name=data.get('name'),
            description=data.get('description'),
            test_type=data.get('test_type'),
            script_path=data.get('script_path'),
            folder_id=folder_id,
            project_id=project_id,
            main_category=data.get('main_category'),
            sub_category=data.get('sub_category'),
            detail_category=data.get('detail_category'),
            pre_condition=data.get('pre_condition'),
            expected_result=data.get('expected_result'),
            remark=data.get('remark'),
            automation_code_path=data.get('automation_code_path'),
            environment=folder_environment,
            creator_id=user_id
        )
        
        db.session.add(testcase)
        db.session.commit()
        
        return serialize_testcase(testcase, include_relations=True)
    
    @staticmethod
    def update_testcase(testcase_id, data):
        """테스트 케이스 업데이트"""
        testcase = TestCase.query.get_or_404(testcase_id)
        
        for key, value in data.items():
            if hasattr(testcase, key) and value is not None:
                setattr(testcase, key, value)
        
        db.session.commit()
        return serialize_testcase(testcase, include_relations=True)
    
    @staticmethod
    def delete_testcase(testcase_id):
        """테스트 케이스 삭제"""
        testcase = TestCase.query.get_or_404(testcase_id)
        db.session.delete(testcase)
        db.session.commit()
        return True
    
    @staticmethod
    def get_testcase_statistics():
        """테스트 케이스 통계 조회"""
        # 환경별 통계
        environment_stats = db.session.query(
            TestCase.environment,
            func.count(TestCase.id).label('total'),
            func.sum(func.case([(TestCase.result_status == 'Pass', 1)], else_=0)).label('passed'),
            func.sum(func.case([(TestCase.result_status == 'Fail', 1)], else_=0)).label('failed'),
            func.sum(func.case([(TestCase.result_status == 'N/T', 1)], else_=0)).label('not_tested'),
            func.sum(func.case([(TestCase.result_status == 'N/A', 1)], else_=0)).label('not_applicable'),
            func.sum(func.case([(TestCase.result_status == 'Block', 1)], else_=0)).label('blocked')
        ).group_by(TestCase.environment).all()
        
        # 카테고리별 통계
        category_stats = db.session.query(
            TestCase.main_category,
            func.count(TestCase.id).label('total'),
            func.sum(func.case([(TestCase.result_status == 'Pass', 1)], else_=0)).label('passed'),
            func.sum(func.case([(TestCase.result_status == 'Fail', 1)], else_=0)).label('failed')
        ).group_by(TestCase.main_category).all()
        
        # 자동화 통계
        automation_stats = db.session.query(
            func.count(TestCase.id).label('total'),
            func.sum(func.case([(TestCase.automation_code_path.isnot(None), 1)], else_=0)).label('automated'),
            func.sum(func.case([(TestCase.automation_code_path.is_(None), 1)], else_=0)).label('manual')
        ).first()
        
        return {
            'environment_stats': [{
                'environment': stat.environment or 'Unknown',
                'total': stat.total,
                'passed': stat.passed or 0,
                'failed': stat.failed or 0,
                'not_tested': stat.not_tested or 0,
                'not_applicable': stat.not_applicable or 0,
                'blocked': stat.blocked or 0,
                'pass_rate': round((stat.passed or 0) / stat.total * 100, 1) if stat.total > 0 else 0
            } for stat in environment_stats],
            
            'category_stats': [{
                'category': stat.main_category or 'Unknown',
                'total': stat.total,
                'passed': stat.passed or 0,
                'failed': stat.failed or 0,
                'pass_rate': round((stat.passed or 0) / stat.total * 100, 1) if stat.total > 0 else 0
            } for stat in category_stats],
            
            'automation_stats': {
                'total': automation_stats.total,
                'automated': automation_stats.automated or 0,
                'manual': automation_stats.manual or 0,
                'automation_rate': round((automation_stats.automated or 0) / automation_stats.total * 100, 1) if automation_stats.total > 0 else 0
            }
        }

