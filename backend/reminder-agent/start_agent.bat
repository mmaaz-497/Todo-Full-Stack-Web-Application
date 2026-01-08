@echo off
REM Reminder Agent Startup Script
REM This script starts the reminder agent in the background

echo ========================================
echo Starting AI Task Reminder Agent
echo ========================================

REM Kill any existing reminder agent processes
echo Stopping existing agent processes...
taskkill /F /FI "WINDOWTITLE eq Reminder Agent*" 2>nul
timeout /t 2 /nobreak >nul

REM Start the agent in a new window
echo Starting agent...
start "Reminder Agent" /MIN cmd /c "cd /d %~dp0 && venv\Scripts\python.exe main.py > logs\agent-output.log 2>&1"

REM Wait a moment for startup
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Agent started successfully!
echo ========================================
echo.
echo Log file: logs\agent-output.log
echo To view logs: tail -f logs\agent-output.log
echo.
echo The agent will check for reminders every 5 minutes.
echo.

pause
