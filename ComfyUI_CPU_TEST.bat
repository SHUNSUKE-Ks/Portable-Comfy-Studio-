@echo off
title Portable Comfy Studio - CPU TEST (validate only, no image)
set PYTHONDONTWRITEBYTECODE=1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

set "COMFY_DIR=%~dp0ComfyUI"

rem Workspace folder name contains a special char; find it via wildcard to keep this BAT pure-ASCII
set "WORKSPACE="
for /d %%D in ("%~dp001*ConfyUI_WorkSpace") do set "WORKSPACE=%%D"
if not defined WORKSPACE (
    echo [ERROR] workspace folder not found under %~dp0
    pause
    exit /b 1
)

set "VALIDATOR=%WORKSPACE%\50_batch\tools\comfyui_test_validate.py"
set "WORKFLOW_DIR=%COMFY_DIR%\user\default\workflows"
set "LOG_DIR=%WORKSPACE%\Report\test_logs"

if not exist "%COMFY_DIR%\venv\Scripts\activate.bat" (
    echo [ERROR] venv not found: %COMFY_DIR%\venv
    pause
    exit /b 1
)
call "%COMFY_DIR%\venv\Scripts\activate.bat"

if not exist "%VALIDATOR%" (
    echo [ERROR] validator not found: %VALIDATOR%
    pause
    exit /b 1
)

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo Running validation (no image generation)...
python "%VALIDATOR%" --comfy-dir "%COMFY_DIR%" --workflow-dir "%WORKFLOW_DIR%" --log-dir "%LOG_DIR%" --mode CPU_TEST
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (echo Validation OK) else (echo Validation reported errors - see JSON log)
echo Logs: %LOG_DIR%
pause
