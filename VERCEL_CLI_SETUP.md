# Vercel CLI 빠른 설정 가이드

## 1단계: Vercel CLI 설치

```bash
npm install -g vercel
```

## 2단계: Vercel 로그인

```bash
vercel login
```

## 3단계: 백엔드 배포

```bash
cd backend
vercel
```

설정 옵션:
- **Set up and deploy**: `Y`
- **Which scope**: `(선택)`
- **Link to existing project**: `N`
- **Project name**: `test-platform-backend`
- **In which directory is your code located**: `./`
- **Want to override the settings**: `N`

## 4단계: 프론트엔드 배포

```bash
cd ../frontend
vercel
```

설정 옵션:
- **Set up and deploy**: `Y`
- **Which scope**: `(선택)`
- **Link to existing project**: `N`
- **Project name**: `test-platform-frontend`
- **In which directory is your code located**: `./`
- **Want to override the settings**: `N`

## 5단계: 환경 변수 설정

### 백엔드 환경 변수
```bash
cd backend
vercel env add DATABASE_URL
vercel env add FLASK_ENV
vercel env add FLASK_APP
```

### 프론트엔드 환경 변수
```bash
cd ../frontend
vercel env add REACT_APP_API_URL
```

## 6단계: 프로덕션 배포

```bash
# 백엔드
cd backend
vercel --prod

# 프론트엔드
cd ../frontend
vercel --prod
```

## 7단계: 도메인 확인

```bash
# 백엔드 도메인 확인
vercel ls

# 프론트엔드 도메인 확인
cd ../frontend
vercel ls
```

## 8단계: GitHub Secrets 설정

Vercel CLI로 생성된 정보를 GitHub Secrets에 추가:

```bash
# 프로젝트 ID 확인
vercel project ls

# 조직 ID 확인
vercel whoami
```

## 9단계: 자동 배포 테스트

```bash
# 코드 변경 후
git add .
git commit -m "테스트 배포"
git push
```

## 유용한 Vercel CLI 명령어

```bash
# 프로젝트 목록
vercel ls

# 프로젝트 정보
vercel project ls

# 환경 변수 확인
vercel env ls

# 로그 확인
vercel logs

# 프로젝트 삭제
vercel remove
``` 