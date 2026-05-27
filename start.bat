@echo off
chcp 65001 >nul
cd /d %~dp0

echo ========================================
echo   베리파이 AI (Verify AI) 실행
echo ========================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 존재하지 않습니다.
    echo 먼저 다음 명령을 실행하세요:
    echo.
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b
)

echo 가상환경 활성화 중...
call .venv\Scripts\activate.bat

echo.
echo 베리파이 AI를 시작합니다...
echo 브라우저가 자동으로 열립니다.
echo.

python -m streamlit run app.py

pause
