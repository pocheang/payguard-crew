@echo off
echo Installing missing dependencies...
pip install email-validator

echo.
echo Starting PayGuard Crew server...
echo Server will be available at: http://127.0.0.1:8000
echo Swagger UI: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
