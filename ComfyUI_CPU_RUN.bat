@echo off
title Portable Comfy Studio - CPU RUN
cd /d "%~dp0ComfyUI"

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] venv not found: %~dp0ComfyUI\venv
    pause
    exit /b 1
)
call "venv\Scripts\activate.bat"

echo.
echo Starting ComfyUI in CPU mode. Loading nodes takes 1-2 minutes...
echo Your browser will open at http://127.0.0.1:8188
echo Press Ctrl+C or close this window to stop.
echo.

python main.py --cpu --auto-launch

pause
