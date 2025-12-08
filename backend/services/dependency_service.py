"""
테스트 의존성 관리 서비스
의존성 그래프, 실행 순서 계산, 순환 의존성 검사
"""
from models import db, TestDependency, TestCase, TestResult
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
from collections import defaultdict, deque
import json

logger = get_logger(__name__)

class DependencyService:
    """테스트 의존성 관리 서비스"""
    
    def create_dependency(self, test_case_id, depends_on_test_case_id, dependency_type='required', condition=None, priority=1):
        """
        테스트 의존성 생성
        
        Args:
            test_case_id: 의존하는 테스트 케이스 ID
            depends_on_test_case_id: 의존 대상 테스트 케이스 ID
            dependency_type: 의존성 타입 ('required', 'optional', 'blocking')
            condition: 의존성 조건 (dict)
            priority: 우선순위
        
        Returns:
            TestDependency: 생성된 의존성
        """
        try:
            # 자기 자신에 대한 의존성 방지
            if test_case_id == depends_on_test_case_id:
                raise ValueError("테스트 케이스는 자기 자신에 의존할 수 없습니다")
            
            # 순환 의존성 검사
            if self._would_create_cycle(test_case_id, depends_on_test_case_id):
                raise ValueError("순환 의존성이 발생합니다")
            
            dependency = TestDependency(
                test_case_id=test_case_id,
                depends_on_test_case_id=depends_on_test_case_id,
                dependency_type=dependency_type,
                condition=json.dumps(condition) if condition else None,
                priority=priority
            )
            
            db.session.add(dependency)
            db.session.commit()
            
            logger.info(f"테스트 의존성 생성 완료: TestCase {test_case_id} -> TestCase {depends_on_test_case_id}")
            return dependency
            
        except Exception as e:
            logger.error(f"테스트 의존성 생성 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def _would_create_cycle(self, test_case_id, depends_on_test_case_id):
        """순환 의존성 발생 여부 확인"""
        # depends_on_test_case_id에서 test_case_id로 도달 가능한지 확인
        visited = set()
        queue = deque([depends_on_test_case_id])
        
        while queue:
            current_id = queue.popleft()
            if current_id == test_case_id:
                return True  # 순환 발견
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # 현재 테스트 케이스가 의존하는 테스트 케이스들 조회
            dependencies = TestDependency.query.filter_by(
                test_case_id=current_id,
                enabled=True
            ).all()
            
            for dep in dependencies:
                queue.append(dep.depends_on_test_case_id)
        
        return False
    
    def get_dependency_graph(self, test_case_ids=None):
        """
        의존성 그래프 조회
        
        Args:
            test_case_ids: 특정 테스트 케이스 ID 목록 (None이면 전체)
        
        Returns:
            dict: 의존성 그래프
        """
        try:
            query = TestDependency.query.filter_by(enabled=True)
            
            if test_case_ids:
                query = query.filter(
                    db.or_(
                        TestDependency.test_case_id.in_(test_case_ids),
                        TestDependency.depends_on_test_case_id.in_(test_case_ids)
                    )
                )
            
            dependencies = query.all()
            
            # 그래프 구성
            graph = defaultdict(list)
            reverse_graph = defaultdict(list)
            
            for dep in dependencies:
                graph[dep.test_case_id].append({
                    'id': dep.id,
                    'depends_on': dep.depends_on_test_case_id,
                    'type': dep.dependency_type,
                    'condition': json.loads(dep.condition) if dep.condition else None,
                    'priority': dep.priority
                })
                reverse_graph[dep.depends_on_test_case_id].append({
                    'id': dep.id,
                    'test_case': dep.test_case_id,
                    'type': dep.dependency_type,
                    'condition': json.loads(dep.condition) if dep.condition else None,
                    'priority': dep.priority
                })
            
            return {
                'forward': dict(graph),  # test_case_id -> depends_on 목록
                'reverse': dict(reverse_graph)  # depends_on -> test_case 목록
            }
            
        except Exception as e:
            logger.error(f"의존성 그래프 조회 오류: {str(e)}")
            return {'forward': {}, 'reverse': {}}
    
    def get_execution_order(self, test_case_ids):
        """
        테스트 케이스 실행 순서 계산 (위상 정렬)
        
        Args:
            test_case_ids: 실행할 테스트 케이스 ID 목록
        
        Returns:
            list: 실행 순서 (의존성 순서대로)
        """
        try:
            graph = self.get_dependency_graph(test_case_ids)
            forward_graph = graph['forward']
            
            # 위상 정렬 (Topological Sort)
            in_degree = defaultdict(int)
            
            # 진입 차수 계산
            for test_id in test_case_ids:
                in_degree[test_id] = 0
            
            for test_id, deps in forward_graph.items():
                if test_id in test_case_ids:
                    for dep in deps:
                        if dep['depends_on'] in test_case_ids:
                            in_degree[test_id] += 1
            
            # 큐에 진입 차수가 0인 노드 추가
            queue = deque([test_id for test_id in test_case_ids if in_degree[test_id] == 0])
            result = []
            
            while queue:
                # 우선순위에 따라 정렬 (priority가 낮을수록 먼저 실행)
                current = queue.popleft()
                result.append(current)
                
                # 현재 노드에 의존하는 노드들의 진입 차수 감소
                if current in forward_graph:
                    for dep in forward_graph[current]:
                        depends_on_id = dep['depends_on']
                        if depends_on_id in test_case_ids:
                            in_degree[depends_on_id] -= 1
                            if in_degree[depends_on_id] == 0:
                                queue.append(depends_on_id)
            
            # 순환 의존성 확인
            if len(result) != len(test_case_ids):
                remaining = set(test_case_ids) - set(result)
                logger.warning(f"순환 의존성 또는 의존성 조건 미충족: {remaining}")
                # 남은 테스트 케이스들을 결과에 추가
                result.extend(remaining)
            
            return result
            
        except Exception as e:
            logger.error(f"실행 순서 계산 오류: {str(e)}")
            return test_case_ids  # 오류 시 원래 순서 반환
    
    def check_dependency_conditions(self, test_case_id):
        """
        테스트 케이스의 의존성 조건 확인
        
        Args:
            test_case_id: 확인할 테스트 케이스 ID
        
        Returns:
            dict: 의존성 조건 충족 여부
        """
        try:
            dependencies = TestDependency.query.filter_by(
                test_case_id=test_case_id,
                enabled=True
            ).order_by(TestDependency.priority.asc()).all()
            
            if not dependencies:
                return {
                    'can_execute': True,
                    'blocked_by': [],
                    'missing_required': [],
                    'optional_missing': []
                }
            
            can_execute = True
            blocked_by = []
            missing_required = []
            optional_missing = []
            
            for dep in dependencies:
                # 의존 대상 테스트 케이스의 최신 결과 조회
                latest_result = TestResult.query.filter_by(
                    test_case_id=dep.depends_on_test_case_id
                ).order_by(TestResult.executed_at.desc()).first()
                
                condition = json.loads(dep.condition) if dep.condition else {}
                condition_met = True
                
                if condition:
                    # 조건 확인
                    if 'result' in condition:
                        if not latest_result or latest_result.result != condition['result']:
                            condition_met = False
                    
                    if 'status' in condition:
                        if not latest_result or latest_result.status != condition['status']:
                            condition_met = False
                    
                    if 'min_pass_rate' in condition:
                        # 최근 N개 결과의 통과율 확인
                        pass_rate = self._calculate_pass_rate(dep.depends_on_test_case_id, condition.get('recent_count', 10))
                        if pass_rate < condition['min_pass_rate']:
                            condition_met = False
                
                if not condition_met:
                    if dep.dependency_type == 'blocking':
                        can_execute = False
                        blocked_by.append({
                            'dependency_id': dep.id,
                            'depends_on_test_case_id': dep.depends_on_test_case_id,
                            'depends_on_test_case_name': dep.depends_on.name if dep.depends_on else None,
                            'condition': condition
                        })
                    elif dep.dependency_type == 'required':
                        can_execute = False
                        missing_required.append({
                            'dependency_id': dep.id,
                            'depends_on_test_case_id': dep.depends_on_test_case_id,
                            'depends_on_test_case_name': dep.depends_on.name if dep.depends_on else None,
                            'condition': condition
                        })
                    elif dep.dependency_type == 'optional':
                        optional_missing.append({
                            'dependency_id': dep.id,
                            'depends_on_test_case_id': dep.depends_on_test_case_id,
                            'depends_on_test_case_name': dep.depends_on.name if dep.depends_on else None,
                            'condition': condition
                        })
            
            return {
                'can_execute': can_execute,
                'blocked_by': blocked_by,
                'missing_required': missing_required,
                'optional_missing': optional_missing
            }
            
        except Exception as e:
            logger.error(f"의존성 조건 확인 오류: {str(e)}")
            return {
                'can_execute': False,
                'blocked_by': [],
                'missing_required': [],
                'optional_missing': [],
                'error': str(e)
            }
    
    def _calculate_pass_rate(self, test_case_id, recent_count=10):
        """테스트 케이스의 최근 통과율 계산"""
        try:
            results = TestResult.query.filter_by(
                test_case_id=test_case_id
            ).order_by(TestResult.executed_at.desc()).limit(recent_count).all()
            
            if not results:
                return 0.0
            
            passed = sum(1 for r in results if r.result == 'Pass')
            return (passed / len(results)) * 100.0
            
        except Exception as e:
            logger.error(f"통과율 계산 오류: {str(e)}")
            return 0.0
    
    def get_dependent_tests(self, test_case_id):
        """특정 테스트 케이스에 의존하는 테스트 케이스 목록 조회"""
        try:
            dependencies = TestDependency.query.filter_by(
                depends_on_test_case_id=test_case_id,
                enabled=True
            ).all()
            
            return [dep.to_dict() for dep in dependencies]
            
        except Exception as e:
            logger.error(f"의존 테스트 조회 오류: {str(e)}")
            return []
    
    def get_dependencies(self, test_case_id):
        """테스트 케이스가 의존하는 테스트 케이스 목록 조회"""
        try:
            dependencies = TestDependency.query.filter_by(
                test_case_id=test_case_id,
                enabled=True
            ).order_by(TestDependency.priority.asc()).all()
            
            return [dep.to_dict() for dep in dependencies]
            
        except Exception as e:
            logger.error(f"의존성 조회 오류: {str(e)}")
            return []

# 전역 의존성 서비스 인스턴스
dependency_service = DependencyService()

