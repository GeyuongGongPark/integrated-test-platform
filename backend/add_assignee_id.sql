-- TestCases 테이블에 assignee_id 컬럼 추가
-- 이 스크립트는 TestCases 테이블에 assignee_id 컬럼이 없는 경우에만 실행하세요.

USE test_management;

-- assignee_id 컬럼이 이미 존재하는지 확인
SELECT COUNT(*) 
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'test_management' 
AND TABLE_NAME = 'TestCases' 
AND COLUMN_NAME = 'assignee_id';

-- assignee_id 컬럼 추가 (존재하지 않는 경우)
ALTER TABLE TestCases 
ADD COLUMN assignee_id INT NULL;

-- 인덱스 추가
ALTER TABLE TestCases 
ADD INDEX idx_testcases_assignee_id (assignee_id);

-- 외래키 제약조건 추가 (Users 테이블이 존재하는 경우)
ALTER TABLE TestCases 
ADD CONSTRAINT fk_testcases_assignee 
FOREIGN KEY (assignee_id) REFERENCES Users(id);

-- 확인
DESCRIBE TestCases;

