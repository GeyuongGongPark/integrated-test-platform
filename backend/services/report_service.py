"""
고급 리포트 및 대시보드 서비스
커스텀 리포트 생성, 리포트 빌더, 다양한 출력 형식 지원
"""
from models import db, CustomReport, ReportExecution, TestCase, TestResult, TestPlan, TestExecution
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
from datetime import datetime, timedelta
import json
import os

logger = get_logger(__name__)

class ReportService:
    """리포트 서비스"""
    
    def create_report(self, name, report_type, config, created_by, description=None, 
                     template=None, output_format='html', filters=None, project_id=None):
        """
        커스텀 리포트 생성
        
        Args:
            name: 리포트 이름
            report_type: 리포트 타입
            config: 리포트 설정 (dict)
            created_by: 생성자 ID
            description: 설명
            template: 템플릿 (HTML 또는 마크다운)
            output_format: 출력 형식
            filters: 필터 설정 (dict)
            project_id: 프로젝트 ID
        
        Returns:
            CustomReport: 생성된 리포트
        """
        try:
            report = CustomReport(
                name=name,
                description=description,
                report_type=report_type,
                config=json.dumps(config) if config else '{}',
                template=template,
                output_format=output_format,
                filters=json.dumps(filters) if filters else '{}',
                project_id=project_id,
                created_by=created_by
            )
            
            db.session.add(report)
            db.session.commit()
            
            logger.info(f"리포트 생성 완료: {name} (ID: {report.id})")
            return report
            
        except Exception as e:
            logger.error(f"리포트 생성 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def generate_report(self, report_id, execution_params=None, executed_by=None):
        """
        리포트 생성 및 실행
        
        Args:
            report_id: 리포트 ID
            execution_params: 실행 파라미터 (dict)
            executed_by: 실행자 ID
        
        Returns:
            ReportExecution: 실행 기록
        """
        try:
            report = CustomReport.query.get(report_id)
            if not report:
                raise ValueError(f"리포트를 찾을 수 없습니다: {report_id}")
            
            # 실행 기록 생성
            execution = ReportExecution(
                report_id=report_id,
                status='running',
                execution_params=json.dumps(execution_params) if execution_params else '{}',
                executed_by=executed_by
            )
            db.session.add(execution)
            db.session.commit()
            
            try:
                # 리포트 타입에 따라 데이터 수집
                config = json.loads(report.config) if report.config else {}
                filters = json.loads(report.filters) if report.filters else {}
                
                # 실행 파라미터와 필터 병합
                if execution_params:
                    filters.update(execution_params)
                
                # 데이터 수집
                data = self._collect_report_data(report.report_type, config, filters)
                
                # 리포트 생성
                result_file_path = self._generate_report_file(
                    report, data, execution.id
                )
                
                # 실행 기록 업데이트
                execution.status = 'completed'
                execution.completed_at = get_kst_now()
                execution.result_file_path = result_file_path
                db.session.commit()
                
                logger.info(f"리포트 생성 완료: {report.name} (Execution ID: {execution.id})")
                return execution
                
            except Exception as e:
                # 실행 실패 처리
                execution.status = 'failed'
                execution.completed_at = get_kst_now()
                execution.error_message = str(e)
                db.session.commit()
                logger.error(f"리포트 생성 실패: {str(e)}")
                raise
            
        except Exception as e:
            logger.error(f"리포트 실행 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def _collect_report_data(self, report_type, config, filters):
        """리포트 타입에 따라 데이터 수집"""
        try:
            if report_type == 'test_execution':
                return self._collect_test_execution_data(config, filters)
            elif report_type == 'test_coverage':
                return self._collect_test_coverage_data(config, filters)
            elif report_type == 'trend':
                return self._collect_trend_data(config, filters)
            elif report_type == 'custom':
                return self._collect_custom_data(config, filters)
            else:
                return {}
        except Exception as e:
            logger.error(f"데이터 수집 오류: {str(e)}")
            return {}
    
    def _collect_test_execution_data(self, config, filters):
        """테스트 실행 리포트 데이터 수집"""
        try:
            # 필터 적용
            query = TestResult.query
            
            # 날짜 범위 필터
            if 'start_date' in filters:
                start_date = datetime.fromisoformat(filters['start_date'])
                query = query.filter(TestResult.executed_at >= start_date)
            if 'end_date' in filters:
                end_date = datetime.fromisoformat(filters['end_date'])
                query = query.filter(TestResult.executed_at <= end_date)
            
            # 환경 필터
            if 'environment' in filters:
                query = query.join(TestCase).filter(TestCase.environment == filters['environment'])
            
            # 프로젝트 필터
            if 'project_id' in filters:
                query = query.join(TestCase).filter(TestCase.project_id == filters['project_id'])
            
            results = query.order_by(TestResult.executed_at.desc()).all()
            
            # 통계 계산
            total = len(results)
            passed = sum(1 for r in results if r.result == 'Pass')
            failed = sum(1 for r in results if r.result == 'Fail')
            blocked = sum(1 for r in results if r.result == 'Blocked')
            
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            # 테스트 케이스별 통계
            test_case_stats = {}
            for result in results:
                tc_id = result.test_case_id
                if tc_id not in test_case_stats:
                    test_case_stats[tc_id] = {
                        'test_case_id': tc_id,
                        'test_case_name': result.test_case.name if result.test_case else 'Unknown',
                        'total': 0,
                        'passed': 0,
                        'failed': 0,
                        'pass_rate': 0
                    }
                test_case_stats[tc_id]['total'] += 1
                if result.result == 'Pass':
                    test_case_stats[tc_id]['passed'] += 1
                elif result.result == 'Fail':
                    test_case_stats[tc_id]['failed'] += 1
            
            for stats in test_case_stats.values():
                stats['pass_rate'] = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            return {
                'summary': {
                    'total': total,
                    'passed': passed,
                    'failed': failed,
                    'blocked': blocked,
                    'pass_rate': round(pass_rate, 2)
                },
                'test_case_stats': list(test_case_stats.values()),
                'results': [r.to_dict() for r in results[:100]]  # 최대 100개만
            }
            
        except Exception as e:
            logger.error(f"테스트 실행 데이터 수집 오류: {str(e)}")
            return {}
    
    def _collect_test_coverage_data(self, config, filters):
        """테스트 커버리지 리포트 데이터 수집"""
        try:
            # 프로젝트별 테스트 케이스 수
            query = TestCase.query.filter_by(status='active')
            
            if 'project_id' in filters:
                query = query.filter(TestCase.project_id == filters['project_id'])
            
            test_cases = query.all()
            
            # 카테고리별 커버리지
            category_coverage = {}
            for tc in test_cases:
                category = tc.main_category or 'Uncategorized'
                if category not in category_coverage:
                    category_coverage[category] = {
                        'category': category,
                        'total': 0,
                        'automated': 0,
                        'manual': 0,
                        'coverage_rate': 0
                    }
                category_coverage[category]['total'] += 1
                if tc.automation_code_path:
                    category_coverage[category]['automated'] += 1
                else:
                    category_coverage[category]['manual'] += 1
            
            for stats in category_coverage.values():
                stats['coverage_rate'] = (stats['automated'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            return {
                'total_test_cases': len(test_cases),
                'automated_count': sum(1 for tc in test_cases if tc.automation_code_path),
                'manual_count': sum(1 for tc in test_cases if not tc.automation_code_path),
                'category_coverage': list(category_coverage.values())
            }
            
        except Exception as e:
            logger.error(f"테스트 커버리지 데이터 수집 오류: {str(e)}")
            return {}
    
    def _collect_trend_data(self, config, filters):
        """트렌드 리포트 데이터 수집"""
        try:
            # 날짜 범위 설정
            end_date = datetime.now()
            days = filters.get('days', 30)
            start_date = end_date - timedelta(days=days)
            
            # 일별 통계
            daily_stats = {}
            current_date = start_date.date()
            while current_date <= end_date.date():
                daily_stats[str(current_date)] = {
                    'date': str(current_date),
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'pass_rate': 0
                }
                current_date += timedelta(days=1)
            
            # 결과 조회
            results = TestResult.query.filter(
                TestResult.executed_at >= start_date,
                TestResult.executed_at <= end_date
            ).all()
            
            # 일별 통계 계산
            for result in results:
                date_str = result.executed_at.date().isoformat()
                if date_str in daily_stats:
                    daily_stats[date_str]['total'] += 1
                    if result.result == 'Pass':
                        daily_stats[date_str]['passed'] += 1
                    elif result.result == 'Fail':
                        daily_stats[date_str]['failed'] += 1
            
            # 통과율 계산
            for stats in daily_stats.values():
                if stats['total'] > 0:
                    stats['pass_rate'] = round((stats['passed'] / stats['total'] * 100), 2)
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'daily_stats': list(daily_stats.values())
            }
            
        except Exception as e:
            logger.error(f"트렌드 데이터 수집 오류: {str(e)}")
            return {}
    
    def _collect_custom_data(self, config, filters):
        """커스텀 리포트 데이터 수집"""
        # 사용자 정의 데이터 수집 로직
        return {}
    
    def _generate_report_file(self, report, data, execution_id):
        """리포트 파일 생성"""
        try:
            # 리포트 디렉토리 생성
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            
            # 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{report.id}_{execution_id}_{timestamp}"
            
            if report.output_format == 'html':
                filepath = os.path.join(reports_dir, f"{filename}.html")
                content = self._generate_html_report(report, data)
            elif report.output_format == 'json':
                filepath = os.path.join(reports_dir, f"{filename}.json")
                content = json.dumps(data, indent=2, ensure_ascii=False)
            elif report.output_format == 'csv':
                filepath = os.path.join(reports_dir, f"{filename}.csv")
                content = self._generate_csv_report(report, data)
            else:
                filepath = os.path.join(reports_dir, f"{filename}.txt")
                content = str(data)
            
            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filepath
            
        except Exception as e:
            logger.error(f"리포트 파일 생성 오류: {str(e)}")
            raise
    
    def _generate_html_report(self, report, data):
        """HTML 리포트 생성"""
        if report.template:
            # 커스텀 템플릿 사용
            template = report.template
            # 데이터를 템플릿에 삽입
            for key, value in data.items():
                template = template.replace(f'{{{{{key}}}}}', str(value))
            return template
        else:
            # 기본 HTML 템플릿
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>{report.name}</h1>
    <p>생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>
</body>
</html>
"""
            return html
    
    def _generate_csv_report(self, report, data):
        """CSV 리포트 생성"""
        import csv
        import io
        
        output = io.StringIO()
        
        if 'results' in data:
            # 테스트 결과 CSV
            writer = csv.DictWriter(output, fieldnames=['test_case_id', 'test_case_name', 'result', 'executed_at'])
            writer.writeheader()
            for result in data['results']:
                writer.writerow({
                    'test_case_id': result.get('test_case_id'),
                    'test_case_name': result.get('test_case_name'),
                    'result': result.get('result'),
                    'executed_at': result.get('executed_at')
                })
        else:
            # 기본 CSV
            writer = csv.writer(output)
            for key, value in data.items():
                writer.writerow([key, str(value)])
        
        return output.getvalue()

# 전역 리포트 서비스 인스턴스
report_service = ReportService()

