@echo off
cd /d "%~dp0"
title Stopp Undergrunn Medlem

echo Stopper Undergrunn Medlem server og tunnel...
taskkill /F /IM cloudflared.exe >nul 2>nul

if exist server.pid (
    set /p SPID=<server.pid
    taskkill /F /PID %SPID% >nul 2>nul
    del /f /q server.pid >nul 2>nul
)

powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*server.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>nul

echo.
echo Alt er na stoppet!
timeout /t 2 >nul
exit
