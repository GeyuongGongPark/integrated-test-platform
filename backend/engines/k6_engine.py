import os
import subprocess

# k6 엔진 클래스 정의
class K6Engine:
    def __init__(self):
        self.k6_path = 'k6'  # k6 실행 파일 경로
    
    def execute_test(self, script_path, env_vars=None):
        """k6 성능 테스트 실행"""
        try:
            # 절대 경로로 변환
            if not os.path.isabs(script_path):
                # 현재 작업 디렉토리를 기준으로 절대 경로 생성
                base_dir = os.path.dirname(os.path.abspath(__file__))
                # backend/engines 디렉토리에서 상위로 이동하여 프로젝트 루트에 접근
                project_root = os.path.join(base_dir, '..', '..')
                script_path = os.path.join(project_root, script_path)
            
            # 스크립트 파일 존재 확인
            if not os.path.exists(script_path):
                return {
                    'status': 'Error',
                    'error': f'스크립트 파일을 찾을 수 없습니다: {script_path}'
                }
            
            # 환경 변수 설정
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # k6 명령어 구성
            cmd = [self.k6_path, 'run', script_path, '--out', 'json=result.json']
            
            # k6 실행
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=1800,  # 30분 타임아웃으로 증가
                cwd=os.path.dirname(script_path)  # 스크립트 디렉토리에서 실행
            )
            
            # 결과 파싱
            if result.returncode == 0:
                return {
                    'status': 'Pass',
                    'output': result.stdout,
                    'response_time_avg': 0.0,  # 실제로는 JSON 결과에서 파싱
                    'throughput': 0.0,
                    'error_rate': 0.0
                }
            else:
                return {
                    'status': 'Fail',
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'Error',
                'error': 'k6 실행 시간 초과'
            }
        except Exception as e:
            return {
                'status': 'Error',
                'error': str(e)
            }

# Docker를 사용하는 k6 엔진 (선택사항)
class DockerK6Engine:
    def __init__(self):
        self.docker_image = 'grafana/k6:latest'
    
    def execute_test(self, script_path, env_vars=None):
        """Docker를 사용한 k6 성능 테스트 실행"""
        try:
            # 절대 경로로 변환
            if not os.path.isabs(script_path):
                base_dir = os.path.dirname(os.path.abspath(__file__))
                # backend/engines 디렉토리에서 상위로 이동하여 프로젝트 루트에 접근
                project_root = os.path.join(base_dir, '..', '..')
                script_path = os.path.join(project_root, script_path)
            
            # 스크립트 파일 존재 확인
            if not os.path.exists(script_path):
                return {
                    'status': 'Error',
                    'error': f'스크립트 파일을 찾을 수 없습니다: {script_path}'
                }
            
            # Docker 볼륨 마운트를 위한 경로 설정
            script_dir = os.path.dirname(script_path)
            script_name = os.path.basename(script_path)
            
            # Docker 명령어 구성
            cmd = [
                'docker', 'run', '--rm',
                '-v', f'{script_dir}:/scripts',
                '-w', '/scripts',
                self.docker_image,
                'run', script_name, '--out', 'json=result.json'
            ]
            
            # 환경 변수 설정
            env = os.environ.copy()
            if env_vars:
                for key, value in env_vars.items():
                    cmd.extend(['-e', f'{key}={value}'])
            
            # Docker 실행
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            # 결과 파싱
            if result.returncode == 0:
                return {
                    'status': 'Pass',
                    'output': result.stdout,
                    'response_time_avg': 0.0,  # 실제로는 JSON 결과에서 파싱
                    'throughput': 0.0,
                    'error_rate': 0.0
                }
            else:
                return {
                    'status': 'Fail',
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'Error',
                'error': 'k6 실행 시간 초과'
            }
        except Exception as e:
            return {
                'status': 'Error',
                'error': str(e)
            }

# k6 엔진 인스턴스 생성
k6_engine = K6Engine()

# Docker k6 엔진 인스턴스 생성 (필요시 사용)
docker_k6_engine = DockerK6Engine() 