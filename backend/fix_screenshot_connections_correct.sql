-- testcase 이름과 스크린샷 파일명이 일치하도록 올바르게 연결
USE test_management_alpha;

-- 현재 잘못된 연결 상태 확인
SELECT '현재 잘못된 연결 상태' as info;
SELECT tc.id, tc.name, tr.id as test_result_id, s.id as screenshot_id, s.file_path 
FROM TestCases tc 
JOIN TestResults tr ON tc.id = tr.test_case_id 
LEFT JOIN Screenshots s ON tr.id = s.test_result_id 
WHERE tc.id >= 84 
ORDER BY tc.id;

-- 올바른 연결을 위한 UPDATE 쿼리
-- testcase 84: 2025-08-05 14_11_51_login -> 2025-08-05 14_11_51_login.png
UPDATE Screenshots SET test_result_id = 21 WHERE file_path LIKE '%2025-08-05 14_11_51_login.png';

-- testcase 85: 2025-08-05 14_11_53_dashborad -> 2025-08-05 14_11_53_dashborad.png  
UPDATE Screenshots SET test_result_id = 22 WHERE file_path LIKE '%2025-08-05 14_11_53_dashborad.png';

-- testcase 86: simple_test -> simple_test.png
UPDATE Screenshots SET test_result_id = 23 WHERE file_path LIKE '%simple_test.png';

-- testcase 87: 2025-08-05 14_14_03_login -> 2025-08-05 14_14_03_login.png
UPDATE Screenshots SET test_result_id = 24 WHERE file_path LIKE '%2025-08-05 14_14_03_login.png';

-- testcase 88: 2025-08-05 14_11_49_main -> 2025-08-05 14_11_49_main.png
UPDATE Screenshots SET test_result_id = 25 WHERE file_path LIKE '%2025-08-05 14_11_49_main.png';

-- testcase 89: 2025-07-15 17_09_23_main -> 2025-07-15 17_09_23_main.png
UPDATE Screenshots SET test_result_id = 26 WHERE file_path LIKE '%2025-07-15 17_09_23_main.png';

-- testcase 90: 2025-08-05 14_14_02_main -> 2025-08-05 14_14_02_main.png
UPDATE Screenshots SET test_result_id = 27 WHERE file_path LIKE '%2025-08-05 14_14_02_main.png';

-- testcase 91: 2025-08-05 14_14_05_dashborad -> 2025-08-05 14_14_05_dashborad.png
UPDATE Screenshots SET test_result_id = 28 WHERE file_path LIKE '%2025-08-05 14_14_05_dashborad.png';

-- testcase 92: 2025-08-06 09_08_10_clm -> 2025-08-06 09_08_10_clm.png
UPDATE Screenshots SET test_result_id = 29 WHERE file_path LIKE '%2025-08-06 09_08_10_clm.png';

-- testcase 93: 2025-08-06 09_08_55_dashborad -> 2025-08-06 09_08_55_dashborad.png
UPDATE Screenshots SET test_result_id = 30 WHERE file_path LIKE '%2025-08-06 09_08_55_dashborad.png';

-- testcase 94: 2025-08-06 09_08_08_dashborad -> 2025-08-06 09_08_08_dashborad.png
UPDATE Screenshots SET test_result_id = 31 WHERE file_path LIKE '%2025-08-06 09_08_08_dashborad.png';

-- testcase 95: 2025-08-06 09_08_53_login -> 2025-08-06 09_08_53_login.png
UPDATE Screenshots SET test_result_id = 32 WHERE file_path LIKE '%2025-08-06 09_08_53_login.png';

-- testcase 96: 2025-08-06 09_08_58_clm -> 2025-08-06 09_08_58_clm.png
UPDATE Screenshots SET test_result_id = 33 WHERE file_path LIKE '%2025-08-06 09_08_58_clm.png';

-- testcase 97: 2025-08-06 09_08_06_login -> 2025-08-06 09_08_06_login.png
UPDATE Screenshots SET test_result_id = 34 WHERE file_path LIKE '%2025-08-06 09_08_06_login.png';

-- testcase 98: 2025-08-06 09_08_51_main -> 2025-08-06 09_08_51_main.png
UPDATE Screenshots SET test_result_id = 35 WHERE file_path LIKE '%2025-08-06 09_08_51_main.png';

-- testcase 99: 2025-08-06 09_08_04_main -> 2025-08-06 09_08_04_main.png
UPDATE Screenshots SET test_result_id = 36 WHERE file_path LIKE '%2025-08-06 09_08_04_main.png';

-- 수정 후 올바른 연결 상태 확인
SELECT '수정 후 올바른 연결 상태' as info;
SELECT tc.id, tc.name, tr.id as test_result_id, s.id as screenshot_id, s.file_path 
FROM TestCases tc 
JOIN TestResults tr ON tc.id = tr.test_case_id 
LEFT JOIN Screenshots s ON tr.id = s.test_result_id 
WHERE tc.id >= 84 
ORDER BY tc.id;

-- testcase 99번의 스크린샷 연결 상태 상세 확인
SELECT 'Testcase 99번 상세 확인' as info;
SELECT tc.id, tc.name, tr.id as test_result_id, s.id as screenshot_id, s.file_path 
FROM TestCases tc 
JOIN TestResults tr ON tc.id = tr.test_case_id 
LEFT JOIN Screenshots s ON tr.id = s.test_result_id 
WHERE tc.id = 99;
