# Config Directory Overview

本ディレクトリは、Aurora Persona System のメモ保存・記憶処理に関する設定・構造定義ファイルを集約しています。

## ファイル一覧

### `memo_conditions.yaml`
- 自動保存の条件を定義する設定ファイル。
- 条件には「特定キーワードの出現」や「最小文字数」などを指定可能。

### `memo_conditions.py`
- `memo_conditions.yaml` を読み込み、メモテキストが保存条件を満たすかどうかを判定するユーティリティ関数を提供。
- 主な関数:
  - `load_conditions()`
  - `check_conditions(memo_text: str, conditions: dict) -> bool`

### `git_memory_protocol.yaml`
- `memory_protocol.py` により読み込まれ、Git に保存する記憶構造と可視性ルールを定義。
- 特に `visible_to` や `author` の検証に使用されます。

### `memory_protocol.py`
- YAML形式のプロトコル（`git_memory_protocol.yaml`）と構造テンプレート（`structure_template.yaml`）を読み込み、記憶データが仕様に準拠しているかを検証。
- 主な機能:
  - 各種検証 (`validate_author`, `validate_tags`, `validate_visible_to`)
  - テンプレートとの整合性確認 (`validate_against_template`)

### `structure_template.yaml`
- 記憶データの構造テンプレートを定義するファイル。
- すべての記憶はこの構造に準拠して記録され、`memory_protocol.py` により検証されます。

---
