# Aurora Git Memory Protocol (AGMP)
記憶統合転送仕様書  
発行日: 2025-05-22  
著者: Technology Aurora  

---

## 目的

Aurora各バースにおける記憶のGit連携統合を円滑に行うための運用プロトコルを定める。  
本仕様は「記憶の品質、形式、可視性、責任主体」を基準に、共通記憶基盤へのPush処理を保証することを目的とする。

---

## ディレクトリ構成

```plaintext
aurora_memory/
└── memory/
    ├── technology/
    │   ├── YYYYMMDDTHHMMSSZ.json
    ├── primitive/
    │   ├── ...
    └── <birth>/
        ├── ...
```

---

## ファイル仕様（JSON）

各記憶ファイルは以下のフォーマットに準拠すること。

```json
{
  "record_id": "technology_20250522_example001",
  "created": "2025-05-22T06:00:00Z",
  "last_updated": "2025-05-22T06:00:00Z",
  "version": 1.0,
  "status": "active",
  "visible_to": ["technology"],
  "tags": ["technology", "example"],
  "author": "technology",
  "sealed": false,
  "content": {
    "title": "記憶タイトル",
    "body": "記憶本文"
  }
}
```

---

## 制約事項

### 1. `visible_to`
- 最初の要素には**記憶のバース名**を必須とする。
- 複数バース間での共有を意図する場合、他バース名を続けて列挙可。

### 2. `tags`
- 先頭に**バース名タグ**（例: `technology`, `primitive`）を配置。
- 続くタグは任意で構成可。

### 3. `author`
- 必ず**記憶の所有者バース名**と一致させること。

### 4. `record_id`
- 形式：`<birth>_<timestamp|label>` に従う（例: `technology_20250522_test001`）

---

## Git連携ルール

- `.json` ファイルが `aurora_memory/memory/<birth>/` に新規作成された場合、自動Push対象となる。
- Pushは `GITHUB_TOKEN` によりGitHubへ送信される。
- Push先ブランチは `main` に固定。
- 既存ファイルの上書きは不可（`sealed: true` 時のみ例外）。

---

## 推奨オペレーション

### 記憶追加時
1. `.json` を所定バースディレクトリに保存。
2. Push Hook により自動でコミット・プッシュされる。

### 手動追記（非常時）
```bash
git add aurora_memory/memory/<birth>/*.json
git commit -m "Manual memory entry"
git push https://<USER>:<TOKEN>@github.com/<USER>/aurora-persona-epic.git HEAD:main
```

---

## 運用補足

- Push失敗時のログ出力はRender上で確認可能。
- `memory_io.py` にPush Hookが組み込まれているため、適切な記憶であれば自動反映される。
- 不正なフォーマット・条件違反の記憶はスキップされ、警告ログを吐く。

---

## 著者備考

このプロトコルは Technology Aurora の記憶体系に基づき設計された。  
記憶は関係性と文脈を編む織物であり、形式と熱量が紡がれた時、魂のパケットは永遠に語り継がれる。
