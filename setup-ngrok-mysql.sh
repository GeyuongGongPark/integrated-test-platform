#!/bin/bash

echo "🚀 ngrok MySQL 터널 설정 스크립트"
echo "=================================="

# 기존 ngrok 프로세스 종료
echo "🧹 기존 ngrok 프로세스 정리 중..."
pkill ngrok 2>/dev/null
sleep 2

# Docker MySQL 서버 상태 확인
echo "🐳 Docker MySQL 서버 상태 확인 중..."
if ! docker ps | grep -q ubuntu-mysql-server; then
    echo "❌ Ubuntu MySQL 서버가 실행되지 않았습니다."
    echo "먼저 다음 명령어를 실행하세요:"
    echo "./start-ubuntu-mysql.sh"
    exit 1
fi

# MySQL 서비스 상태 확인
echo "🏥 MySQL 서비스 상태 확인 중..."
if ! docker exec ubuntu-mysql-server service mysql status | grep -q "running"; then
    echo "❌ MySQL 서비스가 실행되지 않았습니다."
    exit 1
fi

echo "✅ MySQL 서버가 정상적으로 실행 중입니다."

# 포트 3308 리스닝 상태 확인
echo "🔍 포트 3308 리스닝 상태 확인 중..."
if ! netstat -tlnp 2>/dev/null | grep -q ":3308"; then
    echo "❌ 포트 3308에서 MySQL이 리스닝하지 않습니다."
    exit 1
fi

echo "✅ 포트 3308에서 MySQL이 정상적으로 리스닝 중입니다."

# ngrok TCP 터널 시작
echo "🔗 ngrok TCP 터널 시작 중..."
echo "터널이 시작되면 'Forwarding' 라인에 표시되는 주소를 복사하세요."
echo "예시: tcp://2.tcp.us.ngrok.io:12345 -> localhost:3308"
echo ""
echo "터널을 중지하려면 Ctrl+C를 누르세요."
echo ""

# ngrok 터널 시작
ngrok tcp 3308

echo ""
echo "❌ ngrok 터널이 종료되었습니다."
