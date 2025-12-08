#!/usr/bin/env python3
"""
S3에서 데이터베이스 백업 파일 다운로드 스크립트
"""
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def download_backup_from_s3(bucket_name, s3_key, local_path):
    """S3에서 백업 파일 다운로드"""
    try:
        # AWS 자격 증명 확인
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_REGION', 'ap-northeast-2')
        
        if not aws_access_key or not aws_secret_key:
            print("❌ AWS 자격 증명이 설정되지 않았습니다.")
            print("환경 변수에 AWS_ACCESS_KEY_ID와 AWS_SECRET_ACCESS_KEY를 설정하세요.")
            return False
        
        # S3 클라이언트 생성
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        print(f"📥 S3에서 백업 파일 다운로드 중...")
        print(f"   버킷: {bucket_name}")
        print(f"   파일: {s3_key}")
        print(f"   저장 위치: {local_path}")
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # 파일 다운로드
        s3_client.download_file(bucket_name, s3_key, local_path)
        
        print(f"✅ 백업 파일 다운로드 완료: {local_path}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"❌ 버킷을 찾을 수 없습니다: {bucket_name}")
        elif error_code == 'NoSuchKey':
            print(f"❌ 파일을 찾을 수 없습니다: {s3_key}")
        elif error_code == 'AccessDenied':
            print(f"❌ 접근 권한이 없습니다. AWS 자격 증명을 확인하세요.")
        else:
            print(f"❌ 오류 발생: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")
        return False

def list_s3_backups(bucket_name, prefix='backup/'):
    """S3에서 백업 파일 목록 조회"""
    try:
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_REGION', 'ap-northeast-2')
        
        if not aws_access_key or not aws_secret_key:
            print("❌ AWS 자격 증명이 설정되지 않았습니다.")
            return []
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        print(f"🔍 S3 백업 파일 목록 조회 중...")
        print(f"   버킷: {bucket_name}")
        print(f"   경로: {prefix}")
        
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if 'Contents' not in response:
            print("📭 백업 파일이 없습니다.")
            return []
        
        backups = []
        for obj in response['Contents']:
            key = obj['Key']
            size = obj['Size']
            modified = obj['LastModified']
            backups.append({
                'key': key,
                'size': size,
                'modified': modified
            })
            print(f"   📄 {key} ({size:,} bytes, {modified})")
        
        return backups
        
    except ClientError as e:
        print(f"❌ 오류 발생: {e}")
        return []
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")
        return []

if __name__ == '__main__':
    import sys
    
    # 환경 변수에서 설정 가져오기
    bucket_name = os.environ.get('S3_BACKUP_BUCKET', 'test-platform-backups')
    backup_prefix = os.environ.get('S3_BACKUP_PREFIX', 'database/')
    local_backup_dir = os.environ.get('LOCAL_BACKUP_DIR', 'mysql-backup')
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'list':
            # 백업 파일 목록 조회
            backups = list_s3_backups(bucket_name, backup_prefix)
            if backups:
                print(f"\n✅ 총 {len(backups)}개의 백업 파일을 찾았습니다.")
        elif command == 'download':
            # 특정 파일 다운로드
            if len(sys.argv) < 3:
                print("사용법: python download_s3_backup.py download <s3_key>")
                print("예: python download_s3_backup.py download database/backup_20250101.sql")
                sys.exit(1)
            
            s3_key = sys.argv[2]
            local_path = os.path.join(local_backup_dir, os.path.basename(s3_key))
            download_backup_from_s3(bucket_name, s3_key, local_path)
        elif command == 'download-latest':
            # 최신 백업 파일 다운로드
            backups = list_s3_backups(bucket_name, backup_prefix)
            if not backups:
                print("❌ 다운로드할 백업 파일이 없습니다.")
                sys.exit(1)
            
            # 최신 파일 찾기
            latest = max(backups, key=lambda x: x['modified'])
            print(f"\n📥 최신 백업 파일 다운로드: {latest['key']}")
            local_path = os.path.join(local_backup_dir, os.path.basename(latest['key']))
            download_backup_from_s3(bucket_name, latest['key'], local_path)
        else:
            print("사용법:")
            print("  python download_s3_backup.py list              # 백업 파일 목록 조회")
            print("  python download_s3_backup.py download <s3_key>  # 특정 파일 다운로드")
            print("  python download_s3_backup.py download-latest   # 최신 파일 다운로드")
    else:
        print("S3 백업 다운로드 스크립트")
        print("\n환경 변수 설정:")
        print("  AWS_ACCESS_KEY_ID      - AWS 액세스 키")
        print("  AWS_SECRET_ACCESS_KEY  - AWS 시크릿 키")
        print("  AWS_REGION            - AWS 리전 (기본값: ap-northeast-2)")
        print("  S3_BACKUP_BUCKET       - 백업 버킷 이름 (기본값: test-platform-backups)")
        print("  S3_BACKUP_PREFIX       - 백업 파일 경로 (기본값: database/)")
        print("\n사용법:")
        print("  python download_s3_backup.py list              # 백업 파일 목록 조회")
        print("  python download_s3_backup.py download <s3_key>  # 특정 파일 다운로드")
        print("  python download_s3_backup.py download-latest   # 최신 파일 다운로드")

