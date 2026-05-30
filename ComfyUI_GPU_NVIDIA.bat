@echo off
chcp 65001 >nul
title Portable Comfy Studio - GPU (本番生成)

:: BAT自身の場所へ移動（ドライブレター非依存＝相対パス必須の要件を満たす）
cd /d "%~dp0"

echo ============================================================
echo  [GPU MODE] ComfyUI 起動中 ... venv環境で本番生成
echo ============================================================

:: venv 確認（python_embeded は使わない。venv に一本化）
if not exist "ComfyUI\venv\Scripts\activate.bat" (
    echo [ERROR] venv が見つかりません: %~dp0ComfyUI\venv
    echo         このSSD上の venv が必要です。
    pause
    exit /b 1
)
call "ComfyUI\venv\Scripts\activate.bat"

:: ComfyUI 起動（GPU=デフォルト。--cpu は付けない＝GPUがあれば自動でGPU使用）
cd ComfyUI
python main.py --windows-standalone-build

echo.
echo ------------------------------------------------------------
echo ComfyUI が起動しない場合:
echo  - NVIDIAドライバを最新に更新してください
echo  - c10.dll エラーが出る場合は VC再頒布可能パッケージをインストール:
echo      https://aka.ms/vc14/vc_redist.x64.exe
echo ------------------------------------------------------------
pause
