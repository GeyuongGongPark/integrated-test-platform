-- Alpha DB에 스크린샷 데이터 삽입 (기존 ID와 중복 방지)
USE test_management_alpha;

-- 테스트 케이스 삽입 (ID 84부터 시작)
INSERT INTO TestCases (id, name, description, test_type, script_path, main_category, sub_category, environment, created_at, updated_at, priority, status, result_status) VALUES
(84, '2025-08-05 14_11_51_login', '자동 생성된 테스트 케이스 - 2025-08-05 14_11_51_login.png', 'performance', 'performance/screenshots/2025-08-05 14_11_51_login.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(85, '2025-08-05 14_11_53_dashborad', '자동 생성된 테스트 케이스 - 2025-08-05 14_11_53_dashborad.png', 'performance', 'performance/screenshots/2025-08-05 14_11_53_dashborad.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(86, 'simple_test', '자동 생성된 테스트 케이스 - simple_test.png', 'performance', 'performance/screenshots/simple_test.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(87, '2025-08-05 14_14_03_login', '자동 생성된 테스트 케이스 - 2025-08-05 14_14_03_login.png', 'performance', 'performance/screenshots/2025-08-05 14_14_03_login.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(88, '2025-08-05 14_11_49_main', '자동 생성된 테스트 케이스 - 2025-08-05 14_11_49_main.png', 'performance', 'performance/screenshots/2025-08-05 14_11_49_main.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(89, '2025-07-15 17_09_23_main', '자동 생성된 테스트 케이스 - 2025-07-15 17_09_23_main.png', 'performance', 'performance/screenshots/2025-07-15 17_09_23_main.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(90, '2025-08-05 14_14_02_main', '자동 생성된 테스트 케이스 - 2025-08-05 14_14_02_main.png', 'performance', 'performance/screenshots/2025-08-05 14_14_02_main.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(91, '2025-08-05 14_14_05_dashborad', '자동 생성된 테스트 케이스 - 2025-08-05 14_14_05_dashborad.png', 'performance', 'performance/screenshots/2025-08-05 14_14_05_dashborad.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(92, '2025-08-06 09_08_10_clm', '자동 생성된 테스트 케이스 - 2025-08-06 09_08_10_clm.png', 'performance', 'performance/clm/nomerl/screenshots/2025-08-06 09_08_10_clm.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(93, '2025-08-06 09_08_55_dashborad', '자동 생성된 테스트 케이스 - 2025-08-06 09_08_55_dashborad.png', 'performance', 'performance/clm/nomerl/screenshots/2025-08-06 09_08_55_dashborad.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(94, '2025-08-06 09_08_08_dashborad', '자동 생성된 테스트 케이스 - 2025-08-06 09_08_08_dashborad.png', 'performance', 'performance/clm/nomerl/screenshots/2025-08-06 09_08_08_dashborad.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(95, '2025-08-06 09_08_53_login', '자동 생성된 테스트 케이스 - 2025-08-06 09_08_53_login.png', 'performance', 'performance/clm/nomerl/screenshots/2025-08-06 09_08_53_login.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(96, '2025-08-06 09_08_58_clm', '자동 생성된 테스트 케이스 - 2025-08-06 09_08_58_clm.png', 'performance', 'performance/clm/nomerl/screenshots/2025-08-06 09_08_58_clm.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(97, '2025-08-06 09_08_06_login', '자동 생성된 테스트 케이스 - 2025-08-06 09_08_06_login.png', 'performance', 'performance/clm/nomerl/screenshots/2025-08-06 09_08_06_login.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(98, '2025-08-06 09_08_51_main', '자동 생성된 테스트 케이스 - 2025-08-06 09_08_51_main.png', 'performance', 'performance/clm/nomerl/screenshots/2025-08-06 09_08_51_main.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending'),
(99, '2025-08-06 09_08_04_main', '자동 생성된 테스트 케이스 - 2025-08-06 09_08_04_main.png', 'performance', 'performance/clm/nomerl/screenshots/2025-08-06 09_08_04_main.png', 'performance', 'screenshot_migration', 'alpha', NOW(), NOW(), 'medium', 'active', 'pending');

-- 테스트 결과 삽입
INSERT INTO TestResults (test_case_id, result, execution_time, environment, executed_by, executed_at, notes) VALUES
(84, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(85, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(86, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(87, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(88, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(89, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(90, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(91, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(92, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(93, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(94, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(95, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(96, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(97, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(98, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과'),
(99, 'Pass', 0.0, 'alpha', 'migration_script', NOW(), '스크린샷 마이그레이션으로 생성된 테스트 결과');

-- 스크린샷 삽입
INSERT INTO Screenshots (test_result_id, file_path, created_at) VALUES
(LAST_INSERT_ID()-15, 'performance/screenshots/2025-08-05 14_11_51_login.png', NOW()),
(LAST_INSERT_ID()-14, 'performance/screenshots/2025-08-05 14_11_53_dashborad.png', NOW()),
(LAST_INSERT_ID()-13, 'performance/screenshots/simple_test.png', NOW()),
(LAST_INSERT_ID()-12, 'performance/screenshots/2025-08-05 14_14_03_login.png', NOW()),
(LAST_INSERT_ID()-11, 'performance/screenshots/2025-08-05 14_11_49_main.png', NOW()),
(LAST_INSERT_ID()-10, 'performance/screenshots/2025-07-15 17_09_23_main.png', NOW()),
(LAST_INSERT_ID()-9, 'performance/screenshots/2025-08-05 14_14_02_main.png', NOW()),
(LAST_INSERT_ID()-8, 'performance/screenshots/2025-08-05 14_14_05_dashborad.png', NOW()),
(LAST_INSERT_ID()-7, 'performance/clm/nomerl/screenshots/2025-08-06 09_08_10_clm.png', NOW()),
(LAST_INSERT_ID()-6, 'performance/clm/nomerl/screenshots/2025-08-06 09_08_55_dashborad.png', NOW()),
(LAST_INSERT_ID()-5, 'performance/clm/nomerl/screenshots/2025-08-06 09_08_08_dashborad.png', NOW()),
(LAST_INSERT_ID()-4, 'performance/clm/nomerl/screenshots/2025-08-06 09_08_53_login.png', NOW()),
(LAST_INSERT_ID()-3, 'performance/clm/nomerl/screenshots/2025-08-06 09_08_58_clm.png', NOW()),
(LAST_INSERT_ID()-2, 'performance/clm/nomerl/screenshots/2025-08-06 09_08_06_login.png', NOW()),
(LAST_INSERT_ID()-1, 'performance/clm/nomerl/screenshots/2025-08-06 09_08_51_main.png', NOW()),
(LAST_INSERT_ID(), 'performance/clm/nomerl/screenshots/2025-08-06 09_08_04_main.png', NOW());

-- 결과 확인
SELECT 'TestCases' as table_name, COUNT(*) as count FROM TestCases
UNION ALL
SELECT 'TestResults' as table_name, COUNT(*) as count FROM TestResults
UNION ALL
SELECT 'Screenshots' as table_name, COUNT(*) as count FROM Screenshots;
