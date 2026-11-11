@echo off
cd /d "%~dp0"
title Last opp til GitHub for 24/7 Hosting

echo ======================================================================
echo   UNDERGRUNN MEDLEM - LASTER OPP TIL GITHUB
echo ======================================================================
echo.
echo Mal: https://github.com/bannbayne/undergrunn-medlem.git
echo.
git remote remove origin 2>nul
git remote add origin https://github.com/bannbayne/undergrunn-medlem.git
git branch -M main

echo Laster opp filene til GitHub...
echo (Hvis et lite innloggingsvindu dukker opp, trykk 'Sign in with your browser')
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo   SUKSESS! Koden er lastet opp til GitHub!
    echo.
    echo   Render bygger og gjor spillet ditt tilgjengelig pa:
    echo   👉 https://undergrunn-medlem.onrender.com/
    echo ======================================================================
) else (
    echo.
    echo Noe gikk galt. Sjekk at du er logget inn pa GitHub.
)

echo.
pause
