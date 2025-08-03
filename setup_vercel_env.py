#!/usr/bin/env python3
"""
Vercel 환경변수 설정 스크립트
"""

import subprocess
import json

# 환경변수 설정
env_vars = {
    "DEV_DATABASE_URL": "postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
    "PROD_DATABASE_URL": "postgresql://neondb_owner:npg_jAtyhE2HW3pY@ep-flat-frog-a1tlnavw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
    "FLASK_ENV": "production",
    "SECRET_KEY": "your-production-secret-key-here-2025",
    "CORS_ORIGINS": "https://integrated-test-platform-4v4m90qr3-gyeonggong-parks-projects.vercel.app"
}

def set_vercel_env_vars():
    """Vercel 환경변수 설정"""
    print("🚀 Vercel 환경변수 설정 시작...")
    
    for key, value in env_vars.items():
        try:
            cmd = f'vercel env add {key} production'
            print(f"설정 중: {key}")
            
            # 환경변수 설정 명령어 실행
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                input=value
            )
            
            if result.returncode == 0:
                print(f"✅ {key} 설정 완료")
            else:
                print(f"❌ {key} 설정 실패: {result.stderr}")
                
        except Exception as e:
            print(f"❌ {key} 설정 중 오류: {e}")

def main():
    print("=" * 50)
    print("🔧 Vercel 환경변수 설정 도구")
    print("=" * 50)
    
    # 환경변수 설정
    set_vercel_env_vars()
    
    print("\n" + "=" * 50)
    print("📋 설정할 환경변수 목록:")
    for key, value in env_vars.items():
        print(f"  {key}: {value[:50]}...")
    
    print("\n💡 수동 설정 방법:")
    print("1. Vercel 대시보드 접속")
    print("2. 프로젝트 선택")
    print("3. Settings > Environment Variables")
    print("4. 위의 환경변수들을 추가")
    
    print("\n🎯 다음 단계:")
    print("1. 환경변수 설정 완료 후 재배포")
    print("2. API 엔드포인트 테스트")
    print("3. 프론트엔드 배포")

if __name__ == "__main__":
    main() 