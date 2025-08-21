#!/bin/bash

echo "🚀 Ubuntu MySQL 서버 설정 시작..."

# MySQL 서비스 시작
echo "📦 MySQL 서비스 시작 중..."
service mysql start

# MySQL 보안 설정
echo "🔒 MySQL 보안 설정 중..."
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '1q2w#E$R';"
mysql -e "DELETE FROM mysql.user WHERE User='';"
mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -e "DROP DATABASE IF EXISTS test;"
mysql -e "FLUSH PRIVILEGES;"

# 데이터베이스 생성
echo "🗄️ 데이터베이스 생성 중..."
mysql -e "CREATE DATABASE IF NOT EXISTS test_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Vercel용 사용자 생성
echo "👤 Vercel 사용자 생성 중..."
mysql -e "CREATE USER IF NOT EXISTS 'vercel_user'@'%' IDENTIFIED BY 'vercel_secure_pass_2025';"
mysql -e "GRANT ALL PRIVILEGES ON test_management.* TO 'vercel_user'@'%';"
mysql -e "FLUSH PRIVILEGES;"

# MySQL 설정 파일 수정 (외부 접근 허용)
echo "🌐 외부 접근 설정 중..."
sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf

# MySQL 재시작
echo "🔄 MySQL 재시작 중..."
service mysql restart

echo "✅ MySQL 설정 완료!"
echo "📊 데이터베이스: test_management"
echo "👤 사용자: vercel_user"
echo "🔑 비밀번호: vercel_secure_pass_2025"
echo "🌐 포트: 3306"
echo "🔗 외부 접근: 허용됨"
