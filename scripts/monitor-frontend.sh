#!/bin/bash

# 프론트엔드 로그 모니터링 스크립트
# 사용법: ./scripts/monitor-frontend.sh [LOG_FILE]

LOG_FILE="${1:-frontend.log}"

# 색상 정의
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}프론트엔드 로그 모니터링 시작...${NC}"
echo "로그 파일: $LOG_FILE"
echo "종료하려면 Ctrl+C를 누르세요"
echo ""

# 로그 파일이 없으면 생성
touch "$LOG_FILE"

# 실시간 로그 확인
tail -f "$LOG_FILE" 2>/dev/null | \
  while IFS= read -r line; do
    # 타임스탬프 추가
    timestamp=$(date +'%H:%M:%S')
    
    # 에러는 빨간색으로
    if echo "$line" | grep -qiE "(error|failed|exception)"; then
      echo -e "[$timestamp] ${RED}$line${NC}"
    # 경고는 노란색으로
    elif echo "$line" | grep -qiE "(warning|warn)"; then
      echo -e "[$timestamp] ${YELLOW}$line${NC}"
    # 성공은 초록색으로
    elif echo "$line" | grep -qiE "(success|compiled|ready)"; then
      echo -e "[$timestamp] ${GREEN}$line${NC}"
    # 일반 로그
    else
      echo -e "[$timestamp] $line"
    fi
  done

