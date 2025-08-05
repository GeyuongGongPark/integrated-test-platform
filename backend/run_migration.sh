#!/bin/bash

echo "========================================"
echo "Neon DB 마이그레이션 스크립트"
echo "========================================"
echo

# 가상환경 활성화 (있는 경우)
if [ -f "venv/bin/activate" ]; then
    echo "가상환경을 활성화합니다..."
    source venv/bin/activate
fi

# 의존성 확인
echo "의존성을 확인합니다..."
python -c "import pandas, sqlalchemy, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "필요한 패키지를 설치합니다..."
    pip install pandas sqlalchemy python-dotenv psycopg2-binary
fi

echo
echo "마이그레이션을 시작합니다..."
echo

# 간단한 마이그레이션 스크립트 실행
python quick_migrate_neon.py

echo
echo "마이그레이션이 완료되었습니다." 