#!/bin/bash

# MySQL 데이터베이스 백업 스크립트
# Integrated Test Platform - MySQL Backup

DB_NAME="testmanager"
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/testmanager_${TIMESTAMP}.sql"

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

echo "🔧 MySQL 데이터베이스 백업 시작"
echo "=================================="

# 백업 실행
echo "📦 데이터베이스 백업 중..."
mysqldump -u root $DB_NAME > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ 백업 완료: $BACKUP_FILE"
    echo "📊 백업 파일 크기: $(du -h $BACKUP_FILE | cut -f1)"
else
    echo "❌ 백업 실패"
    exit 1
fi

echo "=================================="
echo "백업이 성공적으로 완료되었습니다!" 