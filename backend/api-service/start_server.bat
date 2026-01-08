@echo off
echo Starting Todo AI Chatbot Backend...
echo.
echo ========================================
echo Backend Server Starting...
echo ========================================
echo.
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
