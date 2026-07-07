@echo off
title Dating Photo Checker Backend Server
echo =======================================================================
echo     DATING PHOTO CHECKER - FULL-STACK BACKEND SERVER
echo =======================================================================
echo.
echo [...] Se verifica si se instaleaza dependintele din requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Eroare la instalarea dependintelor. Asigura-te ca ai Python instalat corect.
    pause
)

echo.
echo [...] Pornire server FastAPI (uvicorn) pe http://127.0.0.1:8000...
start "Dating Checker Server" cmd /c "python server.py"
timeout /t 3 >nul

echo [...] Se deschide browserul web la adresa http://localhost:8000...
start http://localhost:8000
echo.
echo [SUCCESS] Serverul ruleaza cu succes pe adresa: http://localhost:8000
echo Apasa orice tasta pentru a opri serverul.
echo.
echo =======================================================================
pause >nul
taskkill /FI "WINDOWTITLE eq Dating Checker Server*" /F >nul 2>&1
echo [INFO] Serverul a fost oprit.
