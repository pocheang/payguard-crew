@echo off
echo ========================================
echo  PayGuard Crew - Complete Demo
echo ========================================
echo.

echo [1/3] Installing dependencies...
pip install email-validator >nul 2>&1

echo [2/3] Starting backend server...
start "PayGuard Backend" cmd /k "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo [3/3] Waiting for server to start...
timeout /t 5 /nobreak >nul

echo [4/3] Opening frontend...
start frontend\index.html

echo.
echo ========================================
echo  Demo Started Successfully!
echo ========================================
echo.
echo Backend:  http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo Frontend: Opening in browser...
echo.
echo Press any key to stop the servers...
pause >nul

taskkill /FI "WINDOWTITLE eq PayGuard Backend*" /T /F >nul 2>&1
echo.
echo Servers stopped. Goodbye!
