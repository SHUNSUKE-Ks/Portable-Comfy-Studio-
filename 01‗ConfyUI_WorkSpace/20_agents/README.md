# 20_agents — AIエージェント定義（JSONC）

このフォルダは、ComfyUI制作システムの**AI向けagent定義**を置く場所です。
人間向けの仕様は [`../10_manual/`](../10_manual/) にあり、ここはそれを**AIが読む形（JSONC）**へ翻訳したもの。

## ファイル形式：JSONC（`//` コメント付きJSON）

- 拡張子 `.jsonc`。純粋JSONに `//` 行コメントを足した形式。
- 採用理由: 機械可読（JSONそのまま）でありつつ、AI・人間どちらにも意図が読める。
- ⚠️ **Pythonの標準 `json` は `//` を解釈できない。** 実行時にJSONCを読む場合は、
  - コメント除去してから `json.loads` する（簡易: 各行の `//` 以降を除去。ただし文字列内 `//` に注意）、または
  - `json5` / `commentjson` 等のライブラリを使う、または
  - 「定義の正(source of truth)はJSONC、実行用の純JSONはビルドで生成」する運用にする。
- 当面は **AI(ManagerやClaude)が直接読んで運用**するため、パース問題は実害なし。
  フェーズ3で自動実行する段階になったら上記いずれかを決める。

## 構成

```
20_agents/
├── _manager/
│   └── manager.jsonc            司令塔。受付/検証/振り分け/とりまとめ
└── tachie_diff/
    └── tachie_diff.agent.jsonc  立ち絵・差分agent（最初の1体）
```

将来agentが増えたら `pixel/` `style/` `multi_angle/` `audio/` を同じ要領で追加。

## 命名規則

- Manager: `manager.jsonc`
- スタイルagent: `<id>.agent.jsonc`（id は manager.jsonc の routing_rules と一致させる）
- `_` 始まりフォルダ = 親/共通（Manager等）

## 編集時のルール

- `schema_version` は形を大きく変えたら上げる。
- パスを変えたら参照元（manager.jsonc の agent_ref / assets、各agentの engine）も更新。
- 定義データ（キャラ/表情/ポーズの本文）の**正は `character_variations.json`**。
  agent側 `char_definitions` は「キー一覧の早見表」であり、本文を二重管理しない。

_最終更新: 2026-05-30 / フェーズ2_
