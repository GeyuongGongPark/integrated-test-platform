#!/bin/bash

# 모든 서버 재시작 스크립트
echo "🔄 모든 서버 재시작 중..."

# 기존 프로세스 종료
echo "📋 기존 프로세스 확인 중..."

# 백엔드 서버 종료
BACKEND_PID=$(lsof -ti:8000)
if [ ! -z "$BACKEND_PID" ]; then
    echo "🛑 기존 백엔드 프로세스 종료 중... (PID: $BACKEND_PID)"
    kill -9 $BACKEND_PID
fi

# Mock JIRA 서버 종료
MOCK_JIRA_PID=$(lsof -ti:5004)
if [ ! -z "$MOCK_JIRA_PID" ]; then
    echo "🛑 기존 Mock JIRA 프로세스 종료 중... (PID: $MOCK_JIRA_PID)"
    kill -9 $MOCK_JIRA_PID
fi

sleep 2

# 가상환경 활성화
cd backend
source venv/bin/activate

# Mock JIRA 서버 시작
echo "🚀 Mock JIRA 서버 시작 중..."
python mock_jira_server.py &
MOCK_JIRA_PID=$!

# 백엔드 서버 시작
echo "🚀 백엔드 서버 시작 중..."
python app.py &
BACKEND_PID=$!

# 서버 시작 대기
echo "⏳ 서버 시작 대기 중..."
sleep 5

# 서버 상태 확인
echo "🔍 서버 상태 확인 중..."

# Mock JIRA 서버 확인
if curl -s http://localhost:5004/health > /dev/null; then
    echo "✅ Mock JIRA 서버 시작 성공! (PID: $MOCK_JIRA_PID)"
else
    echo "❌ Mock JIRA 서버 시작 실패"
fi

# 백엔드 서버 확인
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 백엔드 서버 시작 성공! (PID: $BACKEND_PID)"
else
    echo "❌ 백엔드 서버 시작 실패"
fi

echo ""
echo "🎉 모든 서버 재시작 완료!"
echo "🌐 백엔드: http://localhost:8000"
echo "🌐 Mock JIRA: http://localhost:5004"
echo ""
echo "📋 프로세스 종료하려면:"
echo "   kill $BACKEND_PID $MOCK_JIRA_PID"
