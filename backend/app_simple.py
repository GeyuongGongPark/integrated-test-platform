from flask import Flask, jsonify, request
from datetime import datetime
import os

app = Flask(__name__)

# 기본 설정
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'fallback-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///fallback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS 헤더 추가 함수
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Access-Control-Allow-Origin'
    response.headers['Access-Control-Allow-Credentials'] = 'false'
    response.headers['Access-Control-Max-Age'] = '86400'
    response.headers['Access-Control-Expose-Headers'] = '*'
    return response

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        return add_cors_headers(response), 200
    
    try:
        response = jsonify({
            'status': 'healthy', 
            'message': 'Test Platform Backend is running - Simple Version',
            'version': '2.0.1',
            'timestamp': datetime.now().isoformat(),
            'environment': 'production' if os.environ.get('VERCEL') else 'development',
            'database': {
                'status': 'not_configured',
                'url_set': 'Yes' if os.environ.get('DATABASE_URL') else 'No'
            }
        })
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({
            'status': 'unhealthy',
            'message': f'Health check failed: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'environment': 'production' if os.environ.get('VERCEL') else 'development'
        })
        return add_cors_headers(response), 500

@app.route('/test', methods=['GET', 'OPTIONS'])
def test_endpoint():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        return add_cors_headers(response), 200
    
    try:
        response = jsonify({
            'status': 'test_ok',
            'message': 'Backend is working - Simple Version',
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

@app.route('/cors-test', methods=['GET', 'OPTIONS'])
def cors_test():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        return add_cors_headers(response), 200
    
    response = jsonify({
        'status': 'cors_ok',
        'message': 'CORS is working - Simple Version',
        'timestamp': datetime.now().isoformat()
    })
    return add_cors_headers(response), 200

@app.route('/diagnose', methods=['GET', 'OPTIONS'])
def diagnose():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight_ok'})
        return add_cors_headers(response), 200
    
    try:
        env_vars = {
            'VERCEL': os.environ.get('VERCEL', 'Not set'),
            'DATABASE_URL': 'Set' if os.environ.get('DATABASE_URL') else 'Not set',
            'SECRET_KEY': 'Set' if os.environ.get('SECRET_KEY') else 'Not set'
        }
        
        response = jsonify({
            'status': 'diagnosis_ok',
            'message': 'Diagnosis completed - Simple Version',
            'environment_vars': env_vars,
            'timestamp': datetime.now().isoformat()
        })
        return add_cors_headers(response), 200
    except Exception as e:
        response = jsonify({
            'status': 'diagnosis_error',
            'message': f'Diagnosis failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })
        return add_cors_headers(response), 500

if __name__ == '__main__':
    app.run(debug=True)
