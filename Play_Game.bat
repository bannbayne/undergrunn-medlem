@echo off
setlocal
cd /d "%~dp0"
title Medlem - Norsk Autotune Spillet Launcher
echo ========================================================
echo   Starter Medlem - Norsk Autotune Spillet...
echo ========================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [FEIL] Python ble ikke funnet pa datamaskinen!
        pause
        exit /b 1
    )
    py server.py
    pause
    exit /b 0
)

python server.py
pause
