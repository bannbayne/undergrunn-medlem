@echo off
cd /d "%~dp0"

:: Stopp eventuelle gamle instanser for ren oppstart
taskkill /F /IM cloudflared.exe >nul 2>nul
if exist server.pid (
    set /p OLDPID=<server.pid
    taskkill /F /PID %OLDPID% >nul 2>nul
    del /f /q server.pid >nul 2>nul
)

:: Start serveren 100% usynlig i bakgrunnen uten kommandovindu
where pythonw >nul 2>nul
if %errorlevel% equ 0 (
    start "" pythonw server.py --online
    exit
)

where pyw >nul 2>nul
if %errorlevel% equ 0 (
    start "" pyw server.py --online
    exit
)

:: Reserve-metode med PowerShell skjult vindu hvis pythonw ikke er i PATH
powershell -WindowStyle Hidden -Command "Start-Process python -ArgumentList 'server.py --online' -WindowStyle Hidden"
exit
