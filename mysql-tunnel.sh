#!/bin/bash

# MySQL SSH 터널링 스크립트
# 사용법: ./mysql-tunnel.sh [SSH_USER] [SSH_HOST] [LOCAL_PORT] [REMOTE_PORT]

SSH_USER=${1:-"ggpark"}
SSH_HOST=${2:-"localhost"}
LOCAL_PORT=${3:-"3307"}
REMOTE_PORT=${4:-"3306"}

echo "🚀 MySQL SSH 터널 시작..."
echo "📍 로컬 포트: $LOCAL_PORT"
echo "🌐 원격 포트: $REMOTE_PORT"
echo "👤 SSH 사용자: $SSH_USER"
echo "🖥️  SSH 호스트: $SSH_HOST"
echo ""

# 터널 생성
echo "🔗 SSH 터널 생성 중..."
ssh -L ${LOCAL_PORT}:localhost:${REMOTE_PORT} ${SSH_USER}@${SSH_HOST} -N

echo "❌ SSH 터널이 종료되었습니다."
