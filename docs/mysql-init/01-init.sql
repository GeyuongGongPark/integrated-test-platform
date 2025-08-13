-- MySQL 데이터베이스 초기화 스크립트
-- 컨테이너가 처음 실행될 때 자동으로 실행됩니다.

-- 데이터베이스 생성 (이미 존재하는 경우 무시)
CREATE DATABASE IF NOT EXISTS test_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- test_management 데이터베이스 사용
USE test_management;

-- 기본 사용자 생성 및 권한 설정
CREATE USER IF NOT EXISTS 'testuser'@'%' IDENTIFIED BY '1q2w#E$R';
CREATE USER IF NOT EXISTS 'testuser'@'localhost' IDENTIFIED BY '1q2w#E$R';
GRANT ALL PRIVILEGES ON *.* TO 'testuser'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'testuser'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- 테이블 생성은 Flask-Migrate가 처리하므로 여기서는 생성하지 않음
-- 필요한 경우 여기에 추가 테이블을 생성할 수 있습니다
