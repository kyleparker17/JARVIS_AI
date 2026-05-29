@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ========================================
echo   JARVIS v7
echo   Multi-Agent Edition (24B Orchestrator)
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [오류] 가상환경(.venv)이 없습니다.
    echo.
    echo 먼저 다음 명령을 실행하세요:
    echo   python -m venv .venv
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo 가상환경 활성화 중...
call ".venv\Scripts\activate.bat" >nul 2>&1

echo.
echo JARVIS v7 시작 중...
echo 브라우저가 곧 열립니다.
echo.

".venv\Scripts\python.exe" -m streamlit run app.py

echo.
echo 종료하려면 아무 키나 누르세요.
pause >nul
