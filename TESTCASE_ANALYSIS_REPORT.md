# 테스트 케이스 고급 기능 및 성능 개선 분석 보고서

## 📋 개요
테스트 케이스 관련 고급 기능 추가 및 성능 개선 작업에 대한 코드 분석 및 DB 구조 변경 필요성 검토 결과입니다.

---

## ✅ 구현된 고급 기능

### 1. 테스트 케이스 히스토리 추적
- **위치**: `backend/utils/history_tracker.py`, `backend/models.py` (TestCaseHistory 모델)
- **기능**:
  - 테스트 케이스 생성/수정/삭제 이력 추적
  - 필드별 변경 이력 기록
  - 사용자별 변경 이력 조회
- **API 엔드포인트**: `GET /testcases/<id>/history`

### 2. 테스트 케이스 템플릿 기능
- **위치**: `backend/models.py` (TestCaseTemplate 모델)
- **기능**:
  - 템플릿 생성 및 관리
  - 템플릿을 테스트 케이스로 적용
  - 템플릿 검색 및 필터링
  - 사용 횟수 추적
- **API 엔드포인트**:
  - `GET /templates` - 템플릿 목록 조회
  - `POST /templates` - 템플릿 생성
  - `POST /templates/<id>/apply` - 템플릿 적용

### 3. 테스트 계획 기능
- **위치**: `backend/models.py` (TestPlan, TestPlanTestCase 모델)
- **기능**:
  - 테스트 계획 생성 및 관리
  - 테스트 케이스를 계획에 추가
  - 실행 순서 및 예상 소요 시간 관리
  - 담당자 할당
- **API 엔드포인트**:
  - `GET /test-plans` - 계획 목록 조회
  - `POST /test-plans` - 계획 생성
  - `POST /test-plans/<id>/test-cases` - 테스트 케이스 추가
  - `GET /test-plans/<id>` - 계획 상세 조회

### 4. 대시보드 요약 자동 업데이트
- **위치**: `backend/routes/testcases.py` (update_dashboard_summary_for_environment 함수)
- **기능**:
  - 테스트 케이스 상태 변경 시 자동 업데이트
  - 환경별 통계 자동 계산
  - 통과율 자동 계산

### 5. 자동화 스크립트 추천
- **위치**: `backend/routes/testcases.py` (suggest_automation_scripts 함수)
- **기능**:
  - 카테고리 기반 자동화 스크립트 추천
  - 미연결 테스트 케이스 식별

---

## 🚀 성능 개선 사항

### 1. N+1 쿼리 문제 해결
**위치**: `backend/routes/testcases.py`

#### 개선 전:
```python
# 각 테스트 케이스마다 creator, assignee 조회 쿼리 발생
testcases = TestCase.query.all()
```

#### 개선 후:
```python
# joinedload를 사용하여 한 번에 로드
tc = TestCase.query.options(
    joinedload(TestCase.creator),
    joinedload(TestCase.assignee)
).get_or_404(id)
```

**영향**: 테스트 케이스 조회 시 쿼리 수 대폭 감소

### 2. Bulk Delete 최적화
**위치**: `backend/routes/testcases.py` (bulk_delete_testcases 함수)

#### 개선 사항:
- IN 쿼리를 사용한 일괄 삭제
- synchronize_session=False로 성능 향상
- 연관 데이터(스크린샷, 테스트 결과) 일괄 삭제

```python
# 스크린샷 일괄 삭제
test_result_ids = db.session.query(TestResult.id).filter(
    TestResult.test_case_id.in_(testcase_ids_list)
).subquery()
Screenshot.query.filter(Screenshot.test_result_id.in_(test_result_ids)).delete(synchronize_session=False)
```

### 3. 스크린샷 조회 최적화
**위치**: `backend/routes/testcases.py` (get_testcase, get_testcase_screenshots)

#### 개선 사항:
- test_result_id 목록을 한 번에 가져와서 IN 쿼리로 스크린샷 조회
- N+1 쿼리 문제 해결

```python
test_results = TestResult.query.filter_by(test_case_id=id).all()
if test_results:
    result_ids = [result.id for result in test_results]
    screenshots = Screenshot.query.filter(Screenshot.test_result_id.in_(result_ids)).all()
```

### 4. 페이징 처리
**위치**: `backend/services/testcase_service.py`

- 페이징 지원으로 대량 데이터 조회 시 성능 향상
- per_page 최대값 제한 (100개)

---

## ⚠️ DB 구조 변경 필요 사항

### 1. **필수: 새 테이블 생성 필요**

#### 1.1 test_case_history 테이블
**현재 상태**: 모델 정의만 존재, 마이그레이션 없음

**필요한 스키마**:
```sql
CREATE TABLE `test_case_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_case_id` int NOT NULL,
  `field_name` varchar(100) NOT NULL,
  `old_value` text,
  `new_value` text,
  `changed_by` int NOT NULL,
  `changed_at` datetime NOT NULL,
  `change_type` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `test_case_id` (`test_case_id`),
  KEY `changed_by` (`changed_by`),
  CONSTRAINT `test_case_history_ibfk_1` FOREIGN KEY (`test_case_id`) REFERENCES `TestCases` (`id`),
  CONSTRAINT `test_case_history_ibfk_2` FOREIGN KEY (`changed_by`) REFERENCES `Users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

#### 1.2 test_case_templates 테이블
**현재 상태**: 모델 정의만 존재, 마이그레이션 없음

**필요한 스키마**:
```sql
CREATE TABLE `test_case_templates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` text,
  `main_category` varchar(100),
  `sub_category` varchar(100),
  `detail_category` varchar(100),
  `pre_condition` text,
  `expected_result` text,
  `test_steps` text,
  `automation_code_path` varchar(500),
  `automation_code_type` varchar(50) DEFAULT 'playwright',
  `tags` text,
  `created_by` int NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `is_public` boolean DEFAULT FALSE,
  `usage_count` int DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `test_case_templates_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `Users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

#### 1.3 test_plans 테이블
**현재 상태**: 모델 정의만 존재, 마이그레이션 없음

**필요한 스키마**:
```sql
CREATE TABLE `test_plans` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` text,
  `version` varchar(50),
  `environment` varchar(50),
  `start_date` date,
  `end_date` date,
  `status` varchar(50) DEFAULT 'draft',
  `priority` varchar(20) DEFAULT 'medium',
  `created_by` int NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `test_plans_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `Users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

#### 1.4 test_plan_test_cases 테이블
**현재 상태**: 모델 정의만 존재, 마이그레이션 없음

**필요한 스키마**:
```sql
CREATE TABLE `test_plan_test_cases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_plan_id` int NOT NULL,
  `test_case_id` int NOT NULL,
  `execution_order` int DEFAULT 0,
  `estimated_duration` int,
  `assigned_to` int,
  `notes` text,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `test_plan_id` (`test_plan_id`),
  KEY `test_case_id` (`test_case_id`),
  KEY `assigned_to` (`assigned_to`),
  CONSTRAINT `test_plan_test_cases_ibfk_1` FOREIGN KEY (`test_plan_id`) REFERENCES `test_plans` (`id`),
  CONSTRAINT `test_plan_test_cases_ibfk_2` FOREIGN KEY (`test_case_id`) REFERENCES `TestCases` (`id`),
  CONSTRAINT `test_plan_test_cases_ibfk_3` FOREIGN KEY (`assigned_to`) REFERENCES `Users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

### 2. **중요: TestResult 테이블 필드 추가/수정**

#### 2.1 모델에 없는 필드 추가 (DB에는 이미 존재)
**위치**: `backend/models.py` (TestResult 모델)

**현재 DB 스키마** (local_backup.sql 기준):
- `automation_test_id` int DEFAULT NULL ✅ (DB에 존재)
- `performance_test_id` int DEFAULT NULL ✅ (DB에 존재)

**조치 필요**: 모델에 필드 추가 필요

```python
# TestResult 모델에 추가 필요
automation_test_id = db.Column(db.Integer, db.ForeignKey('AutomationTests.id'), nullable=True)
performance_test_id = db.Column(db.Integer, db.ForeignKey('PerformanceTests.id'), nullable=True)
```

#### 2.2 코드에서 사용하지만 DB에 없는 필드
**위치**: `backend/routes/testcases.py` (execute_automation_code 함수)

**문제점**:
- `execution_duration`: 코드에서 사용하지만 DB에 없음
- `error_message`: 코드에서 사용하지만 DB에 없음
- `screenshot`: 코드에서 사용하지만 DB에 없음 (Screenshot 테이블 사용)

**조치 필요**:
1. **옵션 1**: TestResult 테이블에 필드 추가
   ```sql
   ALTER TABLE `TestResults` 
   ADD COLUMN `execution_duration` float DEFAULT NULL,
   ADD COLUMN `error_message` text;
   ```

2. **옵션 2**: 코드 수정하여 기존 필드 사용
   - `execution_duration` → `execution_time` (이미 존재)
   - `error_message` → `notes` 필드에 포함 또는 별도 처리
   - `screenshot` → Screenshot 테이블 사용 (현재 구조 유지)

**권장**: 옵션 1 (명확성과 확장성)

### 3. **선택: 인덱스 추가**

#### 3.1 TestCases 테이블 인덱스
```sql
-- 환경별 조회 성능 향상
CREATE INDEX `idx_testcases_environment` ON `TestCases` (`environment`);
CREATE INDEX `idx_testcases_result_status` ON `TestCases` (`result_status`);
CREATE INDEX `idx_testcases_folder_id` ON `TestCases` (`folder_id`);
CREATE INDEX `idx_testcases_creator_id` ON `TestCases` (`creator_id`);
CREATE INDEX `idx_testcases_assignee_id` ON `TestCases` (`assignee_id`);
```

#### 3.2 TestResults 테이블 인덱스
```sql
-- 실행 이력 조회 성능 향상
CREATE INDEX `idx_testresults_executed_at` ON `TestResults` (`executed_at`);
CREATE INDEX `idx_testresults_environment` ON `TestResults` (`environment`);
CREATE INDEX `idx_testresults_result` ON `TestResults` (`result`);
```

#### 3.3 TestCaseHistory 테이블 인덱스
```sql
-- 히스토리 조회 성능 향상
CREATE INDEX `idx_testcase_history_test_case_id` ON `test_case_history` (`test_case_id`);
CREATE INDEX `idx_testcase_history_changed_at` ON `test_case_history` (`changed_at`);
CREATE INDEX `idx_testcase_history_changed_by` ON `test_case_history` (`changed_by`);
```

---

## 🔍 코드 개선 제안

### 1. TestResult 모델 업데이트 필요
**파일**: `backend/models.py`

**현재 코드**:
```python
class TestResult(db.Model):
    __tablename__ = 'TestResults'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=True)
    result = db.Column(db.String(20))
    execution_time = db.Column(db.Float)
    environment = db.Column(db.String(50))
    executed_by = db.Column(db.String(100))
    executed_at = db.Column(db.DateTime, default=get_kst_now)
    notes = db.Column(db.Text)
```

**수정 필요**:
```python
class TestResult(db.Model):
    __tablename__ = 'TestResults'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=True)
    result = db.Column(db.String(20))
    execution_time = db.Column(db.Float)  # 기존 필드
    execution_duration = db.Column(db.Float)  # 새 필드 추가 (또는 execution_time과 통합)
    environment = db.Column(db.String(50))
    executed_by = db.Column(db.String(100))
    executed_at = db.Column(db.DateTime, default=get_kst_now)
    notes = db.Column(db.Text)
    error_message = db.Column(db.Text)  # 새 필드 추가
    automation_test_id = db.Column(db.Integer, db.ForeignKey('AutomationTests.id'), nullable=True)  # DB에 존재
    performance_test_id = db.Column(db.Integer, db.ForeignKey('PerformanceTests.id'), nullable=True)  # DB에 존재
```

### 2. 히스토리 추적 함수 import 추가
**파일**: `backend/routes/testcases.py`

**현재 상태**: `get_test_case_history` 함수 사용하지만 import 없음

**수정 필요**:
```python
from utils.history_tracker import get_test_case_history, track_test_case_creation, track_test_case_change
```

### 3. 사용자 ID 하드코딩 제거
**위치**: `backend/routes/testcases.py`

**문제점**:
- `track_test_case_creation(tc.id, data, 1)` - 하드코딩된 사용자 ID
- `track_test_case_change(id, 'automation_code_path', None, script_path, 1)` - 하드코딩된 사용자 ID

**수정 필요**:
```python
# request.user.id 사용 (이미 user_required 데코레이터 사용 중)
track_test_case_creation(tc.id, data, request.user.id)
track_test_case_change(id, 'automation_code_path', None, script_path, request.user.id)
```

---

## 📊 마이그레이션 우선순위

### 🔴 높음 (즉시 필요)
1. **test_case_history 테이블 생성** - 히스토리 기능이 이미 사용 중
2. **TestResult 모델 필드 추가** - automation_test_id, performance_test_id (DB에 존재하지만 모델에 없음)

### 🟡 중간 (기능 활성화 전 필요)
3. **test_case_templates 테이블 생성** - 템플릿 기능 사용 시 필요
4. **test_plans 테이블 생성** - 테스트 계획 기능 사용 시 필요
5. **test_plan_test_cases 테이블 생성** - 테스트 계획 기능 사용 시 필요

### 🟢 낮음 (성능 최적화)
6. **TestResult 테이블 필드 추가** - execution_duration, error_message (코드에서 사용 중이지만 동작은 함)
7. **인덱스 추가** - 데이터량이 많아질 때 성능 향상

---

## 🎯 권장 조치 사항

### 즉시 조치
1. ✅ 새 테이블 생성 마이그레이션 파일 작성
2. ✅ TestResult 모델 업데이트 (automation_test_id, performance_test_id 추가)
3. ✅ 히스토리 추적 함수 import 추가
4. ✅ 사용자 ID 하드코딩 제거

### 단기 조치 (1주일 내)
5. ✅ TestResult 테이블에 execution_duration, error_message 필드 추가
6. ✅ 인덱스 추가 마이그레이션 작성

### 중기 조치 (1개월 내)
7. ✅ 코드 리팩토링 (execution_time vs execution_duration 통합 검토)
8. ✅ 성능 테스트 및 모니터링

---

## 📝 마이그레이션 파일 생성 가이드

새 마이그레이션 파일을 생성하려면:

```bash
cd backend
flask db revision -m "add_test_case_advanced_features"
```

생성된 파일에 위의 SQL 스키마를 추가하거나, Alembic 명령어로 작성합니다.

---

## ✅ 검증 체크리스트

- [ ] test_case_history 테이블 생성 및 마이그레이션
- [ ] test_case_templates 테이블 생성 및 마이그레이션
- [ ] test_plans 테이블 생성 및 마이그레이션
- [ ] test_plan_test_cases 테이블 생성 및 마이그레이션
- [ ] TestResult 모델에 automation_test_id, performance_test_id 추가
- [ ] TestResult 테이블에 execution_duration, error_message 필드 추가 (선택)
- [ ] 히스토리 추적 함수 import 추가
- [ ] 사용자 ID 하드코딩 제거
- [ ] 인덱스 추가
- [ ] 마이그레이션 테스트

---

**작성일**: 2025-01-XX
**분석 대상**: 테스트 케이스 관련 고급 기능 및 성능 개선 코드

