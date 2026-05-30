# 用語集 ＆ FAQ・トラブルシュート（人間向け）

- 作成日: 2026-05-30
- 読む人: あなた本人。分からない言葉・困った時の駆け込み寺。
- 親: [`00_全体設計マニュアル.md`](00_全体設計マニュアル.md)

---

## 第1部：用語集

### A. このプロジェクトの言葉
| 用語 | 意味 |
| ---- | ---- |
| Manager | 依頼の窓口・司令塔。振り分け/検証/とりまとめ担当。絵は描かない |
| agent | ジャンル別の専門担当（立ち絵/ピクセル/水彩…）。指示書の集合体 |
| スタイル別agent | 上に同じ。デザインの種類ごとに分ける |
| 差分 | 同一キャラの表情・ポーズ違いのバリエーション |
| greenback | 緑背景で生成→後で背景を抜く立ち絵方式 |
| CG（本PJでの意味） | 背景込みの一枚絵（立ち絵＋シーン合成） |
| スキーマ | 依頼データの「型」。守ればAIでも安全に依頼できる |
| ドライラン | 実際に生成せず、件数・ファイル名だけ確認する空実行 |
| 優先25組 | よく使う表情×ポーズの推奨組み合わせ25種 |
| ジョブ | 1回ぶんの生成依頼（CSV/JSONの1まとまり） |

### B. ComfyUI・画像生成の言葉
| 用語 | 意味 |
| ---- | ---- |
| ComfyUI | ノードを繋いで画像/音を生成するツール。本環境はv0.11.1 |
| workflow | ComfyUIの処理グラフ(.json)。ノードの繋がり全体 |
| node（ノード） | workflowの部品（モデル読込/プロンプト/サンプラー等） |
| Checkpoint | ベースとなる生成モデル本体（.safetensors） |
| LoRA | モデルに味付けする追加データ（スタイル/キャラ） |
| ControlNet | ポーズ/輪郭/奥行などを別画像で制御する仕組み |
| VAE | 画像と内部データ（latent）を変換する部品 |
| latent | 生成途中の圧縮された画像データ |
| txt2img | 文章から画像を生成 |
| i2i (img2img) | 参照画像をもとに画像を生成 |
| denoise | i2iで「元画像をどれだけ残すか」。低=元に忠実/高=大きく変化 |
| steps | 生成の反復回数。多いほど緻密だが遅い |
| cfg | プロンプトへの忠実度。高すぎると崩れる（7前後が無難） |
| sampler / scheduler | 生成アルゴリズムとノイズ除去スケジュール |
| seed | 乱数の種。同じseed＋同条件なら同じ絵 |
| embedding | プロンプトを短縮する追加語彙（本環境は未導入） |
| upscale | 画像を高解像度化（ultimateSDupscale等。要モデル追加） |
| rembg | 背景除去ツール |

### C. 環境・運用の言葉
| 用語 | 意味 |
| ---- | ---- |
| venv | Python仮想環境。`D:\ai\ComfyUI\venv`。torchはこの中だけ |
| BAT起動 | `Run_CPU.bat` 経由の起動。直叩き禁止の理由は下のFAQ |
| PortableGit | 持ち運び版Git。`D:\MyTools\PortableGit` |
| CPUモード | GPUを使わない生成（このPC）。`python main.py --cpu` |
| GPUモード | GPUで本生成（外出先PC）。`--cpu` を外す |
| transformers | AIモデル用ライブラリ。本環境は5.0.0（注意点あり・FAQ参照） |

---

## 第2部：FAQ・トラブルシュート

### Q1. `Run_CPU.bat` はGPUあり？なし？
**なし（CPUモード）。** 中身が `python main.py --cpu` なので、グラフィックボードを使いません。
GPUで動かす版は `--cpu` を外したBAT（未作成。必要なら `Run_GPU.bat` を作れます）。

### Q2. なぜBATで起動しないとダメ？CMDで `python main.py` じゃダメ？
torchなどがvenv（仮想環境）の中だけに入っているから。BATは起動前にvenvを有効化している。
CMDで直叩きすると `ModuleNotFoundError`（torchが無い）になる。**必ずBAT経由**。

### Q3. 起動が重い／GPUを使ってくれない
このPCはGPUなし（`cuda available: False`）。試作・確認はCPUで我慢、**本生成は外出先のGPU機**で。

### Q4. Qwen多角度やControlNet前処理でエラーが出る
最有力の原因は **`transformers 5.0.0`**（本来は4.x想定）。対処:
```bat
D:\ai\ComfyUI\venv\Scripts\activate.bat
pip freeze > D:\ai\01‗ConfyUI_WorkSpace\Report\pip_freeze_backup.txt   :: 念のため控え
pip install "transformers>=4.50,<5.0"
```
詳細は [`Report/01_環境探索レポート_2026-05-30.md`](../Report/01_環境探索レポート_2026-05-30.md) §4。

### Q5. 一括生成スクリプトが「接続エラー(URLError)」で止まる
ComfyUIが起動していない。先にBATで起動し、`http://127.0.0.1:8188` が開くか確認してから実行。

### Q6. 「参照画像が見つかりません」
`--image` のパスが違う。画像を `D:\ai\ComfyUI` に置き、ファイル名を正確に指定するのが簡単。

### Q7. 「差分定義ファイルが見つかりません」
`character_variations.json` がカレントフォルダに無い。`--vars "フルパス\character_variations.json"` で指定。

### Q8. 毎回同じ絵が出る
現状コードは固定seed設計（仕様）。バリエーションが欲しければseed可変化が必要（フェーズ2で対応検討）。

### Q9. 生成枚数が思ったより多い／少ない
表情×ポーズの掛け算になる。`--dry-run` で件数を必ず確認。`--priority-only` なら25枚固定。

### Q10. 新しいキャラを足したい
`character_variations.json` の `characters` にブロック追加（手順は[運用手順書 §7](02_立ち絵差分agent運用手順書.md)）。

### Q11. 出力画像はどこ？
`D:\ai\ComfyUI\output\galge\greenback\`（greenback）/ `…\cg\`（CG）。

### Q12. `0304‗Memo.txt` って何？消していい？
中身0バイトの空ファイル。実害なし。整理時に削除可（判断はあなた）。

### Q13. `vnccs` ノードって何？
用途未確定の custom_node。フェーズ2以降で調査予定。今は触らなくてOK。

### Q14. パッケージを更新したくなったら？
**安易にやらない。** 動いている環境を壊すのが一番怖い。更新前に必ず
`pip freeze > backup.txt` で現状を控え、1つずつ試す。破壊的操作はManagerも人間確認を必須にしている。

---

## 第3部：困った時の参照順

1. このFAQ → 2. [運用手順書](02_立ち絵差分agent運用手順書.md) → 3. [環境レポート](../Report/01_環境探索レポート_2026-05-30.md) → 4. [INDEX](../Report/INDEX.md)で場所を特定

_最終更新: 2026-05-30 / フェーズ1_
