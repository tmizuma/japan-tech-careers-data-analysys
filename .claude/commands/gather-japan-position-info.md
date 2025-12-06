---
description: 企業情報CSVから日本のソフトウェアエンジニア求人情報を収集するコマンド
allowed-tools: Bash(*), Read(*.md), Read(*.txt), Read(*.json), Read(*.csv), Write(*.md), Write(*.json), mcp__playwright__*
tools: Read, Write, Bash, mcp__playwright__*
---

# 日本のエンジニア求人情報収集

企業情報 CSV から各企業の求人一覧を取得して JSON 形式で出力します。

## 引数

```
/gather-japan-position-info [CSVファイルパス] [yyyymm] [--from N --to M]
```

- **CSV ファイルパス**: デフォルト `company_list.csv`
- **yyyymm**: 出力先フォルダ名（例: `202412`）、必須
- **--from N**: 処理開始位置（1 始まり）、省略時は 1
- **--to M**: 処理終了位置（1 始まり、この位置を含む）、省略時は全件

例:

- `/gather-japan-position-info company_list.csv 202412` - 全件処理、202412 フォルダに出力
- `/gather-japan-position-info company_list.csv 202412 --from 1 --to 10` - 1〜10 番目を処理
- `/gather-japan-position-info company_list.csv 202501 --from 11 --to 20` - 11〜20 番目を処理

## CSV 形式

必須カラム: `company_name_en`, `hiring_url`

データ型:

- `sales`: 整数（非公開は-1）
- `foreign_engineers`: boolean
- その他: 文字列

## 実行手順

### 1. 引数バリデーション

- CSV ファイルの存在確認
- 必須カラムの確認
- `yyyymm` が指定されているか確認（必須）
- `yyyymm` フォルダが存在しない場合は作成
- `--from` は 1 以上、`--to` は `--from` 以上
- `--to` のみ指定は不可

### 2. CSV 読み込み

yyyymm/ ディレクトリ配下に gathering-todo.md が既に存在する場合は、company_list.csv を読み込まないでください。

yyyymm/ ディレクトリ配下に gathering-todo.md が存在しない場合は、このファイルを作成するために、company_list.csv を全行を読み込み、`company_name_en` と `hiring_url` カラムを読み込みます。
この二つのカラムは gathering-todo.md 作成のために用います。

### 3. gathering-todo.md 作成

yyyymm/ ディレクトリ配下に gathering-todo.md を作成してください。

**【重要】CSV の全企業を必ず記載してください（処理範囲に関わらず）**

形式:

```markdown
# 求人情報収集 TODO

## 処理状況

- CSV ファイル: {ファイルパス}
- 総企業数: {N}社
- 最終更新: {現在時刻}

## 企業リスト

1. [ ] mercari (Mercari) - https://careers.mercari.com/ (未開始)
2. [ ] cyberagent (CyberAgent) - https://... (未開始)
       ...
       {N}. [ ] lastcompany (Last Company) - https://... (未開始)
```

ステータス:

- `N. [ ]` - 未処理
- `N. [x]` - 成功
- `N. [/]` - 部分失敗
- `N. [!]` - 失敗

既存ファイルがある場合は読み込み、指定範囲内の未完了企業のみを処理対象とします。

### 4. Playwright MCP 確認

利用不可の場合はエラーを返して終了。

### 5. 求人情報収集（1 社ずつ順次処理）

処理フロー:

```
for インデックス in 処理範囲開始 から 処理範囲終了:
    企業データ = 全企業リスト[インデックス]

    if gathering-todo.md で完了済み:
        continue

    # 求人収集
    結果 = 企業の求人情報を収集(企業データ)

    # TODO更新
    gathering-todo.md を更新

    # 中間保存
    japan-positions-partial.json を更新
```

#### 企業キー正規化

`company_name_en` を正規化（小文字、記号削除、接尾辞削除）:

- "Mercari" → `mercari`
- "Rakuten Group" → `rakuten`

#### 求人収集の詳細

**ページ取得:**

- `hiring_url` にアクセス
- タイムアウト: 30 秒
- 接続エラー時は 1 回リトライ

**エンジニア求人フィルタリング:**

含むキーワード: Engineer, Developer, Programmer, SRE, DevOps, Infrastructure, QA, Data Scientist, ML, AI, Security, Platform, Frontend, Backend, Full-stack, Mobile, iOS, Android, Web, Software, エンジニア, 開発, Tech Lead, Architect

除外キーワード: Sales, Marketing, HR, Finance, Legal, Admin, 営業, マーケティング, 人事, 経理, 法務, 総務

**収集データ（一覧ページのみ、詳細ページへの遷移不要）:**

```javascript
{
  "name": "求人タイトル",
  "description": "一覧ページの説明文（最大500文字）",
  "techstack": ["Go", "Kubernetes"], // 空配列可
  "link": "求人ページURL"
}
```

技術名の標準化: `javascript` → `JavaScript`, `k8s` → `Kubernetes`, `postgres` → `PostgreSQL`

**【重要】全件取得ルール:**

1. **ページング**: 「次へ」「Next」等を検出して最終ページまで処理
2. **カテゴリ**: 複数のエンジニア関連カテゴリがある場合、全カテゴリを順番に処理（重複除去）
3. **省略禁止**: 「代表的」「一部」の選択は禁止、必ず全件収集
4. **スナップショット切り詰め**: 追加スナップショット取得で継続収集

処理中は 1〜3 秒の遅延を入れてください。

### 6. 結果保存

**gathering-todo.md 更新:**

- 成功: `N. [x] {key} ({company_name_en}) - {url} (成功: M件取得)`
- 失敗: `N. [!] {key} ({company_name_en}) - {url} (失敗: {理由})`

**japan-positions-partial.json:**

CSV の全カラム情報 + positions 配列を保存:

```json
{
  "mercari": {
    "company_name_ja": "メルカリ",
    "company_name_en": "Mercari",
    "sales": 1700,
    "foreign_engineers": true,
    ...全CSVカラム,
    "positions": [...]
  },
  "_metadata": {
    "last_updated": "2025-12-07T10:00:00Z",
    "completed_count": 10,
    "total_count": 100
  }
}
```

データ型保持: `sales`は整数、`foreign_engineers`は boolean

### 7. 完了サマリー

範囲指定時:

```
⏸️ 求人情報収集を一時停止（範囲指定実行）

処理サマリー:
- 処理範囲: {from}番目 〜 {to}番目
- 今回処理: {N}社
- 成功: {成功数}社
- 失敗: {失敗数}社
- 今回取得ポジション数: {件数}件

出力先: {yyyymm}/ フォルダ
全体進捗: {完了数}/{総数}社完了
```

全件完了時:

```
✅ 求人情報収集完了

処理サマリー:
- 処理企業数: {N}社
- 成功: {成功数}社
- 失敗: {失敗数}社
- 取得ポジション総数: {件数}件

出力先: {yyyymm}/ フォルダ（{成功数}個のJSONファイル）
```

## エラーハンドリング

**接続エラー時の個別 JSON ファイル:**

`{yyyymm}/{企業キー}.json`:

```json
{
  "company_name_ja": "...",
  "company_name_en": "...",
  "sales": 1700,
  "foreign_engineers": true,
  ...全CSVフィールド,
  "positions": [],
  "error": "CONNECTION_ERROR",
  "error_message": "Failed to connect"
}
```

**パースエラー時の個別 JSON ファイル:**

`{yyyymm}/{企業キー}.json`:

```json
{
  "company_name_ja": "...",
  "company_name_en": "...",
  ...全CSVフィールド,
  "positions": [],
  "error": "PARSE_ERROR",
  "error_message": "Failed to parse listings"
}
```

**タイムアウト:**
取得済みの情報のみ返し、`"_warning": "PARTIAL_RESULT"` を追加

## 重要事項

1. **gathering-todo.md には必ず CSV 全企業を記載**（処理範囲に関わらず）
2. **1 社ずつ順次処理**（並行実行禁止）
3. **全件収集**（省略・サンプリング禁止）
4. **データ型保持**: sales（整数）、foreign_engineers（boolean）
5. **詳細ページへの遷移不要**（一覧ページのみ）
6. **コミット不要**
