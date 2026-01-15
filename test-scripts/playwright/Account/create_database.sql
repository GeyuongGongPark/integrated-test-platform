-- MySQL 데이터베이스 생성 스크립트
-- 실행 방법: mysql -u root -p < Account/create_database.sql

-- 데이터베이스 생성 (이미 존재하면 무시)
CREATE DATABASE IF NOT EXISTS lfbz_accounts 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 데이터베이스 선택
USE lfbz_accounts;

-- 데이터베이스 생성 확인
SHOW DATABASES LIKE 'lfbz_accounts';

