@echo off
title S Quiz by Sai - Premium Edition
color 0B

echo.
echo ============================================================
echo            S QUIZ by SAI - PREMIUM EDITION
echo ============================================================
echo.
echo Branding:
echo   [S] Logo - Floating Brand
echo   App Name: S Quiz
echo   Author: Sai
echo.
echo Features:
echo   - Custom Question Count (1-100)
echo   - Premium UI with Animations
echo   - Motivational Quotes
echo   - AI Teacher Tools
echo.
echo Starting standalone application...
echo.

python premium_desktop_app.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start the application
    echo.
    echo Possible solutions:
    echo 1. Install dependencies: pip install -r requirements.txt
    echo 2. Check if secrets.json has your API key
    echo.
    pause
)
