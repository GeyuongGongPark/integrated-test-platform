# 🆓 무료 호스팅 옵션 가이드

## 🐳 Docker 기반 무료 호스팅

### 1. **Railway (Docker 지원)**
- **무료 플랜**: 월 $5 크레딧
- **장점**: Docker 컨테이너 직접 배포
- **URL**: https://railway.app

### 2. **Render (Docker 지원)**
- **무료 플랜**: 월 750시간
- **장점**: Docker 컨테이너 지원
- **URL**: https://render.com

### 3. **Fly.io (추천)**
- **무료 플랜**: 3개 앱, 3GB 저장소
- **장점**: 글로벌 CDN, 빠른 성능
- **URL**: https://fly.io

### 4. **Google Cloud Run**
- **무료 플랜**: 월 200만 요청
- **장점**: 완전 관리형, 자동 스케일링
- **URL**: https://cloud.google.com/run

### 5. **AWS Lambda**
- **무료 플랜**: 월 100만 요청
- **장점**: 서버리스, 자동 스케일링
- **URL**: https://aws.amazon.com/lambda

## 🚀 GitHub Actions + 무료 호스팅 조합

### 옵션 A: Fly.io + GitHub Actions
```yaml
# .github/workflows/deploy.yml
- name: Deploy to Fly.io
  uses: superfly/flyctl-actions/setup-flyctl@master
- name: Deploy app
  run: flyctl deploy --remote-only
  env:
    FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

### 옵션 B: Google Cloud Run + GitHub Actions
```yaml
# .github/workflows/deploy.yml
- name: Deploy to Cloud Run
  uses: google-github-actions/deploy-cloudrun@v1
  with:
    service: test-platform-backend
    image: gcr.io/${{ secrets.GCP_PROJECT_ID }}/test-platform-backend
```

### 옵션 C: AWS Lambda + GitHub Actions
```yaml
# .github/workflows/deploy.yml
- name: Deploy to Lambda
  uses: aws-actions/configure-aws-credentials@v1
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: ap-northeast-2
```

## 💰 비용 비교

| 서비스 | 무료 플랜 | 제한사항 | Docker 지원 |
|--------|-----------|----------|-------------|
| **Fly.io** | 3개 앱, 3GB | 3개 앱 | ✅ |
| **Google Cloud Run** | 200만 요청/월 | 요청 수 제한 | ✅ |
| **AWS Lambda** | 100만 요청/월 | 요청 수 제한 | ❌ |
| **Render** | 750시간/월 | 자동 슬립 | ✅ |
| **Railway** | $5 크레딧/월 | 크레딧 제한 | ✅ |

## 🎯 추천 조합

### **완전 무료 조합 (추천)**
1. **데이터베이스**: Neon PostgreSQL (무료)
2. **백엔드**: Fly.io (무료)
3. **프론트엔드**: Vercel (무료)
4. **파일 저장소**: Cloudinary (무료)
5. **CI/CD**: GitHub Actions (무료)

### **확장성 좋은 조합**
1. **데이터베이스**: Neon PostgreSQL (무료)
2. **백엔드**: Google Cloud Run (무료)
3. **프론트엔드**: Vercel (무료)
4. **파일 저장소**: Cloudinary (무료)
5. **CI/CD**: GitHub Actions (무료)

## 🛠️ Fly.io 배포 설정

### 1. Fly.io CLI 설치
```bash
# Windows
winget install fly.io.flyctl

# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh
```

### 2. Fly.io 앱 생성
```bash
flyctl auth login
flyctl apps create test-platform-backend
```

### 3. fly.toml 설정
```toml
app = "test-platform-backend"
primary_region = "nrt"

[build]

[env]
  DATABASE_URL = "postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-hidden-paper-a1iuh28r-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
  FLASK_ENV = "production"
  FLASK_APP = "app.py"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"
```

### 4. 배포
```bash
flyctl deploy
```

## 🔧 GitHub Secrets 설정

GitHub 저장소 설정에서 다음 Secrets 추가:

```bash
# Fly.io
FLY_API_TOKEN=your-fly-api-token

# Google Cloud Run
GCP_PROJECT_ID=your-project-id
GCP_SA_KEY=your-service-account-key

# AWS Lambda
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-hidden-paper-a1iuh28r-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
``` 