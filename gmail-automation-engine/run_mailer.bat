@echo off
TITLE Gmail Automation Engine - 24/7 Windows Watchdog Service
COLOR 0A

:: Set working directory to script location
cd /d "%~dp0"

echo ================================================================================
echo   GMAIL MULTI-ACCOUNT AUTOMATION ENGINE - 24/7 WINDOWS WATCHDOG LAUNCHER        
echo ================================================================================
echo.
echo Checking Python environment...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    COLOR 0C
    echo [ERROR] Python 3 is not found in system PATH.
    echo Please install Python 3.10+ and check 'Add Python to PATH' during installation.
    pause
    exit /b 1
)

echo Python is installed and verified.
echo.
echo Starting 24/7 continuous supervisor loop...
echo To stop the engine gracefully, press Ctrl+C or close this window.
echo ================================================================================
echo.

:WATCHDOG_LOOP
echo [%DATE% %TIME%] [SUPERVISOR] Launching Gmail Automation Engine (main.py)...
python main.py

set EXIT_CODE=%ERRORLEVEL%
echo.
echo [%DATE% %TIME%] [SUPERVISOR] Engine stopped with exit code: %EXIT_CODE%

if %EXIT_CODE% EQU 0 (
    echo [%DATE% %TIME%] [SUPERVISOR] Work queue completed cleanly. 
    echo [%DATE% %TIME%] [SUPERVISOR] Sleeping for 60 seconds before next queue cycle...
    timeout /t 60 /nobreak >nul
) else (
    COLOR 0E
    echo [%DATE% %TIME%] [WARNING] Engine encountered an unexpected exit (%EXIT_CODE%).
    echo [%DATE% %TIME%] [SUPERVISOR] Initiating self-healing auto-restart in 10 seconds...
    timeout /t 10 /nobreak >nul
    COLOR 0A
)

goto WATCHDOG_LOOP
