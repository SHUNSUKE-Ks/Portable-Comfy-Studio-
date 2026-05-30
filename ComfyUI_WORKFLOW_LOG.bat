@echo off
title Portable Comfy Studio - Workflow to JSON Log (no image)
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

set "COMFY_DIR=%~dp0ComfyUI"

rem Workspace folder name has a special char; find via wildcard to keep BAT pure-ASCII
set "WORKSPACE="
for /d %%D in ("%~dp001*ConfyUI_WorkSpace") do set "WORKSPACE=%%D"
if not defined WORKSPACE (
    echo [ERROR] workspace folder not found under %~dp0
    pause
    exit /b 1
)

set "PY=%COMFY_DIR%\venv\Scripts\python.exe"
set "SCRIPT=%WORKSPACE%\50_batch\tools\comfyui_workflow_to_log.py"
set "WORKFLOW_DIR=%COMFY_DIR%\user\default\workflows"
set "LOG_DIR=%WORKSPACE%\Report\test_logs"

if not exist "%PY%" (
    echo [ERROR] python not found: %PY%
    pause
    exit /b 1
)
if not exist "%SCRIPT%" (
    echo [ERROR] script not found: %SCRIPT%
    pause
    exit /b 1
)
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo Extracting workflow parameters to JSON (no image, no ComfyUI launch)...
"%PY%" "%SCRIPT%" --workflow-dir "%WORKFLOW_DIR%" --log-dir "%LOG_DIR%" --mode CPU_TEST_PARAMS

echo.
echo Logs: %LOG_DIR%
pause
