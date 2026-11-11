@echo off
setlocal
echo ========================================================
echo   Blodig oktober - Norsk Autotune Hotel
echo   Launching Unreal Engine 5.8 Project...
echo ========================================================

set "UE_EDITOR=C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
set "PROJECT=%~dp0BlodigOktober\BlodigOktober.uproject"

if not exist "%UE_EDITOR%" (
    echo [ERROR] Could not find Unreal Engine 5.8 at:
    echo "%UE_EDITOR%"
    pause
    exit /b 1
)

if not exist "%PROJECT%" (
    echo [ERROR] Could not find project file at:
    echo "%PROJECT%"
    pause
    exit /b 1
)

echo Starting Unreal Editor 5.8 with BlodigOktober...
start "" "%UE_EDITOR%" "%PROJECT%"
echo Done! Unreal Editor is loading the project in the background.
