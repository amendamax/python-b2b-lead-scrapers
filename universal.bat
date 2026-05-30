@echo off
:: Verifică dacă avem deja drepturi de administrator
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if '%errorlevel%' NEQ '0' (
    :: Dacă nu suntem admin, cerem ridicarea privilegiilor
    echo Cerere drepturi de administrator...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    :: Aici ne asigurăm că terminalul rămâne în folderul curent
    pushd "%~dp0"
    
    :: Deschide terminalul și îl lasă deschis pentru comenzi
    cmd /k