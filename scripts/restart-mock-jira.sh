#!/bin/bash

# Mock JIRA 서버 재시작 스크립트
echo "🔄 Mock JIRA 서버 재시작 중..."

# 기존 프로세스 종료
echo "📋 기존 Mock JIRA 프로세스 확인 중..."
MOCK_JIRA_PID=$(lsof -ti:5004)
if [ ! -z "$MOCK_JIRA_PID" ]; then
    echo "🛑 기존 Mock JIRA 프로세스 종료 중... (PID: $MOCK_JIRA_PID)"
    kill -9 $MOCK_JIRA_PID
    sleep 2
else
    echo "ℹ️  실행 중인 Mock JIRA 프로세스가 없습니다."
fi

# Mock JIRA 서버 실행
echo "🚀 Mock JIRA 서버 시작 중..."
cd backend
source venv/bin/activate
python mock_jira_server.py &

# 서버 시작 대기
echo "⏳ 서버 시작 대기 중..."
sleep 3

# 서버 상태 확인
echo "🔍 서버 상태 확인 중..."
if curl -s http://localhost:5004/health > /dev/null; then
    echo "✅ Mock JIRA 서버가 성공적으로 시작되었습니다!"
    echo "🌐 서버 주소: http://localhost:5004"
else
    echo "❌ Mock JIRA 서버 시작에 실패했습니다."
    echo "📋 로그를 확인해주세요."
fi

echo "🎉 Mock JIRA 서버 재시작 완료!"
