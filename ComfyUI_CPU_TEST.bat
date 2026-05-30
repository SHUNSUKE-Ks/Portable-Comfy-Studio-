@echo off
chcp 65001 >nul
title ComfyUI CPU TEST (検証のみ・画像生成なし)

echo ============================================================
echo  [CPU TEST MODE] ComfyUI 検証 ... 画像生成なし / 負荷ゼロ志向
echo ============================================================

:: ---- パス設定 ----
set "COMFY_DIR=D:\ai\ComfyUI"
set "WORKSPACE=D:\ai\01‗ConfyUI_WorkSpace"
set "VALIDATOR=%WORKSPACE%\50_batch\tools\comfyui_test_validate.py"
set "WORKFLOW_DIR=%COMFY_DIR%\user\default\workflows"
set "LOG_DIR=%WORKSPACE%\Report\test_logs"

:: ComfyUI内に __pycache__ を作らない（フォルダを汚さない）
set PYTHONDONTWRITEBYTECODE=1
:: 出力をUTF-8に（パスの特殊文字対策）
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

:: ---- venv 確認 ----
if not exist "%COMFY_DIR%\venv\Scripts\activate.bat" (
    echo [ERROR] venv が見つかりません: %COMFY_DIR%\venv
    echo         先に venv セットアップを確認してください。
    pause
    exit /b 1
)
call "%COMFY_DIR%\venv\Scripts\activate.bat"

:: ---- 検証スクリプト確認 ----
if not exist "%VALIDATOR%" (
    echo [ERROR] 検証スクリプトが見つかりません: %VALIDATOR%
    pause
    exit /b 1
)

:: ---- ログフォルダ作成 ----
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: ---- 検証実行 ----
python "%VALIDATOR%" --comfy-dir "%COMFY_DIR%" --workflow-dir "%WORKFLOW_DIR%" --log-dir "%LOG_DIR%" --mode CPU_TEST
set "RC=%ERRORLEVEL%"

echo.
echo ------------------------------------------------------------
if "%RC%"=="0" (
    echo  検証 OK ^(status: success/warning^)
) else (
    echo  検証 NG ^(status: error^) -- 上のサマリと JSON ログを確認
)
echo  ログ出力先: %LOG_DIR%
echo ------------------------------------------------------------
pause
