# 40_prompts — プロンプト集（再利用ライブラリ）

スタイル別に、**組み合わせ可能なプロンプト部品**を貯める場所。
agentやスクリプトはここから部品を引いて最終プロンプトを組み立てる。

## 収録ファイル

| ファイル | 対応agent | 内容 |
| ---- | ---- | ---- |
| `tachie_diff_prompts.jsonc` | 立ち絵・差分 | 品質/ネガ・キャラbase・表情18・ポーズ16・CG背景8・優先25組 |

将来: `pixel_prompts.jsonc` / `style_watercolor_prompts.jsonc` などを同形式で追加。

## 設計の考え方（部品の組み立て）

```
最終プロンプト =
  base(キャラ) + expression(表情) + pose(ポーズ) + framing + extra(背景/緑) + quality(品質タグ)
ネガティブ =
  global_negative ( + greenback_extra_negative )
```

各部品は `compose_template` の雛形に従って連結する。
これにより「表情だけ差し替え」「ポーズだけ差し替え」が独立してできる。

## ⚠️ 二重管理についての重要ルール

- **engine（generate_variants.py）が実行に使う正データは
  `character_variations.json`**（`D:\ai\ComfyUI\…\archive\`）。
- このフォルダのファイルは **編集・拡張・閲覧の作業用カタログ**。
- 値を変えたら **必ず character_variations.json にも反映**すること（今は手動同期）。
- フェーズ3で「正を1つに統一」する（このライブラリを正にして、そこから
  character_variations.json を生成する方式を予定）。

## status フラグの意味

| status | 意味 |
| ---- | ---- |
| `stable` | 実績あり。本番で使ってよい |
| `draft` | 未検証の拡張候補。本番投入前に少数枚でテストすること |

新しい表情・ポーズ・背景を思いついたら、まず `status: "draft"` で追記 → GPU機でテスト → 良ければ `stable` に昇格、の順で。

_最終更新: 2026-05-30 / フェーズ2（設計）_
