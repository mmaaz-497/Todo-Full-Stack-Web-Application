@echo off
REM Reminder Agent Stop Script

echo Stopping AI Task Reminder Agent...
taskkill /F /FI "WINDOWTITLE eq Reminder Agent*" 2>nul

if %ERRORLEVEL% EQU 0 (
    echo Agent stopped successfully!
) else (
    echo No agent process found running.
)

pause
