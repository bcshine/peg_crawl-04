@echo off
echo 🚀 나스닥 PEG 분석 서버를 시작합니다...
echo.

cd /d "C:\Users\USER\Desktop\github_2\peg_crawl-02"

echo 📦 필요한 패키지 설치 중...
pip install -r requirements.txt

echo.
echo 🌐 Flask 서버 시작...
echo 📱 브라우저에서 http://localhost:5000 접속하세요
echo ⚠️  서버를 중지하려면 Ctrl+C를 누르세요
echo.

python app.py

pause 