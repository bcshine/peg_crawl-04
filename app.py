from flask import Flask, render_template_string, jsonify, request, send_from_directory
import subprocess
import os
from datetime import datetime

app = Flask(__name__)

# 정적 파일 서빙을 위한 라우트 추가
@app.route('/logo2.png')
def logo():
    return send_from_directory('.', 'logo2.png')

@app.route('/bull_logo.png')
def bull_logo():
    return send_from_directory('.', 'bull_logo.png')

@app.route('/bnb.jpg')
def bnb_image():
    return send_from_directory('.', 'bnb.jpg')

# PWA 필수 파일 서빙
@app.route('/manifest.json')
def manifest():
    response = send_from_directory('.', 'manifest.json')
    response.headers['Content-Type'] = 'application/manifest+json'
    response.headers['Cache-Control'] = 'max-age=0, no-cache, no-store, must-revalidate'
    return response

@app.route('/sw.js')
def service_worker():
    response = send_from_directory('.', 'sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Cache-Control'] = 'max-age=0, no-cache, no-store, must-revalidate'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

# HTML 템플릿을 읽어오는 함수
def read_html_template():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/')
def index():
    html_content = read_html_template()
    return html_content

@app.route('/update', methods=['POST'])
def update_data():
    # 간단한 보안 검증 (헤더에서 특별한 값 확인)
    auth_header = request.headers.get('X-Admin-Key')
    if auth_header != 'nasdaq-peg-admin-2025':
        return jsonify({
            'success': False, 
            'message': '권한이 없습니다. 관리자만 접근 가능합니다.'
        }), 403
    
    try:
        print(f"[{datetime.now()}] 데이터 업데이트 시작...")
        
        # 1. 데이터 크롤링 실행
        print("1단계: 데이터 크롤링 중...")
        result1 = subprocess.run(['python', 'crawl_pe_peg_batch.py'], 
                               capture_output=True, text=True, cwd=os.getcwd())
        
        if result1.returncode != 0:
            return jsonify({
                'success': False, 
                'message': f'크롤링 오류: {result1.stderr}'
            })
        
        # 2. 웹 리포트 생성
        print("2단계: 웹 리포트 생성 중...")
        result2 = subprocess.run(['python', 'generate_web_report.py'], 
                               capture_output=True, text=True, cwd=os.getcwd())
        
        if result2.returncode != 0:
            return jsonify({
                'success': False, 
                'message': f'리포트 생성 오류: {result2.stderr}'
            })
        
        print(f"[{datetime.now()}] 업데이트 완료!")
        return jsonify({
            'success': True, 
            'message': '데이터가 성공적으로 업데이트되었습니다! 페이지를 새로고침해주세요.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'업데이트 중 오류 발생: {str(e)}'
        })

if __name__ == '__main__':
    print("🚀 나스닥 PEG 분석 서버 시작...")
    print("📱 브라우저에서 http://localhost:5000 접속하세요")
    print("📱 모바일에서는 http://14.33.80.107:5000 접속하세요")
    app.run(debug=True, host='0.0.0.0', port=5000) 