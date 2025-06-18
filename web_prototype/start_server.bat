@echo off
chcp 65001 > nul
echo.
echo 🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗
echo                 치킨마스터 웹 프로토타입 시작
echo 🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗🍗
echo.

echo 📁 현재 디렉토리: %CD%
echo 🐍 Python 버전 확인...
python --version
echo.

echo 📦 필요한 패키지 설치 확인...
pip list | findstr fastapi uvicorn
echo.

echo 🚀 서버 시작 중...
echo 📱 브라우저에서 http://localhost:8000 으로 접속하세요!
echo 🛑 서버 종료하려면 Ctrl+C를 누르세요.
echo.

python main.py

echo.
echo 서버가 종료되었습니다.
echo 아무 키나 누르면 창이 닫힙니다...
pause > nul 