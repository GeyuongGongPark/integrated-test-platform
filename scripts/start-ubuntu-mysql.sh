#!/bin/bash

echo "🚀 Ubuntu MySQL 서버 시작 스크립트"
echo "=================================="

# 필요한 디렉토리 생성
echo "📁 필요한 디렉토리 생성 중..."
mkdir -p ubuntu-setup mysql-backup

# 스크립트 실행 권한 부여
echo "🔐 스크립트 실행 권한 부여 중..."
chmod +x ubuntu-setup/*.sh

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리 중..."
docker-compose -f docker-compose.ubuntu.yml down -v

# Ubuntu MySQL 서버 시작
echo "🐳 Ubuntu MySQL 서버 시작 중..."
docker-compose -f docker-compose.ubuntu.yml up -d ubuntu-server

# 서버 시작 대기
echo "⏳ 서버 시작 대기 중... (30초)"
sleep 30

# Ubuntu 서버에 접속하여 MySQL 설정
echo "🔧 Ubuntu 서버에서 MySQL 설정 중..."
docker exec ubuntu-mysql-server bash /setup/setup-mysql.sh

# 상태 확인
echo "🏥 서버 상태 확인 중..."
docker exec ubuntu-mysql-server bash /setup/health-check.sh

echo ""
echo "🎉 Ubuntu MySQL 서버 설정 완료!"
echo "=================================="
echo "📊 데이터베이스: test_management"
echo "👤 Vercel 사용자: vercel_user"
echo "🔑 비밀번호: vercel_secure_pass_2025"
echo "🌐 포트: 3306"
echo "🔗 외부 접근: 허용됨"
echo ""
echo "📋 다음 단계:"
echo "1. 데이터 마이그레이션: ./migrate-data.sh"
echo "2. Vercel 환경변수 설정"
echo "3. 연결 테스트"
