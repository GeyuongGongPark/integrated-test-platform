#!/bin/bash

# .env 파일에 MySQL 설정을 추가하는 스크립트

ENV_FILE=".env"

echo "=== .env 파일에 MySQL 설정 추가 ==="
echo ""

# .env 파일 존재 확인
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  .env 파일이 없습니다. 새로 생성합니다."
    touch "$ENV_FILE"
fi

# MySQL 설정이 이미 있는지 확인
if grep -q "DB_HOST" "$ENV_FILE"; then
    echo "⚠️  MySQL 설정이 이미 존재합니다."
    echo "기존 설정을 확인하세요:"
    grep -E "DB_(HOST|PORT|USER|PASSWORD|NAME)" "$ENV_FILE" || echo "  (설정 없음)"
    echo ""
    read -p "기존 설정을 덮어쓰시겠습니까? (y/n): " answer
    if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
        echo "취소되었습니다."
        exit 0
    fi
    
    # 기존 MySQL 설정 제거
    sed -i.bak '/^DB_HOST=/d' "$ENV_FILE"
    sed -i.bak '/^DB_PORT=/d' "$ENV_FILE"
    sed -i.bak '/^DB_USER=/d' "$ENV_FILE"
    sed -i.bak '/^DB_PASSWORD=/d' "$ENV_FILE"
    sed -i.bak '/^DB_NAME=/d' "$ENV_FILE"
    rm -f "$ENV_FILE.bak"
fi

echo ""
echo "MySQL 연결 정보를 입력하세요:"
echo ""

read -p "호스트 (기본값: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "포트 (기본값: 3306): " DB_PORT
DB_PORT=${DB_PORT:-3306}

read -p "사용자명 (기본값: root): " DB_USER
DB_USER=${DB_USER:-root}

read -sp "비밀번호: " DB_PASSWORD
echo ""

read -p "데이터베이스명 (기본값: lfbz_accounts): " DB_NAME
DB_NAME=${DB_NAME:-lfbz_accounts}

# .env 파일에 추가
echo "" >> "$ENV_FILE"
echo "# MySQL 데이터베이스 연결 정보" >> "$ENV_FILE"
echo "DB_HOST=$DB_HOST" >> "$ENV_FILE"
echo "DB_PORT=$DB_PORT" >> "$ENV_FILE"
echo "DB_USER=$DB_USER" >> "$ENV_FILE"
echo "DB_PASSWORD=$DB_PASSWORD" >> "$ENV_FILE"
echo "DB_NAME=$DB_NAME" >> "$ENV_FILE"

echo ""
echo "✅ MySQL 설정이 .env 파일에 추가되었습니다!"
echo ""
echo "추가된 설정:"
echo "  DB_HOST=$DB_HOST"
echo "  DB_PORT=$DB_PORT"
echo "  DB_USER=$DB_USER"
echo "  DB_PASSWORD=***"
echo "  DB_NAME=$DB_NAME"
echo ""
echo "다음 단계: npm run migrate:accounts"

