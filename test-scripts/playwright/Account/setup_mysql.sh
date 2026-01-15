#!/bin/bash

# MySQL 데이터베이스 생성 스크립트
# 사용법: bash Account/setup_mysql.sh

echo "=== MySQL 데이터베이스 설정 ==="
echo ""

# MySQL 서버 상태 확인
if ! pgrep -x "mysqld" > /dev/null; then
    echo "⚠️  MySQL 서버가 실행되지 않았습니다."
    echo "MySQL 서버를 시작하시겠습니까? (y/n)"
    read -r answer
    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        echo "MySQL 서버 시작 중..."
        brew services start mysql
        sleep 3
    else
        echo "MySQL 서버를 먼저 시작해주세요: brew services start mysql"
        exit 1
    fi
fi

echo "✅ MySQL 서버 실행 중"
echo ""

# MySQL 접속 정보 입력
echo "MySQL 접속 정보를 입력하세요:"
read -p "사용자명 (기본값: root): " DB_USER
DB_USER=${DB_USER:-root}

read -sp "비밀번호: " DB_PASSWORD
echo ""

read -p "호스트 (기본값: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "포트 (기본값: 3306): " DB_PORT
DB_PORT=${DB_PORT:-3306}

DB_NAME="lfbz_accounts"

echo ""
echo "데이터베이스 생성 중: $DB_NAME"

# 데이터베이스 생성
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" << EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE $DB_NAME;

SHOW DATABASES LIKE '$DB_NAME';
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 데이터베이스 '$DB_NAME' 생성 완료!"
    echo ""
    echo "다음 단계:"
    echo "1. .env 파일에 다음 정보를 추가하세요:"
    echo "   DB_HOST=$DB_HOST"
    echo "   DB_PORT=$DB_PORT"
    echo "   DB_USER=$DB_USER"
    echo "   DB_PASSWORD=$DB_PASSWORD"
    echo "   DB_NAME=$DB_NAME"
    echo ""
    echo "2. 마이그레이션 실행: npm run migrate:accounts"
else
    echo ""
    echo "❌ 데이터베이스 생성 실패"
    echo "MySQL 접속 정보를 확인해주세요."
    exit 1
fi

