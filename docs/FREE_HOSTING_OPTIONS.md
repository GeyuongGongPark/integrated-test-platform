# 🆓 무료 호스팅 옵션 가이드

## 🎯 현재 사용 중인 조합

### **성공적으로 배포된 조합**
1. **데이터베이스**: Neon PostgreSQL (무료)
2. **백엔드**: Vercel (무료)
3. **프론트엔드**: Vercel (무료)
4. **CI/CD**: GitHub Actions (무료)

### **배포된 URL**
- **프론트엔드**: https://integrated-test-platform-fe-gyeonggong-parks-projects.vercel.app
- **백엔드 API**: https://integrated-test-platform.vercel.app
- **헬스체크**: https://integrated-test-platform.vercel.app/health

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
| **Vercel** | 무제한 | 서버리스 함수 제한 | ❌ |
| **Fly.io** | 3개 앱, 3GB | 3개 앱 | ✅ |
| **Google Cloud Run** | 200만 요청/월 | 요청 수 제한 | ✅ |
| **AWS Lambda** | 100만 요청/월 | 요청 수 제한 | ❌ |
| **Render** | 750시간/월 | 자동 슬립 | ✅ |
| **Railway** | $5 크레딧/월 | 크레딧 제한 | ✅ |

## 🎯 추천 조합

### **현재 사용 중인 조합 (성공)**
1. **데이터베이스**: Neon PostgreSQL (무료)
2. **백엔드**: Vercel (무료)
3. **프론트엔드**: Vercel (무료)
4. **CI/CD**: GitHub Actions (무료)

### **완전 무료 조합 (대안)**
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

## 🛠️ Vercel 배포 설정 (현재 사용 중)

### 1. Vercel CLI 설치
```bash
npm install -g vercel
```

### 2. Vercel 프로젝트 설정
```bash
cd integrated-test-platform/backend
vercel
```

### 3. vercel.json 설정
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "DATABASE_URL": "postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
    "FLASK_ENV": "production",
    "FLASK_APP": "app.py"
  }
}
```

### 4. 프론트엔드 배포
```bash
cd integrated-test-platform/frontend
vercel
```

## 🛠️ Fly.io 배포 설정 (대안)

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
  DATABASE_URL = "postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
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
# Vercel (현재 사용 중)
VERCEL_TOKEN=your-vercel-token
VERCEL_PROJECT_ID=your-project-id
VERCEL_ORG_ID=your-org-id

# Fly.io (대안)
FLY_API_TOKEN=your-fly-api-token

# Google Cloud Run (대안)
GCP_PROJECT_ID=your-project-id
GCP_SA_KEY=your-service-account-key

# AWS Lambda (대안)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

## 📊 성능 비교

### **Vercel (현재 사용 중)**
- **장점**: 빠른 배포, 자동 HTTPS, 글로벌 CDN
- **단점**: 서버리스 함수 제한, 콜드 스타트
- **적합한 용도**: 중소규모 프로젝트, 빠른 프로토타이핑

### **Fly.io (대안)**
- **장점**: Docker 지원, 글로벌 배포, 빠른 성능
- **단점**: 설정 복잡도
- **적합한 용도**: 대규모 프로젝트, Docker 기반 배포

### **Google Cloud Run (대안)**
- **장점**: 완전 관리형, 자동 스케일링, 높은 안정성
- **단점**: 설정 복잡도, 비용 증가 가능성
- **적합한 용도**: 엔터프라이즈급 프로젝트

## 🎯 결론

현재 **Vercel + Neon PostgreSQL** 조합이 가장 성공적으로 작동하고 있습니다. 이 조합은:

- ✅ **완전 무료**: 모든 서비스가 무료 플랜으로 운영
- ✅ **빠른 배포**: GitHub Actions와 연동하여 자동 배포
- ✅ **안정적**: 프로덕션 환경에서 안정적으로 운영
- ✅ **확장 가능**: 향후 기능 확장에 대응 가능

다른 옵션들은 필요에 따라 대안으로 고려할 수 있습니다. 