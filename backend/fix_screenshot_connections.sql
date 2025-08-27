-- Screenshots 테이블의 test_result_id를 올바른 TestResult ID와 연결하도록 수정
USE test_management_alpha;

-- 현재 상황 확인
SELECT '현재 상황' as info;
SELECT s.id as screenshot_id, s.test_result_id, s.file_path, 
       tr.id as correct_test_result_id, tr.test_case_id
FROM Screenshots s
LEFT JOIN TestResults tr ON tr.test_case_id = 
    CASE 
        WHEN s.file_path LIKE '%2025-08-05 14_11_51_login%' THEN 84
        WHEN s.file_path LIKE '%2025-08-05 14_11_53_dashborad%' THEN 85
        WHEN s.file_path LIKE '%simple_test%' THEN 86
        WHEN s.file_path LIKE '%2025-08-05 14_14_03_login%' THEN 87
        WHEN s.file_path LIKE '%2025-08-05 14_11_49_main%' THEN 88
        WHEN s.file_path LIKE '%2025-07-15 17_09_23_main%' THEN 89
        WHEN s.file_path LIKE '%2025-08-05 14_14_02_main%' THEN 90
        WHEN s.file_path LIKE '%2025-08-05 14_14_05_dashborad%' THEN 91
        WHEN s.file_path LIKE '%2025-08-06 09_08_10_clm%' THEN 92
        WHEN s.file_path LIKE '%2025-08-06 09_08_55_dashborad%' THEN 93
        WHEN s.file_path LIKE '%2025-08-06 09_08_08_dashborad%' THEN 94
        WHEN s.file_path LIKE '%2025-08-06 09_08_53_login%' THEN 95
        WHEN s.file_path LIKE '%2025-08-06 09_08_58_clm%' THEN 96
        WHEN s.file_path LIKE '%2025-08-06 09_08_06_login%' THEN 97
        WHEN s.file_path LIKE '%2025-08-06 09_08_51_main%' THEN 98
        WHEN s.file_path LIKE '%2025-08-06 09_08_04_main%' THEN 99
    END
ORDER BY s.id;

-- Screenshots 테이블의 test_result_id를 올바른 값으로 업데이트
UPDATE Screenshots SET test_result_id = 21 WHERE file_path LIKE '%2025-08-06 09_08_04_main%';
UPDATE Screenshots SET test_result_id = 22 WHERE file_path LIKE '%2025-08-05 14_11_51_login%';
UPDATE Screenshots SET test_result_id = 23 WHERE file_path LIKE '%2025-08-05 14_11_53_dashborad%';
UPDATE Screenshots SET test_result_id = 24 WHERE file_path LIKE '%simple_test%';
UPDATE Screenshots SET test_result_id = 25 WHERE file_path LIKE '%2025-08-05 14_14_03_login%';
UPDATE Screenshots SET test_result_id = 26 WHERE file_path LIKE '%2025-08-05 14_11_49_main%';
UPDATE Screenshots SET test_result_id = 27 WHERE file_path LIKE '%2025-07-15 17_09_23_main%';
UPDATE Screenshots SET test_result_id = 28 WHERE file_path LIKE '%2025-08-05 14_14_02_main%';
UPDATE Screenshots SET test_result_id = 29 WHERE file_path LIKE '%2025-08-05 14_14_05_dashborad%';
UPDATE Screenshots SET test_result_id = 30 WHERE file_path LIKE '%2025-08-06 09_08_10_clm%';
UPDATE Screenshots SET test_result_id = 31 WHERE file_path LIKE '%2025-08-06 09_08_55_dashborad%';
UPDATE Screenshots SET test_result_id = 32 WHERE file_path LIKE '%2025-08-06 09_08_08_dashborad%';
UPDATE Screenshots SET test_result_id = 33 WHERE file_path LIKE '%2025-08-06 09_08_53_login%';
UPDATE Screenshots SET test_result_id = 34 WHERE file_path LIKE '%2025-08-06 09_08_58_clm%';
UPDATE Screenshots SET test_result_id = 35 WHERE file_path LIKE '%2025-08-06 09_08_06_login%';
UPDATE Screenshots SET test_result_id = 36 WHERE file_path LIKE '%2025-08-06 09_08_51_main%';

-- 수정 후 결과 확인
SELECT '수정 후 결과' as info;
SELECT s.id as screenshot_id, s.test_result_id, s.file_path, 
       tr.test_case_id, tc.name as test_case_name
FROM Screenshots s
JOIN TestResults tr ON s.test_result_id = tr.id
JOIN TestCases tc ON tr.test_case_id = tc.id
ORDER BY s.id;

-- 최종 연결 상태 확인
SELECT '최종 연결 상태' as info;
SELECT 
    tc.id as test_case_id,
    tc.name as test_case_name,
    tr.id as test_result_id,
    s.id as screenshot_id,
    s.file_path
FROM TestCases tc
JOIN TestResults tr ON tc.id = tr.test_case_id
LEFT JOIN Screenshots s ON tr.id = s.test_result_id
WHERE tc.id >= 84
ORDER BY tc.id;
