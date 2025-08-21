#!/bin/bash

echo "🔄 데이터 마이그레이션 시작..."

# 로컬 MySQL에서 데이터 덤프
echo "📤 로컬 MySQL에서 데이터 덤프 중..."
mysqldump -h 127.0.0.1 -P 3307 -u root -p1q2w#E$R test_management > /backup/local_backup.sql

if [ $? -eq 0 ]; then
    echo "✅ 로컬 데이터 덤프 완료: /backup/local_backup.sql"
else
    echo "❌ 로컬 데이터 덤프 실패"
    exit 1
fi

# Ubuntu MySQL에 데이터 복원
echo "📥 Ubuntu MySQL에 데이터 복원 중..."
mysql -u root -p1q2w#E$R test_management < /backup/local_backup.sql

if [ $? -eq 0 ]; then
    echo "✅ 데이터 복원 완료!"
    echo "📊 복원된 데이터베이스: test_management"
else
    echo "❌ 데이터 복원 실패"
    exit 1
fi

# 테이블 확인
echo "📋 복원된 테이블 목록:"
mysql -u root -p1q2w#E$R -e "USE test_management; SHOW TABLES;"

echo "🎉 마이그레이션 완료!"
