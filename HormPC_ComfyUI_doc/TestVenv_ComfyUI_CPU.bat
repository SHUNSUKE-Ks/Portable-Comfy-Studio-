@echo off
REM ===== ComfyUI CPU Mode Launcher =====
REM Uses separate virtual environment (venv)
REM Separate environment from GPU version - isolated dependencies

cd /d D:\ai\ComfyUI

if errorlevel 1 (
    echo Failed to change directory to ComfyUI folder.
    pause
    exit /b
)

if not exist venv\Scripts\activate.bat (
    echo Virtual environment not found. Please check setup.
    pause
    exit /b
)

call venv\Scripts\activate

echo Launching ComfyUI in CPU mode...
echo +Using separate venv environment
python main.py --cpu
pause
