---
description: 企業情報CSVから日本のソフトウェアエンジニア求人情報を収集するコマンド
allowed-tools: Bash(*), Read(*.md), Read(*.txt), Read(*.json), Read(*.csv), Write(*.md), Write(*.json), mcp__playwright__*
tools: Read, Write, Bash, mcp__playwright__*
---

# タスク: 日本のソフトウェアエンジニア求人情報収集

企業情報 CSV を受け取り、各企業の採用ページから求人一覧を取得して JSON 形式で出力します。ポジション詳細画面には遷移せず、一覧ページから取得可能な情報のみを収集します。

## 引数

- **第 1 引数（オプション）**: 企業情報 CSV ファイルのパス

  - デフォルト: `company_list.csv`
  - 形式: CSV（ヘッダー行を含む）
  - 必須カラム: `company_name_en`, `hiring_url`

- **第 2 引数（オプション）**: `--max-companies`
- **第 3 引数（オプション）**: 一度に処理する企業数の上限（数値）
  - 例: `--max-companies 10`
  - 指定しない場合は全件処理

## 前提条件

- Playwright MCP が利用可能であること
- 企業情報 CSV ファイルが存在すること
- CSV に `company_name_en` と `hiring_url` カラムが含まれていること

## CSV ファイル形式

```csv
company_name_ja,company_name_en,description,description_en,hiring_url,num_of_employees,sales,foreign_engineers,logo_url,company_url
```

**データ型:**

- `sales`: 整数型（非公開の場合は -1）
- `foreign_engineers`: boolean 型（TRUE/FALSE）
- その他: 文字列型

## 実行手順

### ステップ 1: 引数のバリデーション

1. 第 1 引数が指定されていない場合は `company_list.csv` をデフォルトとする
2. 指定されたファイルが存在することを確認
3. ファイルが CSV 形式であることを確認
4. `--max-companies` オプションが指定されている場合、数値が有効か確認

**引数なしの場合（デフォルト動作）:**

```
使用方法: /gather-japan-position-info [CSVファイルパス] [--max-companies N]

例:
  /gather-japan-position-info
  /gather-japan-position-info company_list.csv
  /gather-japan-position-info company_list.csv --max-companies 10

引数:
  CSVファイルパス (オプション) - 企業情報CSVファイル（デフォルト: company_list.csv）

オプション:
  --max-companies N  一度に処理する企業数の上限（指定しない場合は全件処理）

CSVファイル形式:
  - ヘッダー行を含むCSV
  - 必須カラム: company_name_en, hiring_url
  - その他のカラムはすべて出力に含まれます
```

**ファイルが存在しない場合:**

```
❌ エラー: ファイル '{パス}' が見つかりません。

デフォルトファイル (company_list.csv) を使用する場合:
  /gather-japan-position-info

カスタムファイルを使用する場合:
  /gather-japan-position-info [ファイルパス]
```

**必須カラムが不足している場合:**

```
❌ エラー: CSVに必須カラムが含まれていません。
必須カラム: company_name_en, hiring_url
見つかったカラム: {実際のカラムリスト}
```

**--max-companies の値が無効な場合:**

```
❌ エラー: --max-companies の値は正の整数である必要があります。
指定された値: {値}
```

### ステップ 2: CSV ファイルの読み込み

CSV ファイルを読み込み、処理対象の企業リストを作成します。

**処理ルール:**

- ヘッダー行を読み取り、カラム名を取得
- 各行をパースして企業情報として保持
- `hiring_url` が空または無効な行はスキップ
- `company_name_en` が空の行はスキップ
- `sales` カラムを整数型として読み込む（-1 は非公開を意味）
- `foreign_engineers` カラムを boolean 型として読み込む

**空の CSV または有効な企業がない場合:**

```
⚠️ 警告: CSVファイルに有効な企業データが含まれていません。
company_name_en と hiring_url が両方とも入力されている行が必要です。
```

### ステップ 3: gathering-todo.md の作成・確認

進捗管理用の `gathering-todo.md` ファイルを作成または既存ファイルを確認します。

**新規作成の場合:**

```markdown
# 求人情報収集 TODO

## 処理状況

- 開始時刻: {現在時刻}
- CSV ファイル: {ファイルパス}
- 総企業数: {N}
- 処理上限: {max_companies 指定時のみ表示}

## 企業リスト

- [ ] mercari (Mercari) - https://careers.mercari.com/ (未開始)
- [ ] cyberagent (CyberAgent) - https://www.cyberagent.co.jp/careers/ (未開始)
      ...
```

**既存ファイルがある場合（再開モード）:**

- 既存の `gathering-todo.md` を読み込み
- 完了済み（`- [x]`）の企業はスキップ
- 未完了の企業のみ処理対象：
  - `- [ ] ... (未開始)` - 処理対象
  - `- [/] ... (部分失敗)` - 処理対象（再試行）
  - `- [!] ... (失敗: ...)` - 処理対象（再試行）

**ステータス形式:**

- `- [ ] {key} ({company_name_en}) - {hiring_url} (未開始)` - 未処理
- `- [x] {key} ({company_name_en}) - {hiring_url} (成功: N件取得)` - 成功
- `- [/] {key} ({company_name_en}) - {hiring_url} (部分失敗)` - 一部のみ取得成功
- `- [!] {key} ({company_name_en}) - {hiring_url} (失敗: エラー内容)` - 失敗

{key} は company_name_en を正規化したもの（小文字、記号削除等）

### ステップ 3.5: company-patterns.json の読み込み（オプション）

企業の求人ページ URL パターンを記録したファイルが存在する場合、読み込みます。

**ファイル形式:**

```json
{
  "mercari": {
    "career_page_pattern": "https://careers.mercari.com/jp/",
    "last_successful": "2025-12-01",
    "confidence": "high"
  },
  "google": {
    "career_page_pattern": "https://careers.google.com/jobs/results/",
    "search_params": "?q=software%20engineer&location=Japan",
    "last_successful": "2025-12-01",
    "confidence": "high"
  }
}
```

### ステップ 4: MCP 可用性の確認

**重要: Playwright MCP が利用できない場合は即座にエラーを返してください。**

1. **Playwright MCP** (`mcp__playwright__*`) が利用可能か確認
2. **利用不可の場合は即座にエラーを返却して終了**

```
❌ エラー: Playwright MCP が利用できません。
Playwright MCP を有効にしてから再度実行してください。
```

### ステップ 5: 各企業の求人情報を順次収集

Playwright MCP を使用して、各企業の求人情報を収集します。

**実行ルール:**

- **1 社ずつ順次処理**（ブラウザリソース競合を回避するため）
- 各企業の処理完了を待ってから次を開始
- **max_companies が指定されている場合、その数だけ処理したら中断**

**処理フロー:**

```
処理対象企業リスト = gathering-todo.md から未完了企業を抽出
処理済みカウンター = 0

for 企業データ in 処理対象企業リスト:
    if max_companies が指定されている and 処理済みカウンター >= max_companies:
        処理を中断
        break

    # 企業キーの正規化
    企業キー = company_name_en を正規化

    # パターンキャッシュの確認（オプション）
    パターンURL = null
    if company-patterns.json に企業のパターンが存在:
        パターンURL = パターンから取得

    # 求人情報の収集（以下の詳細手順を実行）
    結果 = 企業の求人情報を収集(企業データ, パターンURL)

    # 結果を gathering-todo.md に記録
    gathering-todo.md を更新

    # 結果を japan-positions-partial.json に保存
    japan-positions-partial.json を更新

    # 成功した場合、パターンをキャッシュに保存（オプション）
    if 成功 and パターンが検出された:
        company-patterns.json を更新

    処理済みカウンター += 1
```

#### 企業キーの正規化ルール

`company_name_en` を以下のルールで正規化してキーとします：

- **英語のみ使用**
- **小文字のみ**
- **スペース・記号は使用禁止**（削除する）
- **接尾辞は削除**: Inc., Ltd., Co., Corp., 株式会社, グループ 等
- **ハイフン・アンダースコアは削除**
- **数字はそのまま保持**

例:

- "Mercari" → `mercari`
- "Rakuten Group" → `rakuten`
- "LY Corporation" → `lycorporation`
- "SmartHR" → `smarthr`
- "PayPay" → `paypay`

#### 求人情報収集の詳細手順

各企業に対して以下の手順で求人情報を収集します：

**5.1: ページの取得**

Playwright MCP を使用して、指定された URL のページを取得します。

**通常の場合:**

1. hiring_url にアクセス
2. 必要に応じて求人ページへのリンクを探索

**注意事項:**

- User-Agent は標準的なブラウザのものを使用
- タイムアウト: 30 秒
- 接続エラー時は 1 回リトライ

**5.2: エンジニア求人のフィルタリング**

ページ内の求人情報から、以下のキーワードを含む**エンジニア関連職種のみ**をフィルタリングしてください。
大文字小文字を区別せずマッチングします。

**フィルタリングキーワード:**

- Engineer, Developer, Programmer
- SRE, DevOps, Infrastructure
- QA, Quality Assurance, Test
- Data Scientist, ML Engineer, AI, Machine Learning
- Security Engineer, Platform Engineer
- Frontend, Backend, Full-stack, Fullstack
- Mobile, iOS, Android, Web
- Software, エンジニア, 開発, プログラマ
- Tech Lead, Architect, CTO

**除外キーワード:**

- Sales, Marketing, HR, Finance, Legal, Admin
- 営業, マーケティング, 人事, 経理, 法務, 総務

**5.3: 求人一覧ページからの情報収集**

求人一覧ページ(CSV の hiring_url)から以下の情報を収集してください。ポジション詳細ページへの遷移は不要です。

**収集する情報:**

1. **求人タイトル** (name)
2. **求人説明** (description)
   - 一覧ページに表示されている説明文のみ
   - 最大 500 文字
   - 500 文字を超える場合は末尾を "..." で切り詰め
3. **技術スタック** (techstack)
   - 一覧ページに表示されている技術キーワードを抽出
   - 抽出対象例: Python, JavaScript, Go, Java, Ruby, TypeScript,
     React, Vue, Angular, Node.js, Django, Rails, AWS, GCP, Azure,
     Kubernetes, Docker, PostgreSQL, MySQL, MongoDB, Redis 等
   - 技術名の標準化:
     - `javascript` → `JavaScript`
     - `k8s` → `Kubernetes`
     - `postgres` → `PostgreSQL`
     - `react.js` → `React`
   - 見つからない場合は空の配列
4. **求人ページへのリンク** (link)

**フィルタリング機能の活用:**

- 求人一覧ページにフィルタリング機能がある場合は活用してください
- 例: 職種でエンジニア関連のみを絞り込む
- 例: 勤務地で日本を絞り込む

**ページング処理:**

- 求人一覧が複数ページにわたる場合、最終ページまで処理してください
- 「次へ」「Next」等のページング要素を検出して遷移
- 最終ページに到達したら処理を終了

**処理の注意点:**

- ポジション詳細ページへの遷移は不要です
- 一覧ページから取得可能な情報のみを収集してください
- 求人数が多い場合でも、全ての求人を探索対象としてください。勝手な判断で途中で処理を打ち切ることをしないでください
- これは統計情報として扱われるため、少なくともポジション数は正確に把握する必要があります

**【重要】全件取得の原則:**

- **省略・サンプリング禁止**: 「代表的な求人」「主要な求人」などの判断で一部のみを取得することは禁止。必ず全件取得すること
- **確認ルール**: 以下の場合は作業を進める前にユーザーに報告し確認を取ること
  - ページに表示されている求人総数と、実際に取得した件数に差異がある場合
  - ページネーションや「もっと見る」ボタンがあり、全件表示されていない可能性がある場合
  - フィルタリング後の件数が想定より著しく少ない場合（例: エンジニア求人が0件）
- **完了基準**: 各企業について、取得可能な全てのエンジニア求人を取得したことを確認してから次の企業に進むこと

### ステップ 6: 結果の収集と TODO 更新

各企業の処理が完了したら、以下を実行します：

1. **gathering-todo.md の更新**

   - 成功時: `- [x] {key} ({company_name_en}) - {hiring_url} (成功: N件取得)`
   - 部分失敗: `- [/] {key} ({company_name_en}) - {hiring_url} (部分失敗)`
   - 失敗時: `- [!] {key} ({company_name_en}) - {hiring_url} (失敗: エラー内容)`

2. **中間結果の保存**

   - 収集した JSON を生成
   - CSV の企業情報（全カラム）と positions 配列をマージ
   - `japan-positions-partial.json` に**上書き保存**
   - 保存形式は最終出力と同じ JSON 形式

3. **バリデーション（オプション）**
   - JSON が正しくパースできるか確認
   - positions 配列内の必須フィールド（name, link）が存在するか確認
   - URL が有効な形式か確認
   - 異常があれば警告を表示

**中間結果ファイル形式（japan-positions-partial.json）:**

```json
{
  "mercari": {
    "company_name_ja": "メルカリ",
    "company_name_en": "Mercari",
    "description": "日本最大のフリマアプリ。...",
    "description_en": "Operates Mercari, Japan's largest flea market app...",
    "hiring_url": "https://careers.mercari.com/",
    "num_of_employees": "2000+",
    "sales": 1700,
    "foreign_engineers": true,
    "logo_url": "https://logo.clearbit.com/mercari.com",
    "company_url": "https://about.mercari.com/",
    "positions": [
      {
        "name": "Backend Engineer",
        "description": "We are looking for backend engineers...",
        "techstack": ["Go", "Kubernetes"],
        "link": "https://careers.mercari.com/jp/jobs/123"
      },
      {
        "name": "iOS Engineer",
        "description": "Join our iOS team...",
        "techstack": ["Swift", "iOS"],
        "link": "https://careers.mercari.com/jp/jobs/124"
      }
    ]
  },
  "cyberagent": {
    "company_name_ja": "サイバーエージェント",
    "company_name_en": "CyberAgent",
    "description": "...",
    "description_en": "...",
    "sales": 7200,
    "foreign_engineers": false,
    "positions": [...]
  },
  "_metadata": {
    "last_updated": "2025-12-06T12:00:00Z",
    "completed_count": 3,
    "total_count": 100
  }
}
```

**データ型の注意:**

- 必ず `{` で始まり `}` で終わる有効な JSON オブジェクトを生成してください
- 入力として受け取った企業情報の**全フィールド**を出力に含めてください
- **データ型を正確に保持**してください:
  - `sales`: 整数型（ダブルクォート不要、例: 1700, -1）
  - `foreign_engineers`: boolean 型（ダブルクォート不要、例: true, false）
  - その他: 文字列型
- positions 配列に収集した求人情報を格納してください

### ステップ 7: 最終 JSON 出力

**全ての企業の処理が完了した場合のみ**、最終結果を出力します。

**出力ファイル:** `japan-positions.json`

**出力形式:**

```json
{
  "mercari": {
    "company_name_ja": "メルカリ",
    "company_name_en": "Mercari",
    "description": "日本最大のフリマアプリ。...",
    "description_en": "Operates Mercari, Japan's largest flea market app...",
    "hiring_url": "https://careers.mercari.com/",
    "num_of_employees": "2000+",
    "sales": 1700,
    "foreign_engineers": true,
    "logo_url": "https://logo.clearbit.com/mercari.com",
    "company_url": "https://about.mercari.com/",
    "positions": [
      {
        "name": "Backend Engineer",
        "description": "We are looking for backend engineers...",
        "techstack": ["Go", "Kubernetes"],
        "link": "https://careers.mercari.com/jp/jobs/123"
      }
    ]
  },
  "cyberagent": {
    ...
  }
}
```

**データ型の注意:**

- `sales`: 整数型（例: 1700, 7200, -1）
- `foreign_engineers`: boolean 型（true/false）
- その他: 文字列型

**出力処理:**

1. 全ての結果をマージ
2. `_metadata` フィールドを削除
3. `japan-positions.json` に保存
4. 成功時のみ `japan-positions-partial.json` を削除

**max_companies で途中終了した場合:**

- `japan-positions.json` は作成しない
- `japan-positions-partial.json` のみ保持
- 次回実行時に続きから処理

### ステップ 8: 完了サマリーの表示

処理完了後、以下の形式でサマリーを表示します：

**途中終了時（max_companies 指定時）:**

```
⏸️ 求人情報収集を一時停止

処理サマリー:
- 今回処理: 10社
- 成功: 8社
- 部分成功: 1社
- 失敗: 1社
- 今回取得ポジション数: 42件

出力ファイル:
- japan-positions-partial.json (中間結果)

残り企業: 90社
再開するには同じコマンドを再度実行してください。

詳細は gathering-todo.md を確認してください。
```

**全件完了時:**

```
✅ 求人情報収集完了

処理サマリー:
- 処理企業数: 100社
- 成功: 85社
- 部分成功: 10社
- 失敗: 5社
- 取得ポジション総数: 428件

出力ファイル:
- japan-positions.json

詳細は gathering-todo.md を確認してください。
```

## エラーハンドリング

### CSV 読み込みエラー

- CSV のパースに失敗した場合はエラーを表示
- 不正な行がある場合は警告を出してスキップ
- `sales` カラムが整数に変換できない場合は -1 として扱う
- `foreign_engineers` カラムが boolean でない場合は false として扱う

### 接続エラー

企業の求人ページに接続できない場合：

```json
{
  "{正規化された企業キー}": {
    "company_name_ja": "${入力値}",
    "company_name_en": "${入力値}",
    "description": "${入力値}",
    "description_en": "${入力値}",
    "hiring_url": "${入力値}",
    "num_of_employees": "${入力値}",
    "sales": ${入力値（整数型）},
    "foreign_engineers": ${入力値（boolean型）},
    "logo_url": "${入力値}",
    "company_url": "${入力値}",
    "positions": [],
    "error": "CONNECTION_ERROR",
    "error_message": "Failed to connect to ${url} after retry"
  }
}
```

### ページ構造解析失敗

```json
{
  "{正規化された企業キー}": {
    "company_name_ja": "${入力値}",
    "company_name_en": "${入力値}",
    "description": "${入力値}",
    "description_en": "${入力値}",
    "hiring_url": "${入力値}",
    "num_of_employees": "${入力値}",
    "sales": ${入力値（整数型）},
    "foreign_engineers": ${入力値（boolean型）},
    "logo_url": "${入力値}",
    "company_url": "${入力値}",
    "positions": [],
    "error": "PARSE_ERROR",
    "error_message": "Failed to parse job listings from ${url}"
  }
}
```

### 求人情報なし

企業ページにエンジニア関連の求人が見つからない場合、空の配列を返します：

```json
{
  "{正規化された企業キー}": {
    "company_name_ja": "${入力値}",
    "company_name_en": "${入力値}",
    "description": "${入力値}",
    "description_en": "${入力値}",
    "hiring_url": "${入力値}",
    "num_of_employees": "${入力値}",
    "sales": ${入力値（整数型）},
    "foreign_engineers": ${入力値（boolean型）},
    "logo_url": "${入力値}",
    "company_url": "${入力値}",
    "positions": []
  }
}
```

### タイムアウト

30 秒を超える処理は中断し、取得済みの情報のみを返します：

```json
{
  "{正規化された企業キー}": {
    "company_name_ja": "${入力値}",
    "company_name_en": "${入力値}",
    ...（入力の全フィールド、データ型保持）,
    "positions": [
      ...取得済みの求人情報...
    ],
    "_warning": "PARTIAL_RESULT",
    "_warning_message": "Processing timed out. Returning partial results."
  }
}
```

### 部分的な失敗

- 取得できた結果のみを保存
- gathering-todo.md を `- [/]` で更新

### 途中中断からの再開

既存の `gathering-todo.md` がある場合は、未完了の企業のみを処理対象として再開します。
`japan-positions-partial.json` が存在する場合は、その内容を引き継いで処理を継続します。

## 実行例

### デフォルト実行（company_list.csv を使用）

```
ユーザー入力:
/gather-japan-position-info

処理:
📖 CSVファイルを読み込み中...
  → company_list.csv
  → 100社のデータを検出

📝 gathering-todo.md を作成中...

🔍 Playwright MCP の確認中...
  ✅ 利用可能

🚀 求人情報収集を開始...
  → 100社を順次処理中...

✅ mercari (Mercari): 8件取得
✅ cyberagent (CyberAgent): 12件取得
✅ rakuten (Rakuten Group): 6件取得
...

📄 japan-positions.json を出力しました

✅ 求人情報収集完了

処理サマリー:
- 処理企業数: 100社
- 成功: 85社
- 部分成功: 10社
- 失敗: 5社
- 取得ポジション総数: 428件
```

### カスタム CSV ファイルを指定

```
ユーザー入力:
/gather-japan-position-info my-companies.csv

処理:
📖 CSVファイルを読み込み中...
  → my-companies.csv
  → 50社のデータを検出

...
```

### 段階的実行（max-companies 使用）

```
ユーザー入力:
/gather-japan-position-info --max-companies 10

処理:
📖 CSVファイルを読み込み中...
  → company_list.csv（デフォルト）
  → 100社のデータを検出

📝 gathering-todo.md を作成中...

🔍 Playwright MCP の確認中...
  ✅ 利用可能

🚀 求人情報収集を開始...
  → 最大10社を処理中...

✅ mercari (Mercari): 8件取得
✅ cyberagent (CyberAgent): 12件取得
...（10社分）

⏸️ 求人情報収集を一時停止

処理サマリー:
- 今回処理: 10社
- 成功: 8社
- 部分成功: 1社
- 失敗: 1社
- 今回取得ポジション数: 82件

残り企業: 90社
再開するには同じコマンドを再度実行してください。
```

### 再開実行

```
ユーザー入力:
/gather-japan-position-info --max-companies 10

処理:
📖 既存の gathering-todo.md を検出
  → 再開モードで実行
  → 未完了: 90社
  → 今回処理: 最大10社

🚀 残りの企業を処理中...

✅ 求人情報収集を一時停止（再開処理）
```

## 注意事項

1. **即時更新**: 各企業の処理完了後は即座に TODO を更新
2. **中間保存**: 途中結果は常に `japan-positions-partial.json` に保存
3. **順次処理**: ブラウザ競合を避けるため 1 社ずつ処理（並行実行禁止）
4. **遅延設定**: 各リクエスト間に 1-3 秒の遅延を入れる
5. **コミットしない**: このコマンドはコミットを行わない
6. **段階的実行**: 大量の企業を処理する場合は `--max-companies` で分割実行を推奨
7. **CSV 情報の保持**: CSV の全カラム情報を出力 JSON に含める
8. **データ型の保持**: sales は整数型、foreign_engineers は boolean 型として扱う
9. **一覧ページのみ**: ポジション詳細ページへの遷移は不要

## データ構造の詳細

### CSV から出力 JSON へのマッピング

CSV 行の全カラムがそのまま出力 JSON の各企業オブジェクトに含まれます：

```
CSV行:
company_name_ja,company_name_en,description,description_en,hiring_url,...

↓

JSON出力:
{
  "{正規化されたcompany_name_en}": {
    "company_name_ja": "...",
    "company_name_en": "...",
    "description": "...",
    "description_en": "...",
    "hiring_url": "...",
    ...（CSVの全カラム）,
    "positions": [...]
  }
}
```

## 依存関係

- Playwright MCP (`mcp__playwright__*`)

## オプション機能

### パターンキャッシュ（company-patterns.json）

企業ごとの求人ページ URL パターンを記録することで、2 回目以降の実行を高速化できます。
このファイルは自動的に更新されますが、手動での編集も可能です。

### 詳細ログ（gathering-details.jsonl）

各企業の処理詳細を JSON Lines 形式で記録できます（オプション）。
デバッグや改善に役立ちます。

## 実行開始

コマンドとして呼び出された際、上記の手順に従って求人情報収集タスクを開始してください。
