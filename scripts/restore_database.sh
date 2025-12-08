#!/bin/bash

# 데이터베이스 복구 스크립트
# local_backup.sql 파일을 사용하여 데이터베이스를 복구합니다.

set -e

BACKUP_FILE="mysql-backup/local_backup.sql"
DB_NAME="test_management"
DB_USER="root"
DB_PASSWORD="1q2w#E$R"
DB_HOST="localhost"
DB_PORT="3306"

# 색상 코드
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔄 데이터베이스 복구 시작..."

# 백업 파일 확인
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ 백업 파일을 찾을 수 없습니다: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 백업 파일 확인: $BACKUP_FILE${NC}"
echo "   파일 크기: $(ls -lh $BACKUP_FILE | awk '{print $5}')"

# MySQL 연결 테스트
echo ""
echo "🔍 MySQL 연결 테스트 중..."
if ! mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" > /dev/null 2>&1; then
    echo -e "${RED}❌ MySQL 연결 실패${NC}"
    echo "   호스트: $DB_HOST"
    echo "   포트: $DB_PORT"
    echo "   사용자: $DB_USER"
    echo ""
    echo "다음 사항을 확인하세요:"
    echo "  1. MySQL 서비스가 실행 중인지 확인"
    echo "  2. Docker Compose로 MySQL 실행: docker-compose up -d mysql"
    echo "  3. 연결 정보가 올바른지 확인 (.env 파일)"
    exit 1
fi

echo -e "${GREEN}✅ MySQL 연결 성공${NC}"

# 데이터베이스 존재 여부 확인 및 생성
echo ""
echo "📊 데이터베이스 확인 중..."
if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "USE $DB_NAME" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  데이터베이스 '$DB_NAME'가 이미 존재합니다.${NC}"
    read -p "기존 데이터베이스를 삭제하고 복구하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "복구를 취소했습니다."
        exit 0
    fi
    echo "🗑️  기존 데이터베이스 삭제 중..."
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME;"
fi

echo "📦 데이터베이스 생성 중..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo -e "${GREEN}✅ 데이터베이스 생성 완료${NC}"

# 백업 파일 복구
echo ""
echo "📥 백업 파일 복구 중..."
echo "   이 작업은 몇 분이 걸릴 수 있습니다..."

if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$BACKUP_FILE"; then
    echo -e "${GREEN}✅ 데이터베이스 복구 완료!${NC}"
else
    echo -e "${RED}❌ 데이터베이스 복구 실패${NC}"
    exit 1
fi

# 복구 확인
echo ""
echo "🔍 복구 확인 중..."
TABLE_COUNT=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES;" 2>/dev/null | wc -l | tr -d ' ')
TABLE_COUNT=$((TABLE_COUNT - 1))  # 헤더 제외

if [ "$TABLE_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ 복구 확인 완료${NC}"
    echo "   복구된 테이블 수: $TABLE_COUNT"
    echo ""
    echo "📋 테이블 목록:"
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES;" 2>/dev/null | tail -n +2
else
    echo -e "${YELLOW}⚠️  테이블이 복구되지 않았습니다.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 데이터베이스 복구 프로세스 완료!${NC}"
echo ""
echo "다음 단계:"
echo "  1. 백엔드 애플리케이션 재시작"
echo "  2. http://localhost:8000/health 에서 데이터베이스 연결 확인"
echo "  3. http://localhost:8000/init-db 로 기본 사용자 생성 (필요시)"

