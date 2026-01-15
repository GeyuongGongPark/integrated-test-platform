# Slack Webhook 설정 가이드

이 가이드는 배포 환경에서 Slack 알림을 받기 위한 Webhook URL 설정 방법을 안내합니다.

## 📋 목차

1. [Slack Webhook URL 생성](#slack-webhook-url-생성)
2. [Vercel 배포 환경 설정](#vercel-배포-환경-설정)
3. [로컬 개발 환경 설정](#로컬-개발-환경-설정)
4. [사용자별 Slack 설정](#사용자별-slack-설정)
5. [테스트 및 확인](#테스트-및-확인)

## 🔗 Slack Webhook URL 생성

### 1. Slack 워크스페이스 접속
[Slack API 웹사이트](https://api.slack.com/apps)에 접속하여 로그인합니다.

### 2. 새 앱 생성
1. "Create New App" 클릭
2. "From scratch" 선택
3. App Name과 Workspace 선택 후 "Create App" 클릭

### 3. Incoming Webhooks 활성화
1. 왼쪽 메뉴에서 "Incoming Webhooks" 선택
2. "Activate Incoming Webhooks" 토글을 ON으로 변경
3. "Add New Webhook to Workspace" 클릭
4. 알림을 받을 채널 선택 후 "Allow" 클릭

### 4. Webhook URL 복사
생성된 Webhook URL을 복사합니다. 형식은 다음과 같습니다:
```
https://hooks.slack.com/services/TXXXXXXXXX/BXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXXX
```
**참고**: 위는 예시 형식입니다. 실제 URL은 Slack에서 생성한 고유한 URL을 사용하세요.

⚠️ **보안 주의사항**: 이 URL은 비밀번호와 같이 취급해야 합니다. 절대 Git에 커밋하지 마세요!

## 🚀 Vercel 배포 환경 설정

### 방법 1: Vercel 대시보드에서 설정 (권장)

1. **Vercel 대시보드 접속**
   - [Vercel Dashboard](https://vercel.com/dashboard)에 로그인
   - 프로젝트 선택

2. **환경 변수 추가**
   - 프로젝트 설정 > "Environment Variables" 메뉴 클릭
   - "Add New" 클릭
   - 다음 정보 입력:
     - **Key**: `SLACK_WEBHOOK_URL`
     - **Value**: 복사한 Webhook URL
     - **Environment**: Production, Preview, Development 모두 선택 (또는 필요에 따라 선택)
   - "Save" 클릭

3. **재배포**
   - 환경 변수 추가 후 자동으로 재배포되거나
   - 수동으로 "Redeploy" 클릭

### 방법 2: Vercel CLI로 설정

```bash
# Vercel CLI 설치 (없는 경우)
npm i -g vercel

# 환경 변수 추가
vercel env add SLACK_WEBHOOK_URL

# 프롬프트에 Webhook URL 입력
# Environment 선택 (Production/Preview/Development)

# 재배포
vercel --prod
```

## 💻 로컬 개발 환경 설정

### 1. `.env` 파일 생성/수정

프로젝트 루트의 `backend/` 디렉토리에 `.env` 파일을 생성하거나 수정합니다:

```bash
cd backend
nano .env  # 또는 원하는 에디터 사용
```

### 2. 환경 변수 추가

`.env` 파일에 다음 내용 추가:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_BOT_ID/YOUR_WEBHOOK_TOKEN
```

### 3. 서버 재시작

환경 변수를 추가한 후 서버를 재시작합니다:

```bash
# Flask 개발 서버 재시작
python app.py

# 또는
flask run
```

## 👤 사용자별 Slack 설정

앱에서 사용자별로 다른 Slack 채널로 알림을 받을 수 있습니다.

### API를 통한 설정

1. **알림 설정 조회**
   ```bash
   GET /notifications/settings
   Authorization: Bearer {token}
   ```

2. **Slack 설정 업데이트**
   ```bash
   PUT /notifications/settings
   Authorization: Bearer {token}
   Content-Type: application/json
   
   {
     "slack_enabled": true,
     "slack_webhook_url": "https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_BOT_ID/YOUR_WEBHOOK_TOKEN"
   }
   ```

### 우선순위

1. **사용자별 설정** (최우선)
   - 사용자가 `slack_webhook_url`을 설정한 경우 사용자별 URL 사용
   - `slack_enabled`가 `false`면 Slack 알림 비활성화

2. **전역 환경 변수**
   - 사용자별 설정이 없으면 `SLACK_WEBHOOK_URL` 환경 변수 사용

## ✅ 테스트 및 확인

### 1. 환경 변수 확인

서버 로그에서 다음 메시지를 확인하세요:

```
✅ SLACK_WEBHOOK_URL 환경 변수 로드됨: https://hooks.slack.com/services/...
```
**참고**: 로그에는 URL의 일부만 표시됩니다 (보안상 이유).

또는 다음 메시지가 보이면 환경 변수가 설정되지 않은 것입니다:

```
⚠️ SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.
```

### 2. 알림 테스트

테스트 케이스를 실행하거나 알림을 생성하면 Slack 채널에 메시지가 전송됩니다.

### 3. 로그 확인

서버 로그에서 다음 메시지를 확인하세요:

- 성공: `슬랙 알림 전송 성공: User {user_id}, Notification {notification_id}`
- 실패: `슬랙 알림 전송 실패: Status {status_code}, Response: {response}`

## 🔍 문제 해결

### Slack 메시지가 전송되지 않는 경우

1. **환경 변수 확인**
   ```bash
   # Vercel에서
   vercel env ls
   
   # 로컬에서
   echo $SLACK_WEBHOOK_URL
   ```

2. **Webhook URL 유효성 확인**
   - Slack 앱 설정에서 Webhook이 활성화되어 있는지 확인
   - URL이 올바른지 확인 (복사/붙여넣기 오류 확인)

3. **사용자 설정 확인**
   - `slack_enabled`가 `true`로 설정되어 있는지 확인
   - 사용자별 `slack_webhook_url`이 올바른지 확인

4. **서버 로그 확인**
   - Vercel: 대시보드 > Functions > app.py > Logs
   - 로컬: 터미널 출력 확인

### 환경 변수가 로드되지 않는 경우

1. **서버 재시작**
   - 환경 변수 추가 후 반드시 서버 재시작 필요

2. **파일 경로 확인**
   - `.env` 파일이 `backend/` 디렉토리에 있는지 확인
   - 파일명이 정확히 `.env`인지 확인 (`.env.local` 아님)

3. **Vercel 재배포**
   - 환경 변수 추가 후 재배포 필요

## 📚 참고 자료

- [Slack Incoming Webhooks 가이드](https://api.slack.com/messaging/webhooks)
- [Vercel 환경 변수 설정](https://vercel.com/docs/concepts/projects/environment-variables)
- [프로젝트 배포 가이드](./deployment/VERCEL_DEPLOYMENT_GUIDE.md)

## 🚨 보안 주의사항

1. **절대 Git에 커밋하지 마세요**
   - `.env` 파일은 `.gitignore`에 포함되어 있습니다
   - Webhook URL은 비밀번호처럼 취급하세요

2. **환경별 분리**
   - 개발/스테이징/프로덕션 환경별로 다른 Webhook URL 사용 권장
   - 각 환경의 채널을 분리하여 관리

3. **권한 관리**
   - Webhook URL을 공유할 때는 신뢰할 수 있는 사람에게만 공유
   - 필요시 Slack 앱 설정에서 Webhook 재생성

