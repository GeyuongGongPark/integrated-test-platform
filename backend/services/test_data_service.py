"""
테스트 데이터 관리 서비스
데이터 세트 생성, 마스킹, 버전 관리 등
"""
from models import db, TestDataSet, TestCaseDataMapping, TestCase
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
import json
import copy

logger = get_logger(__name__)

class TestDataService:
    """테스트 데이터 관리 서비스"""
    
    def create_data_set(self, name, data, environment='dev', description=None, 
                       data_type='json', masking_enabled=False, masking_rules=None,
                       tags=None, created_by=None):
        """
        테스트 데이터 세트 생성
        
        Args:
            name: 데이터 세트 이름
            data: 데이터 (dict 또는 JSON 문자열)
            environment: 환경
            description: 설명
            data_type: 데이터 타입
            masking_enabled: 마스킹 활성화 여부
            masking_rules: 마스킹 규칙 (dict)
            tags: 태그 (list)
            created_by: 생성자 ID
        
        Returns:
            TestDataSet: 생성된 데이터 세트
        """
        try:
            # 데이터를 JSON 문자열로 변환
            if isinstance(data, str):
                # 이미 JSON 문자열인지 확인
                try:
                    json.loads(data)
                    data_json = data
                except:
                    raise ValueError("잘못된 JSON 형식입니다")
            else:
                data_json = json.dumps(data)
            
            data_set = TestDataSet(
                name=name,
                description=description or '',
                data=data_json,
                data_type=data_type,
                environment=environment,
                version='1.0',
                masking_enabled=masking_enabled,
                masking_rules=json.dumps(masking_rules) if masking_rules else None,
                tags=json.dumps(tags) if tags else None,
                created_by=created_by
            )
            
            db.session.add(data_set)
            db.session.commit()
            
            logger.info(f"테스트 데이터 세트 생성 완료: {name} (ID: {data_set.id})")
            return data_set
            
        except Exception as e:
            logger.error(f"데이터 세트 생성 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def create_data_set_version(self, parent_id, data, version=None, created_by=None):
        """
        데이터 세트 버전 생성
        
        Args:
            parent_id: 부모 데이터 세트 ID
            data: 새 데이터
            version: 버전 번호 (없으면 자동 증가)
            created_by: 생성자 ID
        
        Returns:
            TestDataSet: 새 버전
        """
        try:
            parent = TestDataSet.query.get(parent_id)
            if not parent:
                raise ValueError(f"부모 데이터 세트를 찾을 수 없습니다: {parent_id}")
            
            # 버전 번호 계산
            if not version:
                # 같은 부모를 가진 최신 버전 찾기
                latest = TestDataSet.query.filter_by(
                    parent_version_id=parent_id
                ).order_by(TestDataSet.created_at.desc()).first()
                
                if latest:
                    # 버전 번호 증가
                    try:
                        current_version = float(latest.version)
                        version = str(current_version + 0.1)
                    except:
                        version = f"{latest.version}.1"
                else:
                    version = f"{parent.version}.1"
            
            # 데이터를 JSON 문자열로 변환
            if isinstance(data, str):
                data_json = data
            else:
                data_json = json.dumps(data)
            
            new_version = TestDataSet(
                name=parent.name,
                description=parent.description,
                data=data_json,
                data_type=parent.data_type,
                environment=parent.environment,
                version=version,
                parent_version_id=parent_id,
                masking_enabled=parent.masking_enabled,
                masking_rules=parent.masking_rules,
                tags=parent.tags,
                created_by=created_by or parent.created_by
            )
            
            db.session.add(new_version)
            db.session.commit()
            
            logger.info(f"데이터 세트 버전 생성 완료: {parent.name} v{version}")
            return new_version
            
        except Exception as e:
            logger.error(f"데이터 세트 버전 생성 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def get_data_for_test_case(self, test_case_id, environment=None):
        """
        테스트 케이스에 매핑된 데이터 세트 조회
        
        Args:
            test_case_id: 테스트 케이스 ID
            environment: 환경 (선택적)
        
        Returns:
            dict: 매핑된 데이터
        """
        try:
            # 활성화된 매핑 조회
            query = TestCaseDataMapping.query.filter_by(
                test_case_id=test_case_id,
                enabled=True
            ).join(
                TestDataSet, TestCaseDataMapping.data_set_id == TestDataSet.id
            )
            
            if environment:
                query = query.filter(TestDataSet.environment == environment)
            
            # 우선순위로 정렬
            mappings = query.order_by(TestCaseDataMapping.priority.asc()).all()
            
            if not mappings:
                return None
            
            # 가장 높은 우선순위의 데이터 세트 사용
            mapping = mappings[0]
            data_set = mapping.data_set
            
            # 데이터 가져오기 (마스킹 적용)
            if data_set.masking_enabled:
                data = data_set.get_masked_data()
            else:
                data = json.loads(data_set.data) if data_set.data else {}
            
            # 필드 매핑 적용
            if mapping.field_mapping:
                field_mapping = json.loads(mapping.field_mapping)
                mapped_data = self._apply_field_mapping(data, field_mapping)
            else:
                mapped_data = data
            
            # 사용 통계 업데이트
            data_set.usage_count += 1
            data_set.last_used_at = get_kst_now()
            db.session.commit()
            
            return mapped_data
            
        except Exception as e:
            logger.error(f"테스트 케이스 데이터 조회 오류: {str(e)}")
            return None
    
    def _apply_field_mapping(self, data, field_mapping):
        """필드 매핑 적용"""
        try:
            mapped = {}
            for target_field, source_path in field_mapping.items():
                # 점 표기법으로 중첩된 데이터 접근
                value = self._get_nested_value(data, source_path)
                mapped[target_field] = value
            return mapped
        except Exception as e:
            logger.error(f"필드 매핑 적용 오류: {str(e)}")
            return data
    
    def _get_nested_value(self, data, path):
        """중첩된 경로에서 값 가져오기"""
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def generate_dynamic_data(self, schema, count=1):
        """
        스키마를 기반으로 동적 테스트 데이터 생성
        
        Args:
            schema: 데이터 스키마 (dict)
            count: 생성할 데이터 개수
        
        Returns:
            list: 생성된 데이터 리스트
        """
        try:
            import random
            import string
            from datetime import datetime, timedelta
            
            generated_data = []
            
            for i in range(count):
                item = {}
                
                for field_name, field_schema in schema.items():
                    field_type = field_schema.get('type', 'string')
                    
                    if field_type == 'string':
                        if 'enum' in field_schema:
                            item[field_name] = random.choice(field_schema['enum'])
                        elif 'pattern' in field_schema:
                            # 간단한 패턴 매칭 (실제로는 더 복잡한 로직 필요)
                            item[field_name] = self._generate_from_pattern(field_schema['pattern'])
                        else:
                            length = field_schema.get('length', 10)
                            item[field_name] = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
                    
                    elif field_type == 'integer':
                        min_val = field_schema.get('minimum', 0)
                        max_val = field_schema.get('maximum', 100)
                        item[field_name] = random.randint(min_val, max_val)
                    
                    elif field_type == 'email':
                        item[field_name] = f"test{random.randint(1000, 9999)}@example.com"
                    
                    elif field_type == 'date':
                        days_ago = random.randint(0, 365)
                        item[field_name] = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                    
                    elif field_type == 'boolean':
                        item[field_name] = random.choice([True, False])
                    
                    else:
                        item[field_name] = None
                
                generated_data.append(item)
            
            return generated_data
            
        except Exception as e:
            logger.error(f"동적 데이터 생성 오류: {str(e)}")
            return []
    
    def _generate_from_pattern(self, pattern):
        """패턴에서 데이터 생성 (간단한 버전)"""
        import random
        import string
        
        # 간단한 패턴 처리
        if 'email' in pattern.lower():
            return f"test{random.randint(1000, 9999)}@example.com"
        elif 'phone' in pattern.lower():
            return f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        else:
            return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# 전역 테스트 데이터 서비스 인스턴스
test_data_service = TestDataService()

