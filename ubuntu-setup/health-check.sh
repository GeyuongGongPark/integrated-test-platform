#!/bin/bash

echo "🏥 Ubuntu MySQL 서버 상태 확인 중..."

# MySQL 서비스 상태 확인
echo "📊 MySQL 서비스 상태:"
service mysql status

# MySQL 연결 테스트
echo "🔗 MySQL 연결 테스트:"
if mysql -u root -p1q2w#E$R -e "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ MySQL 연결 성공"
else
    echo "❌ MySQL 연결 실패"
fi

# 데이터베이스 목록 확인
echo "🗄️ 데이터베이스 목록:"
mysql -u root -p1q2w#E$R -e "SHOW DATABASES;"

# 사용자 목록 확인
echo "👥 사용자 목록:"
mysql -u root -p1q2w#E$R -e "SELECT User, Host FROM mysql.user WHERE User IN ('root', 'vercel_user');"

# 포트 리스닝 상태 확인
echo "🌐 포트 리스닝 상태:"
netstat -tlnp | grep :3306

# Vercel 사용자 권한 확인
echo "🔑 Vercel 사용자 권한:"
mysql -u root -p1q2w#E$R -e "SHOW GRANTS FOR 'vercel_user'@'%';"

echo "✅ 상태 확인 완료!"
