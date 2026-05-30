# ComfyUI BATシステム設計資料
作成日: 2026-05-30  
対象環境: ComfyUI v0.11.1 / SSDポータブル運用

---

## ■ 目的

**「GPU環境では生成だけに集中できる状態を作る」**

GPU無し環境（自宅・移動中など）で以下をすべて完結させる：

- 環境構築・動作確認
- 生成プロンプトの作成・検証
- 出力先フォルダの事前準備
- ワークフローのテスト（JSONログで結果確認）

GPU有り環境（外出先PC接続時）では：

- プロンプトと設定は完成済み
- 保存先フォルダも作成済み
- **「生成を実行するだけ」の状態にする**

---

## ■ 期待する結果

| フェーズ | 環境 | やること |
|---------|------|---------|
| 準備フェーズ | GPU無し（CPU） | 環境構築・プロンプト作成・フォルダ準備・テストログ確認 |
| 生成フェーズ | GPU有り（外出先） | 生成実行のみ・指定フォルダへ自動保存 |

- 一括生成時、グループ（キャラ・差分・背景など）ごとに保存先フォルダを事前指定
- 生成結果が自動的に正しいフォルダへ振り分けられる
- 生成後の整理作業が不要な状態を目指す

---

## ■ 概要

本資料は、ComfyUI環境において以下を実現するためのBATシステム設計をまとめたものです。

- GPU用・CPU用の2本構成BAT
- 本番ワークフロー無傷のテスト運用
- テスト結果のJSONログ記録（画像出力なし）
- 出力先を `test_output\logs\` に強制固定

---

## ■ 要件まとめ

| 項目 | 内容 |
|------|------|
| BAT構成 | 2本（GPU用・CPU用） |
| venv | 共通（本番環境と同一） |
| テストログ形式 | JSONのみ（画像出力なし） |
| ログファイル管理 | 実行ごとに1ファイル |
| ステータス粒度 | success / error ＋ エラー時はメッセージも記録 |
| ログ記録内容 | プロンプト・seed・モデル名・パラメータ・タイムスタンプ・実行結果ステータス |
| 本番ワークフロー | 未定（後で決める） |
| 出力先固定 | `D:\ai\ComfyUI\test_output\logs\` のみ |

---

## ■ フォルダ構成

```
D:\ai\ComfyUI\
├── venv\                            ← 共通venv（GPU・CPU共用）
├── models\
│   ├── checkpoints\
│   ├── loras\
│   └── controlnet\
├── user\default\workflows\
│   ├── MyDailyDriverWorkflow_v1.2.json   ← 本番（触らない）
│   ├── txt2img_warkflow_v1.2.json        ← 本番（触らない）
│   └── [workflow名]_TEST.json            ← テスト用コピー（後で作成）
├── test_output\
│   └── logs\
│       ├── [timestamp]_test.json         ← 実行ごとに1ファイル
│       └── ...
├── launch_gpu.bat                   ← GPU用起動BAT（本番）
└── launch_cpu.bat                   ← CPU用起動BAT（テスト）
```

---

## ■ BATファイル設計

### launch_gpu.bat（GPU用・本番）

```bat
@echo off
chcp 65001
echo [GPU MODE] ComfyUI 起動中...

:: Git パス設定
set GIT=D:\MyTools\PortableGit\bin\git.exe

:: venv有効化
call D:\ai\ComfyUI\venv\Scripts\activate.bat

:: 依存パッケージ確認インストール
pip install GitPython requests librosa --quiet

:: ComfyUI起動（GPU・通常出力）
python D:\ai\ComfyUI\main.py

pause
```

---

### launch_cpu.bat（CPU用・テスト）

```bat
@echo off
chcp 65001
echo [CPU TEST MODE] ComfyUI 起動中...

:: Git パス設定
set GIT=D:\MyTools\PortableGit\bin\git.exe

:: venv有効化
call D:\ai\ComfyUI\venv\Scripts\activate.bat

:: 依存パッケージ確認インストール
pip install GitPython requests librosa --quiet

:: 出力先をtest_outputに強制固定
set COMFYUI_OUTPUT_DIR=D:\ai\ComfyUI\test_output

:: test_output\logsフォルダが存在しない場合は作成
if not exist "%COMFYUI_OUTPUT_DIR%\logs" mkdir "%COMFYUI_OUTPUT_DIR%\logs"

:: ComfyUI起動（CPU・テスト出力先固定）
python D:\ai\ComfyUI\main.py --cpu --output-directory %COMFYUI_OUTPUT_DIR%

pause
```

---

## ■ テスト用ワークフロー設定（本番との差分）

本番ワークフローをコピーし、以下の箇所のみ変更します。  
**本番JSONは一切触りません。**

| ノード | 本番設定 | テスト設定 |
|--------|---------|-----------|
| KSampler / steps | 20〜30 | **1〜2** |
| KSampler / cfg | 7.0 | **1.0** |
| 解像度 | 512〜1024px | **64×64px** |
| SaveImage ノード | 有効 | **削除または無効化** |
| 出力ノード | SaveImage | **PreviewText（テキスト確認用）** |

> ⚠️ テスト用ワークフローファイルは `[元ファイル名]_TEST.json` として保存すること。

---

## ■ JSONログ仕様

### ファイル命名規則

```
D:\ai\ComfyUI\test_output\logs\[YYYYMMDDHHmmss]_test.json
例: 20260530120000_test.json
```

### 成功時のJSON構造

```json
{
  "timestamp": "2026-05-30T12:00:00",
  "status": "success",
  "mode": "CPU_TEST",
  "model": "novaOrangeXL_v140",
  "prompt": "1girl, solo...",
  "negative_prompt": "bad hands...",
  "seed": 123456789,
  "steps": 1,
  "cfg": 1.0,
  "sampler": "euler",
  "scheduler": "normal",
  "resolution": "64x64",
  "workflow_file": "MyDailyDriverWorkflow_v1.2_TEST.json"
}
```

### エラー時のJSON構造

```json
{
  "timestamp": "2026-05-30T12:05:00",
  "status": "error",
  "mode": "CPU_TEST",
  "model": "novaOrangeXL_v140",
  "prompt": "1girl, solo...",
  "seed": 123456789,
  "workflow_file": "MyDailyDriverWorkflow_v1.2_TEST.json",
  "error_message": "RuntimeError: CUDA not available / model load failed..."
}
```

---

## ■ venv共通運用の注意点

venvはGPU・CPU共通で使用します。  
torchはGPU環境用（CUDA版）のものがインストール済みのため、  
**CPU環境ではtorchのCPUフォールバック動作となります。**

| 環境 | torch動作 |
|------|----------|
| GPU（外出先PC） | CUDA版torch → GPU生成 |
| CPU（GPU無しPC） | 同じtorchがCPUフォールバック → CPU生成（低速） |

> ⚠️ テスト用途（steps=1・64×64）であればCPUフォールバックでも実用的な速度で動作します。

---

## ■ 一括生成用：出力フォルダ構成

GPU有り環境での生成前に、CPU環境でフォルダを事前作成しておく。  
生成時はワークフロー内の保存先ノードで対象フォルダを指定するだけでよい。

```
D:\ai\ComfyUI\output\
├── chara\                    ← キャラ立ち絵
│   ├── [キャラ名]\
│   │   ├── base\             ← 通常立ち絵
│   │   ├── diff\             ← 差分（表情・衣装など）
│   │   └── pose\             ← ポーズ差分
├── bg\                       ← 背景素材
│   ├── indoor\
│   └── outdoor\
├── tile\                     ← タイル素材
├── pixel\                    ← ピクセル素材
├── ui\                       ← UIパーツ
└── test_output\
    └── logs\                 ← テストJSONログ
```

> 📌 フォルダ構成はプロジェクト・用途に応じて変更可。  
> CPU環境でフォルダだけ先に作っておき、GPU環境では生成＆保存のみに集中する。

---

## ■ フォルダIndexファイル（FUTURE）

> ⚠️ **将来実装予定**：カラム定義が固まった時点で正式設計する。

各出力フォルダに `_index.json`（またはCSV）を置き、  
チェック表＋目次の役割を持たせる構想。

### 想定する役割

- フォルダ内のファイル一覧をインデックス化
- 生成済み・未生成・要再生成のチェック状態を管理
- ワークフローや保存先パスの参照元として使用

### 現時点で想定しているカラム候補

| カラム名 | 内容 | 状態 |
|---------|------|------|
| `file_name` | ファイル名 | 確定 |
| `dict` | 説明・用途メモ | 確定 |
| `path` | 保存先フルパス | 確定 |
| `scale` | 解像度・スケール情報 | 確定 |
| （その他） | 未定 | **検討中** |

### 想定するファイル形式（仮）

```json
[
  {
    "file_name": "chara_alice_base_001.png",
    "dict": "アリス通常立ち絵 正面",
    "path": "D:\\ai\\ComfyUI\\output\\chara\\alice\\base\\chara_alice_base_001.png",
    "scale": "512x768",
    "status": "generated"
  }
]
```

> 📝 カラム定義・ファイル形式（JSON or CSV）・自動生成スクリプトは  
> **カラムが固まった段階で別資料として設計する。**

---

## ■ 今後の作業ステップ

**CPU環境（準備フェーズ）**
- [ ] `launch_cpu.bat` 作成・テスト
- [ ] `launch_gpu.bat` 現行BATをリファクタリング
- [ ] 出力フォルダ構成を作成（`output\` 以下）
- [ ] テスト用ワークフローJSON作成（本番ワークフロー決定後）
- [ ] ログ出力カスタムノード or スクリプト設計
- [ ] `test_output\logs\` フォルダ運用確認

**GPU環境（生成フェーズ）**
- [ ] 保存先フォルダ指定の動作確認
- [ ] 一括生成ワークフローの動作確認

**FUTURE（将来実装）**
- [ ] フォルダIndexファイルのカラム定義を確定
- [ ] `_index.json` 自動生成スクリプト設計
- [ ] IndexをCSV出力してExcel管理と連携する構成検討

---

## ■ 参考：現在の環境構成サマリ

| 項目 | 内容 |
|------|------|
| ComfyUI | v0.11.1（最新: v0.22.0） |
| ルートパス | `D:\ai\ComfyUI` |
| 起動方式 | BAT経由必須（venv + PortableGit） |
| GPU | 外出先PC接続（スペック未計測） |
| LoRA | Qwen系2本 + granblue-klein 1本 |
| Checkpoint | XL系 / PixelArt / ACE-Step |
| 用途 | ゲーム素材・立ち絵量産・音楽生成 |

---

*最終更新: 2026-05-30*
