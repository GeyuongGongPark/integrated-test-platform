#!/bin/bash

# API 테스트 스크립트
# 사용법: ./scripts/test-api.sh [TOKEN]

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정
API_URL="${API_URL:-http://localhost:8000}"
TOKEN="${1:-}"

echo -e "${BLUE}=== API 테스트 시작 ===${NC}"
echo "API URL: $API_URL"
echo ""

# 헬스 체크
echo -e "${YELLOW}1. 헬스 체크${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✓ 헬스 체크 성공 (HTTP $http_code)${NC}"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ 헬스 체크 실패 (HTTP $http_code)${NC}"
    echo "$body"
fi
echo ""

# 토큰이 제공된 경우에만 인증이 필요한 API 테스트
if [ -n "$TOKEN" ]; then
    echo -e "${YELLOW}2. 테스트 케이스 목록 조회${NC}"
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "$API_URL/api/testcases")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✓ 테스트 케이스 조회 성공 (HTTP $http_code)${NC}"
        count=$(echo "$body" | jq 'length' 2>/dev/null || echo "0")
        echo "총 $count 개의 테스트 케이스"
        echo "$body" | jq '.[0:3]' 2>/dev/null || echo "$body" | head -20
    else
        echo -e "${RED}✗ 테스트 케이스 조회 실패 (HTTP $http_code)${NC}"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    fi
    echo ""
    
    echo -e "${YELLOW}3. 알림 목록 조회${NC}"
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "$API_URL/api/notifications")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✓ 알림 조회 성공 (HTTP $http_code)${NC}"
        echo "$body" | jq '.notifications | length' 2>/dev/null || echo "응답 확인 필요"
    else
        echo -e "${RED}✗ 알림 조회 실패 (HTTP $http_code)${NC}"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    fi
    echo ""
else
    echo -e "${YELLOW}토큰이 제공되지 않아 인증이 필요한 API는 테스트하지 않습니다.${NC}"
    echo "사용법: ./scripts/test-api.sh YOUR_TOKEN"
    echo ""
fi

echo -e "${BLUE}=== 테스트 완료 ===${NC}"

