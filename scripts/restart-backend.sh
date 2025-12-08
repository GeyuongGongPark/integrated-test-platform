#!/bin/bash

# 백엔드 재시작 스크립트
echo "🔄 백엔드 서버 재시작 중..."

# 기존 프로세스 종료
echo "📋 기존 백엔드 프로세스 확인 중..."
BACKEND_PID=$(lsof -ti:8000)
if [ ! -z "$BACKEND_PID" ]; then
    echo "🛑 기존 백엔드 프로세스 종료 중... (PID: $BACKEND_PID)"
    kill -9 $BACKEND_PID
    sleep 2
else
    echo "ℹ️  실행 중인 백엔드 프로세스가 없습니다."
fi

# 가상환경 활성화 및 백엔드 실행
echo "🚀 백엔드 서버 시작 중..."
cd backend
source venv/bin/activate
python app.py &

# 서버 시작 대기
echo "⏳ 서버 시작 대기 중..."
sleep 3

# 서버 상태 확인
echo "🔍 서버 상태 확인 중..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 백엔드 서버가 성공적으로 시작되었습니다!"
    echo "🌐 서버 주소: http://localhost:8000"
else
    echo "❌ 백엔드 서버 시작에 실패했습니다."
    echo "📋 로그를 확인해주세요."
fi

echo "🎉 백엔드 재시작 완료!"
