@echo off
title Portable Comfy Studio - GPU
cd /d "%~dp0ComfyUI"

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] venv not found: %~dp0ComfyUI\venv
    pause
    exit /b 1
)
call "venv\Scripts\activate.bat"

echo.
echo Starting ComfyUI (GPU mode)...
echo.

python main.py --windows-standalone-build

echo.
echo If ComfyUI did not start:
echo  - Update your NVIDIA drivers to the latest version
echo  - For a c10.dll error, install VC redist: https://aka.ms/vc14/vc_redist.x64.exe
pause
