from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv
from config import config

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
            db.session.execute('SELECT 1')
            print("✅ 데이터베이스 연결 성공")
            db.create_all()
            print("✅ PostgreSQL 테이블 생성 완료")
            
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
            
            print("Neon PostgreSQL 데이터베이스 초기화 완료!")
            
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 중 오류: {str(e)}")
            db.session.rollback()

# 헬스체크 엔드포인트
@app.route('/health', methods=['GET'])
def health_check():
    response = jsonify({
        'status': 'healthy', 
        'message': 'Test Platform Backend is running - Modularized Version',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'environment': 'production' if os.environ.get('VERCEL') else 'development'
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

# Flask 서버 실행
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000, debug=True) 