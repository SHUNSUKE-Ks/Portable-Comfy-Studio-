# 設計メモ — ComfyUI バージョンアップ方針（v0.11.1 → v0.22.0）

作成日: 2026-05-30

---

## ■ 結論（先に）

1. **ComfyUI本体の更新は「安全に試せる」**。ComfyUIは git リポジトリ（現 v0.11.1）なので、
   壊れても `git checkout v0.11.1` で**確実に戻せる**。
2. **ただし PyTorch を cu130（CUDA 13）へ更新するのは“今はやらない／本体更新と分離／延期”** を強く推奨。
   これは本体更新より遥かにリスクが高く、しかも**必須ではない**。
3. 更新後は、今回作った**準備フェーズのツール（CPU検証・起動・ログ）で家で検証**してから出先GPU機へ。

---

## ■ 確認した事実（推測でなく実機）

| 項目 | 値 |
|------|----|
| ComfyUI | **gitリポジトリ**。現 v0.11.1（commit b0d97089, 2026-01-29）。origin=comfyanonymous/ComfyUI |
| PyTorch | `2.5.1+cu121`（CUDA 12.1） |
| requirements.txt の torch | **版指定なし（`torch` のみ）** → v0.22 は基本、現行torchでも動く想定 |
| GPU機のスペック/ドライバ | **未計測・不明**（= cu130 が動く保証なし） |

---

## ■ リスク評価

| 変更 | リスク | 戻せるか | 推奨 |
|------|--------|---------|------|
| ComfyUI本体 v0.11→v0.22 | 中（11バージョンのジャンプ。カスタムノード互換が主リスク） | ✅ git で戻せる | **段階的にやってよい** |
| `pip install -r requirements.txt`（本体付随の依存更新） | 中（一部パッケージが上がる） | △ pip freeze で戻せる | 事前バックアップ必須 |
| **PyTorch → 2.9/cu130** | **高**（GPU機ドライバ依存・全カスタムノードがtorch2.5前提・再ビルド連鎖） | △ freezeで戻せるが重い | **今はやらない・延期** |
| カスタムノード一括更新 | 中〜高（rgthreeはNode2.0非互換を警告済。deprecation多数） | ノードによる（git版のみ） | 更新後に1件ずつ確認 |

---

## ■ 推奨手順（段階的・各段で戻せる）

> ⚠️ 各操作は**人間確認後**。venv変更前に必ずバックアップ。

**Step 0｜バックアップ（戻れる状態を作る）**
- `cd D:\ai\ComfyUI\venv\Scripts && python -m pip freeze > ..\..\..\01‗ConfyUI_WorkSpace\Report\test_logs\requirements_BEFORE_2026-05-30.txt`
- 現タグを記録（v0.11.1）。可能なら venv フォルダを zip 退避。

**Step 1｜本体だけ更新（torchは触らない）**
- `cd D:\ai\ComfyUI`
- `git fetch --tags`
- `git checkout v0.22.0`  ← コードだけ切替。**torchは現状維持**。

**Step 2｜本体付随の依存だけ更新**
- `git\PortableGit経由のpip` で `pip install -r requirements.txt`
- ※ここで torch を cu130 に上げるコマンドは**打たない**。

**Step 3｜家で検証（今回のツールで・グラボ不要）**
- `ComfyUI_CPU_TEST.bat`（import/ノード/モデル検証）
- `ComfyUI_CPU_RUN.bat`（UIが起動するか）
- `ComfyUI_WORKFLOW_LOG.bat`（主要ワークフローの設定が壊れてないか）
- 重点テスト: greenback系 / i2i_workflow / MyDailyDriverWorkflow

**Step 4｜壊れたカスタムノードの対応**
- ComfyUI-Manager で互換チェック・更新。直らない物は `.disabled` で一旦無効化。
- ※使うワークフロー（greenback）は**コアのみ**なので、最悪カスタムノードが全滅しても生成は可能。

**Step 5｜PyTorchは別件として後日判断**
- 前提: ①出先GPU機のドライバがCUDA13対応か確認 ②速度改善の実測ニーズがあるか
- 両方Yesになるまで torch は `2.5.1+cu121` のまま。

**ロールバック条件と方法**
- UIが起動しない／主要ワークフローが壊れた → `git checkout v0.11.1` ＋ `pip install -r requirements.txt`（または freeze 復元 / zip戻し）。

---

## ■ そもそも今やるべきか（コスト/ベネフィット）

- 現環境は**あなたの用途（立ち絵量産）で既に動く**。新機能（CogVideoX動画/Stable Audio/Gemma4等）は立ち絵に不要。
- メリットは主に「BiRefNet標準搭載で rembg系カスタムノードを整理できるかも」程度の付加価値。
- → **緊急性は低い**。やるなら**急がず・バックアップ前提で段階的に**。現状維持（v0.11.1）も十分アリ。

---

## ■ あなたの判断が要る点（未決）

- [ ] 本体更新を実行するか（推奨: Step0〜4を一緒にやる。torchは据え置き）
- [ ] torch更新は延期でよいか（推奨: 延期。GPU機ドライバ確認が先）
- [ ] バックアップに venv の zip 退避までやるか（容量と相談）

> 注: 添付の比較表（別AI作成と思われる）の個別バージョン（Gemma4 / torch 2.9.1 等）は本メモでは未検証。
> ただし「段階的・バックアップ・torch分離・家で検証」という方針は版番号に関わらず有効。
