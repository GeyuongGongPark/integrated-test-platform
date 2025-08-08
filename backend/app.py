from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv
from config import config
from sqlalchemy import text

# 모델 import
from models import db

# 유틸리티 import
from utils.cors import setup_cors, add_cors_headers

# 라우트 import
from routes.users import users_bp
from routes.testcases import testcases_bp
from routes.performance import performance_bp
from routes.automation import automation_bp
from routes.folders import folders_bp
from routes.dashboard import dashboard_bp

# .env 파일 로드
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

def create_app(config_name=None):
    if config_name is None:
        if os.environ.get('VERCEL'):
            config_name = 'production'
        elif os.environ.get('FLASK_ENV') == 'production':
            config_name = 'production'
        else:
            config_name = 'development'
    
    app = Flask(__name__)
    
    # Vercel 환경에서 instance_path 설정
    if os.environ.get('VERCEL'):
        app.instance_path = '/tmp'
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # CORS 설정
    setup_cors(app)
    
    # 데이터베이스 초기화
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Blueprint 등록
    app.register_blueprint(users_bp)
    app.register_blueprint(testcases_bp)
    app.register_blueprint(performance_bp)
    app.register_blueprint(automation_bp)
    app.register_blueprint(folders_bp)
    app.register_blueprint(dashboard_bp)
    
    return app, db, migrate

app, db, migrate = create_app()

def init_db():
    """데이터베이스 초기화"""
    with app.app_context():
        try:
            # 데이터베이스 연결 확인
            db.session.execute(text('SELECT 1'))
            print("✅ 데이터베이스 연결 성공")
            
            # 현재 데이터베이스 URI 로깅
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
            print(f"🔗 현재 데이터베이스 URI: {db_uri[:50]}...")
            
            # 모든 테이블 생성
            db.create_all()
            print("✅ 데이터베이스 테이블 생성 완료")
            
            # 테이블 목록 확인
            try:
                result = db.session.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
                print(f"📋 생성된 테이블 목록: {tables}")
            except Exception as e:
                print(f"⚠️ 테이블 목록 확인 중 오류: {str(e)}")
            
            # 기본 프로젝트 생성
            from models import Project
            default_project = Project.query.filter_by(name='Test Management System').first()
            if not default_project:
                default_project = Project(
                    name='Test Management System',
                    description='통합 테스트 관리 시스템'
                )
                db.session.add(default_project)
                db.session.commit()
                print("✅ 기본 프로젝트 생성 완료")
            
            print("데이터베이스 초기화 완료!")
            
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 중 오류: {str(e)}")
            print(f"🔍 오류 타입: {type(e).__name__}")
            db.session.rollback()
            raise

# 헬스체크 엔드포인트
@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        return add_cors_headers(response), 200
    
    try:
        # 데이터베이스 연결 확인
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
        
        # 테이블 존재 여부 확인
        from models import TestCase, PerformanceTest, TestExecution
        tables_exist = True
        try:
            TestCase.query.first()
            PerformanceTest.query.first()
            TestExecution.query.first()
        except Exception as e:
            tables_exist = False
            print(f"테이블 확인 중 오류: {str(e)}")
        
        response = jsonify({
            'status': 'healthy', 
            'message': 'Test Platform Backend is running - Modularized Version',
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat(),
            'environment': 'production' if os.environ.get('VERCEL') else 'development',
            'database': {
                'status': db_status,
                'tables_exist': tables_exist,
                'url_set': 'Yes' if os.environ.get('DATABASE_URL') else 'No'
            }
        })
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'environment': 'production' if os.environ.get('VERCEL') else 'development'
        })
        return add_cors_headers(response), 500

# 간단한 테스트 엔드포인트
@app.route('/test', methods=['GET', 'OPTIONS'])
def test_endpoint():
    """간단한 테스트 엔드포인트"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        return add_cors_headers(response), 200
    
    try:
        # 환경 변수 확인
        db_url = os.environ.get('DATABASE_URL', 'Not set')
        secret_key = os.environ.get('SECRET_KEY', 'Not set')
        flask_env = os.environ.get('FLASK_ENV', 'Not set')
        vercel_env = os.environ.get('VERCEL', 'Not set')
        
        # 데이터베이스 연결 테스트
        db_connection_status = 'unknown'
        db_error = None
        try:
            db.session.execute(text('SELECT 1'))
            db_connection_status = 'connected'
        except Exception as e:
            db_connection_status = 'failed'
            db_error = str(e)
        
        # 현재 설정된 데이터베이스 URI 확인
        current_db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        
        response = jsonify({
            'status': 'test_ok',
            'message': 'Backend is working',
            'environment_vars': {
                'DATABASE_URL_set': 'Yes' if db_url != 'Not set' else 'No',
                'DATABASE_URL_length': len(db_url) if db_url != 'Not set' else 0,
                'SECRET_KEY_set': 'Yes' if secret_key != 'Not set' else 'No',
                'FLASK_ENV': flask_env,
                'VERCEL': vercel_env
            },
            'database': {
                'connection_status': db_connection_status,
                'current_uri': current_db_uri[:50] + '...' if len(current_db_uri) > 50 else current_db_uri,
                'error': db_error
            },
            'timestamp': datetime.now().isoformat()
        })
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        })
        return add_cors_headers(response), 500

# CORS 테스트 엔드포인트
@app.route('/cors-test', methods=['GET', 'OPTIONS'])
def cors_test():
    """CORS 테스트 엔드포인트"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        return add_cors_headers(response), 200
    
    response = jsonify({
        'status': 'cors_ok',
        'message': 'CORS is working',
        'origin': request.headers.get('Origin', 'No origin'),
        'timestamp': datetime.now().isoformat()
    })
    return add_cors_headers(response), 200

# CORS preflight 요청 처리
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """CORS preflight 요청 처리"""
    origin = request.headers.get('Origin')
    
    response = jsonify({'status': 'preflight_ok'})
    
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Access-Control-Allow-Origin'
    response.headers['Access-Control-Allow-Credentials'] = 'false'
    response.headers['Access-Control-Max-Age'] = '86400'
    response.headers['Access-Control-Expose-Headers'] = '*'
    
    return response, 200

# 데이터베이스 초기화 엔드포인트
@app.route('/init-db', methods=['POST', 'OPTIONS'])
def initialize_database():
    """데이터베이스 초기화 엔드포인트"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        return add_cors_headers(response), 200
    
    try:
        init_db()
        response = jsonify({
            'status': 'success',
            'message': '데이터베이스 초기화가 완료되었습니다.',
            'timestamp': datetime.now().isoformat()
        })
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'message': f'데이터베이스 초기화 중 오류가 발생했습니다: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })
        return add_cors_headers(response), 500

# Flask 서버 실행
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000, debug=True)

# Vercel 환경에서 앱 시작 시 데이터베이스 초기화
if os.environ.get('VERCEL'):
    try:
        init_db()
        print("✅ Vercel 환경에서 데이터베이스 초기화 완료")
    except Exception as e:
        print(f"❌ Vercel 환경에서 데이터베이스 초기화 실패: {str(e)}") 