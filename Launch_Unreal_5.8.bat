@echo off
setlocal
cd /d "%~dp0"
echo ========================================================
echo   Starter Unreal Engine 5.8 Prosjekt: BlodigOktober
echo ========================================================
set "UE_EDITOR=C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
set "PROJECT=%~dp0BlodigOktober\BlodigOktober.uproject"

if not exist "%UE_EDITOR%" (
    echo [FEIL] Fant ikke Unreal Engine 5.8 på:
    echo "%UE_EDITOR%"
    pause
    exit /b 1
)

start "" "%UE_EDITOR%" "%PROJECT%"
echo Unreal Editor 5.8 starter...
