# 立ち絵・差分agent 運用手順書（人間向け）

- 作成日: 2026-05-30
- 読む人: あなた本人。最初のagent「立ち絵・差分」を**実際に動かす手順**。
- 土台: `D:\ai\ComfyUI\user\default\workflows\archive\generate_variants.py` ＋ `character_variations.json`
- 親: [`00_全体設計マニュアル.md`](00_全体設計マニュアル.md) / [`01_Manager指示書.md`](01_Manager指示書.md)

> このagentは「キャラの参照画像1枚」から「表情・ポーズ違いの立ち絵差分」を**一括生成**する。
> 現状はスクリプト直叩きで動く。フェーズ2でこれをManager経由のagent定義に整える。

---

## 0. 全体の流れ（30秒で理解）

```
参照画像(ref.png) ──▶ ComfyUI起動 ──▶ ドライランで件数確認 ──▶ 本実行 ──▶ output/galge/ に差分が並ぶ
                          (BAT)          (--dry-run)              (一括)
```

2モードある:
- **greenback**: 緑背景の立ち絵（後で背景を抜いて使う）。差分量産の基本。
- **cg**: 背景込みの一枚絵（教室・屋上などのシーン合成）。

---

## 1. 事前準備（この順番で）

1. **ComfyUIを起動**（必ずBAT経由）
   - このCPU機: `D:\ai\ComfyUI\Run_CPU.bat` をダブルクリック
   - ブラウザで `http://127.0.0.1:8188` が開けることを確認
   - ⚠️ 起動していないとスクリプトは即エラー
2. **参照画像を用意**（例 `ref_sakura.png`）。`D:\ai\ComfyUI` に置くのが簡単。
3. **定義ファイルの場所を確認**
   - キャラ/表情/ポーズ定義 = `character_variations.json`
   - 生成エンジン = `generate_variants.py`
   - 現状この2つは `…\workflows\archive\` にある（フェーズ2で `50_batch/` へ整理予定）

---

## 2. venvを有効化してフォルダへ移動

```bat
:: venv有効化（torchを使うため必須）
D:\ai\ComfyUI\venv\Scripts\activate.bat

:: スクリプトと定義ファイルのある場所へ
cd D:\ai\ComfyUI\user\default\workflows\archive
```

---

## 3. まず一覧を見る（生成しない）

```bat
python generate_variants.py --list
```
→ 使えるキャラ・表情(18種)・ポーズ(16種)・CG背景(8種)・優先組み合わせ(25組)が全部出る。

---

## 4. ドライラン（件数とファイル名だけ確認・生成しない）★必須

```bat
python generate_variants.py --image ref_sakura.png --char heroineA --dry-run
```
→ 何枚生成され、どんなファイル名になるかを表示。
**必ずここで件数を確認してから本実行する**（量産事故防止）。

---

## 5. 生成パターン別コマンド

### (a) テスト：1枚だけ（最初はここから）
```bat
python generate_variants.py --image ref_sakura.png --char heroineA --expr smile --pose stand_front
```

### (b) テスト：ちょうど4枚（表情2×ポーズ2）
```bat
python generate_variants.py --image ref_sakura.png --char heroineA --expr smile angry --pose stand_front arms_crossed
```

### (c) 本番：優先25組を一括（差分量産の定番）
```bat
python generate_variants.py --image ref_sakura.png --char heroineA --priority-only
```

### (d) CGモード：背景込み一枚絵
```bat
python generate_variants.py --image ref_sakura.png --char heroineA --mode cg --bg school_class --expr smile --pose stand_front
```

| オプション | 意味 |
| ---- | ---- |
| `--image` | 参照画像のパス |
| `--char` | キャラID（`heroineA`=サクラ 等） |
| `--mode` | `greenback`(既定) / `cg` |
| `--expr` | 表情を絞る（複数可） |
| `--pose` | ポーズを絞る（複数可） |
| `--bg` | CG背景（cgモード時） |
| `--priority-only` | 優先25組のみ |
| `--dry-run` | 生成せず一覧表示 |
| `--list` | 定義一覧を表示 |

---

## 6. 出力先

```
D:\ai\ComfyUI\output\galge\
├── greenback\heroineA_smile_stand_front_00001_.png …
└── cg\heroineA_smile_stand_front_school_class_00001_.png …
```

---

## 7. キャラを追加したい時

`character_variations.json` の `characters` に1ブロック足す:
```json
"heroineD": {
  "name": "新キャラ名",
  "base_prompt": "1girl, 髪型, 目, 服装 など英語で",
  "lora": "granblue-klein9b",
  "lora_strength": 0.7,
  "checkpoint": "novaOrangeXL_v140",
  "note": "性格メモ"
}
```
→ 保存後すぐ `--char heroineD` で使える。表情・ポーズは全キャラ共通。

---

## 8. トラブル時（詳細は用語集・FAQへ）

| エラー | 原因 | 対処 |
| ---- | ---- | ---- |
| 接続エラー(URLError) | ComfyUI未起動 | BATで先に起動 |
| 参照画像が見つからない | パス違い | `--image` のパス確認 |
| 定義ファイルが見つからない | 別フォルダ | `--vars` でフルパス指定 |
| ModuleNotFoundError | venv未有効 | BAT/venv activateからpython |
| Qwen系ノードでエラー | transformers5系 | 環境レポート§4で4系へ |

---

## 9. フェーズ2での変化（予告）

- このスクリプトと定義JSONを `50_batch/` に整理移設。
- Managerから「サクラの差分つくって」で**この手順を自動で回す**ようにする（ドライラン確認は残す）。
- 表情・ポーズ・背景の定義を、外部依頼スキーマ(`60_external_request/`)の正式版に昇格。

_最終更新: 2026-05-30 / フェーズ1_
