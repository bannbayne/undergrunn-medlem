@echo off
cd /d "%~dp0"
title Medlem (lokal)
where python >nul 2>nul
if %errorlevel% neq 0 (set PY=py) else (set PY=python)
%PY% medlem_server.py
pause
