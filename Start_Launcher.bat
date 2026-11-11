@echo off
setlocal
cd /d "%~dp0"
title Blodig oktober - Meny Launcher

where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [FEIL] Python ble ikke funnet pa datamaskinen!
        pause
        exit /b 1
    )
    py launcher.py
    pause
    exit /b 0
)

python launcher.py
pause
