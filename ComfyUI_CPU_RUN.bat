@echo off
chcp 65001 >nul
title Portable Comfy Studio - CPU RUN (動作確認用・低速)

:: BAT自身の場所へ移動（ドライブレター非依存）
cd /d "%~dp0"

echo ============================================================
echo  [CPU MODE] ComfyUI 起動中 ... グラボなし動作確認用
echo  （生成は非常に低速。UI/動作チェック用です）
echo ============================================================

if not exist "ComfyUI\venv\Scripts\activate.bat" (
    echo [ERROR] venv が見つかりません: %~dp0ComfyUI\venv
    pause
    exit /b 1
)
call "ComfyUI\venv\Scripts\activate.bat"

cd ComfyUI
echo.
echo 起動には1〜2分かかります（全ノード読込のため）。
echo 起動後、ブラウザで自動的に http://127.0.0.1:8188 が開きます。
echo  ※一部カスタムノードのimport警告が出ますが、コア機能は動作します。
echo 終了するには このウィンドウで Ctrl+C を押すか、ウィンドウを閉じてください。
echo.

:: CPUモードで起動。--auto-launch でブラウザを自動で開く
python main.py --cpu --auto-launch

pause
