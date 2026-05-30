# ComfyUI WorkSpace 索引書（INDEX）

- 作成日: 2026-05-30
- 役割: 人間（あなた）とAIエージェント双方のための「どこに何があり、いつアクセスするか」の地図
- 凡例: **Title**=名称 / **Dict**=どんな時にここを使うか / **Path**=場所
- 使い方: 迷ったらまずこのファイルを開く。各行の Dict を見て、該当する Path へ飛ぶ。

> このINDEXは「環境の現状」の索引です。生成物（agent/プロンプト集/CSV等）が増えたら §A の新構成に追記していきます。

---

## A. WorkSpace 新フォルダ構成（✅ 2026-05-30 作成済み）

`D:\ai\01‗ConfyUI_WorkSpace` 配下に以下を新設済み。

```
01‗ConfyUI_WorkSpace\
├── doc\                      既存。依頼書・環境資料など「人間向け原文」
├── Report\                   既存。本INDEX・各種レポート（ここ）
│   ├── INDEX.md              ← この索引書（常に最新の入口）
│   └── 01_環境探索レポート_2026-05-30.md
│
├── 10_manual\                【フェーズ1】人間向け指示書・運用マニュアル(.md)
├── 20_agents\                【フェーズ2】AI向けagent定義(.json / コメント付き.js)
│   ├── _manager\             ComfyUI専属Manager（司令塔）
│   └── tachie_diff\          立ち絵・差分agent（最初の1体）
├── 30_workflows\             整理済みworkflow(.json)。カテゴリ別
│   ├── tachie\               立ち絵・差分
│   ├── pixel\                ピクセル素材
│   ├── style\                スタイル別(水彩/neon等)
│   └── audio\                音楽(ACE-Step)
├── 40_prompts\               プロンプト集(.json / .md)。スタイル別
├── 50_batch\                 一括生成用 CSV / JSON とスクリプト
│   ├── schemas\              入力スキーマ定義(JSON Schema)
│   └── jobs\                 実依頼ファイル置き場
└── 60_external_request\      【フェーズ4】外部依頼マニュアル＋スキーマ＋検証
```

> 命名規則: 数字接頭辞でフェーズ/用途順に並べる。`_`始まりは「共通/親」。

---

## B. ComfyUI 本体ナビ（`D:\ai\ComfyUI`）

| Title | Dict（いつ使う） | Path |
| ---- | ---- | ---- |
| ComfyUI ルート | 全ての起点。BAT・main.py がある | `D:\ai\ComfyUI\` |
| Run_CPU.bat | **このCPU機で起動する時**（GPU未使用） | `D:\ai\ComfyUI\Run_CPU.bat` |
| main.py | 起動本体（直叩き禁止・BAT経由） | `D:\ai\ComfyUI\main.py` |
| venv | Python実行環境。pip操作はここをactivate | `D:\ai\ComfyUI\venv\` |
| venv activate | パッケージ追加/確認/freeze する時 | `D:\ai\ComfyUI\venv\Scripts\activate.bat` |
| requirements.txt | 本体が要求する依存を確認する時 | `D:\ai\ComfyUI\requirements.txt` |
| バージョン確認 | ComfyUI本体のバージョンを知りたい時 | `D:\ai\ComfyUI\comfyui_version.py`（=v0.11.1） |
| extra_model_paths | 外部モデルフォルダを追加したい時（雛形） | `D:\ai\ComfyUI\extra_model_paths.yaml.example` |
| API URL | スクリプトから生成投入する時の接続先 | `http://127.0.0.1:8188` |

---

## C. モデル索引（`D:\ai\ComfyUI\models`）

| Title | Dict（いつ使う） | Path |
| ---- | ---- | ---- |
| checkpoints | ベースモデル選択時 | `models\checkpoints\` |
| └ novaOrangeXL_v140 | 汎用XL / 立ち絵差分の標準ベース | 同上 |
| └ pixelArtSpriteDiffusion | ピクセル素材生成 | 同上 |
| └ waiIllustriousSDXL_v120 | Illustrious系アニメ | 同上 |
| └ retro_scifi_artstyle_illustriousXL | レトロSF調 | 同上 |
| └ ace_step_v1_3.5b | 音楽/BGM生成 | 同上 |
| loras | スタイル/キャラ味付け時 | `models\loras\` |
| └ granblue-klein9b | グラブル風キャラ（立ち絵差分で使用中） | 同上 |
| └ Qwen-Edit-2509-Multiple-angles | 多角度視点生成 | 同上 |
| └ Qwen-Image-Edit-...Lightning-4steps | 高速4step生成 | 同上 |
| └ watercolor_v1_sdxl | 水彩スタイル | 同上 |
| └ Anime neon-contrast SDXL | ネオン/高コントラスト | 同上 |
| └ vn_bg | ビジュアルノベル背景 | 同上 |
| └ Arri_MJ-illustriousXL_v01 | MJ風Illustrious | 同上 |
| controlnet | ポーズ/輪郭/奥行/タイル制御時 | `models\controlnet\` |
| └ openpose / canny / depth / tile / scribble / inpaint | 各SD1.5系制御 | 同上(.pth) |
| └ SDXL\controlnet-openpose-sdxl-1.0 | SDXLでポーズ制御する時 | `models\controlnet\SDXL\` |
| vae | VAE指定が要る時 | `models\vae\`（ae / qwen_image_vae） |
| embeddings | （未導入）今後追加時 | `models\embeddings\` |
| upscale_models | （未導入）ultimateSDupscale使う時に要追加 | `models\upscale_models\` |

---

## D. Custom Nodes 索引（`D:\ai\ComfyUI\custom_nodes`）

| Title | Dict（いつ使う） | 状態 |
| ---- | ---- | ---- |
| ComfyUI-Manager (v3.39.2) | ノードのインストール/更新管理 | 稼働 |
| ComfyUI-Easy-Use | ワークフロー効率化ノード | 稼働 |
| rgthree-comfy | UI/制御フロー拡張 | 稼働 |
| comfyui-custom-scripts | UI拡張（補完等） | 稼働 |
| efficiency-nodes-comfyui | 効率化ノード群 | 稼働 |
| ComfyUI-Crystools | パフォーマンス計測 | 稼働 |
| comfyui-image-saver | 画像保存拡張（メタ付き） | 稼働 |
| ComfyUI-qwenmultiangle | Qwen多角度生成 | ⚠️transformers5系で要確認 |
| comfyui_controlnet_aux | ControlNet前処理(openpose等) | ⚠️transformers5系で要確認 |
| comfyui_ultimatesdupscale | 高解像度アップスケール | upscale_model要追加 |
| ComfyUI_Jags_Audiotools | 音声ツール | 稼働 |
| batchimg-rembg-comfyui-nodes | バッチ背景除去 | 稼働 |
| rembg-comfyui-node / -better | 背景除去 | 稼働 |
| vnccs | **用途未確定（要調査）** | ❓ |
| websocket_image_save.py | WebSocket経由保存補助 | 補助 |

---

## E. Workflow / スクリプト索引（`D:\ai\ComfyUI\user\default\workflows`）

### 現行（カレント）
| Title | Dict（いつ使う） | Path |
| ---- | ---- | ---- |
| 0304_01_greenback_A_smile_front | 立ち絵差分・笑顔正面（GUI手動） | `workflows\` |
| 0304_01_greenback_B_angry_crossed | 立ち絵差分・怒り腕組み | 同上 |
| 0304_01_greenback_C_shy_fidget | 立ち絵差分・照れもじもじ | 同上 |
| 0304_01_greenback_D_happy_waving | 立ち絵差分・笑顔手振り | 同上 |
| 0304‗Memo.txt | （0バイト・空。整理対象） | 同上 |

### archive（過去資産・宝庫）
| Title | Dict（いつ使う） | Path |
| ---- | ---- | ---- |
| **generate_variants.py** | **立ち絵差分の一括生成エンジン**(API/CLI) | `workflows\archive\` |
| **character_variations.json** | キャラ/表情/ポーズ/背景の定義スキーマ（外部依頼スキーマの原型） | 同上 |
| 0304_01_python_lecture.md | generate_variants.py の操作マニュアル | 同上 |
| 0304_01_test_greenback_A〜D | 立ち絵差分テスト版WF | 同上 |
| workflow_greenback_i2i.json | グリーンバックi2i | 同上 |
| workflow_cg_with_bg.json | 背景CG合成 | 同上 |
| character_variations.json | （同上） | 同上 |
| wf_01_watercolor_chara.json | 水彩キャラ | 同上 |
| wai_v2 / WAI-...SDXLV12 | WAI Illustrious系 | 同上 |
| wf_06_controlnet_openpose.json | openposeでポーズ制御 | 同上 |
| workflow_color_removal.json | 色除去 | 同上 |
| txt2img_warkflow_v1 / v1.2 | txt2img 基本/改良 | 同上 |
| i2i_workflow_v2.1.json | i2i基本 | 同上 |
| MyDailyDriverWorkflow_v1.2.json | 日常メイン | 同上 |
| Qwen-MultiAngle_v1.json | Qwen多角度 | 同上 |
| 0220_style_system_workflow.json | スタイルシステム | 同上 |
| 05_audio_ace_step_1_...json | 音楽生成(ACE-Step) | 同上 |
| mapsheet01.csv | ピクセルタイルCSV一括生成の実例 | 同上 |
| generate_variants.py / comfy.settings.json | 実行・設定 | 同上 |

---

## F. 入出力フォルダ索引

| Title | Dict（いつ使う） | Path |
| ---- | ---- | ---- |
| input | i2i/参照画像の投入先 | `D:\ai\ComfyUI\input\` |
| output | 生成画像の出力先（galge/pixel/audio等にサブ分け済み） | `D:\ai\ComfyUI\output\` |
| └ output\galge\greenback | 立ち絵差分の出力 | 同上 |
| └ output\galge\cg | 背景CG合成の出力 | 同上 |

---

## G. WorkSpace ドキュメント索引（`D:\ai\01‗ConfyUI_WorkSpace`）

| Title | Dict（いつ使う） | Path |
| ---- | ---- | ---- |
| 依頼書.md | 元の依頼・環境資料(2026-02-20版) | `doc\依頼書.md` |
| INDEX.md（本書） | 迷ったら最初に開く索引 | `Report\INDEX.md` |
| 01_環境探索レポート | 環境の現状・安定性リスク | `Report\01_環境探索レポート_2026-05-30.md` |
| 00_全体設計マニュアル | システム全体像・部品・ロードマップ（人間向け親ドキュメント） | `10_manual\00_全体設計マニュアル.md` |
| 01_Manager指示書 | Managerの役割・振り分け・検証・失敗対応（人間向け／フェーズ2のJSON化元） | `10_manual\01_Manager指示書.md` |
| 02_立ち絵差分agent運用手順書 | 最初のagentを実際に動かす手順（起動→ドライラン→本実行） | `10_manual\02_立ち絵差分agent運用手順書.md` |
| 03_用語集とFAQ | 用語の意味・困った時のトラブルシュート | `10_manual\03_用語集とFAQ.md` |
| 20_agents/README | agent定義のJSONC形式・命名・編集ルール | `20_agents\README.md` |
| manager.jsonc | 【AI向け】Manager定義（受付/検証/振り分け/失敗対応） | `20_agents\_manager\manager.jsonc` |
| tachie_diff.agent.jsonc | 【AI向け】立ち絵・差分agent定義（能力/入力契約/実行本体/出力） | `20_agents\tachie_diff\tachie_diff.agent.jsonc` |
| 40_prompts/README | プロンプト集の構造・組み立て方・二重管理ルール | `40_prompts\README.md` |
| tachie_diff_prompts.jsonc | 立ち絵差分の再利用プロンプト部品（品質/ネガ/表情/ポーズ/背景/優先組） | `40_prompts\tachie_diff_prompts.jsonc` |

---

## H. このINDEXの更新ルール

- 新しい成果物（agent/workflow/CSV/manual）を作ったら、必ず該当セクションに1行追記する。
- フォルダ構成を変えたら §A を更新する。
- 「Title / Dict / Path」の3列は崩さない（人間とAIが同じ規則で読むため）。
- 大きな環境変更（パッケージ更新・モデル追加）は `Report\` に日付付きレポートを追加し、§G に登録する。

_最終更新: 2026-05-30 / フェーズ0完了時点_
