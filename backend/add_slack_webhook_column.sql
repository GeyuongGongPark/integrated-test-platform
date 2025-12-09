-- NotificationSettings 테이블에 slack_webhook_url 컬럼 추가
-- 이 스크립트는 직접 MySQL에 실행할 수 있습니다.

-- 컬럼이 이미 존재하는지 확인하고 추가
ALTER TABLE NotificationSettings 
ADD COLUMN IF NOT EXISTS slack_webhook_url VARCHAR(500) NULL 
COMMENT '사용자별 슬랙 웹훅 URL';

-- MySQL 5.7 이하 버전에서는 IF NOT EXISTS를 지원하지 않으므로, 
-- 아래 방법을 사용하세요:

-- 방법 1: 직접 실행 (컬럼이 없을 때만)
-- ALTER TABLE NotificationSettings ADD COLUMN slack_webhook_url VARCHAR(500) NULL;

-- 방법 2: 프로시저 사용 (안전하게)
-- DELIMITER $$
-- CREATE PROCEDURE AddSlackWebhookColumn()
-- BEGIN
--     IF NOT EXISTS (
--         SELECT * FROM information_schema.COLUMNS 
--         WHERE TABLE_SCHEMA = DATABASE() 
--         AND TABLE_NAME = 'NotificationSettings' 
--         AND COLUMN_NAME = 'slack_webhook_url'
--     ) THEN
--         ALTER TABLE NotificationSettings ADD COLUMN slack_webhook_url VARCHAR(500) NULL;
--     END IF;
-- END$$
-- DELIMITER ;
-- CALL AddSlackWebhookColumn();
-- DROP PROCEDURE AddSlackWebhookColumn;

