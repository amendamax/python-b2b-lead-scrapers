@echo off
:: Verifică dacă scriptul rulează cu drepturi de administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :gotAdmin
) else (
    goto :elevate
)

:elevate
echo [>] Cerere drepturi de administrator (UAC)...
powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit /B

:gotAdmin
:: Schimbă directorul curent la folderul unde se află acest script .bat
cd /d "%~dp0"
title Terminal Dezvoltare (ADMIN) - %~nx0
cls
echo =======================================================================
echo   💻 TERMINAL DE DEZVOLTARE AMING-BORG (MOD ADMINISTRATOR)
echo =======================================================================
echo.
echo   Director Proiect: %CD%
echo   Status Privilegii: Elevat (Administrator)
echo.
echo   Poti rula comenzi de sistem, instalari de pachete sau configurari.
echo   Tasteaza 'exit' pentru a inchide acest terminal.
echo.
echo =======================================================================
echo.
cmd /k
