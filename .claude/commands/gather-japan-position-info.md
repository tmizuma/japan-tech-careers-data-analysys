---
description: 企業情報CSVから日本のソフトウェアエンジニア求人情報を収集するコマンド
allowed-tools: Bash(*), Read(*.md), Read(*.txt), Read(*.json), Read(*.csv), Read(*.ts), Write(*.md), Write(*.json), mcp__playwright__*
tools: Read, Write, Bash, mcp__playwright__*
---

# 目的: 日本のエンジニア求人情報収集の統計情報を取得する。

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

- `/gather-japan-position-info company_list.csv 202412` - 全件処理
- `/gather-japan-position-info company_list.csv 202412 --from 1 --to 10` - 1〜10 番目を処理

## 実行手順

### 1. 引数バリデーション

- CSV ファイルの存在確認
- `yyyymm` フォルダが存在しない場合は作成
- `--from` は 1 以上、`--to` は `--from` 以上

### 2. gathering-todo.md 作成

yyyymm/ ディレクトリ配下に gathering-todo.md が存在しない場合のみ作成。
CSV の全企業を記載（処理範囲に関わらず）。

```markdown
# 求人情報収集 TODO

## 処理状況

- CSV ファイル: {ファイルパス}
- 総企業数: {N}社
- 最終更新: {現在時刻}

## 企業リスト

1. [ ] mercari (Mercari) - https://careers.mercari.com/
2. [ ] cyberagent (CyberAgent) - https://...
       ...
```

ステータス: `[ ]` 未処理、`[x]` 成功

### 3. 求人情報収集（1 社ずつ順次処理）

```
for 企業 in 処理範囲:
    if 完了済み: continue

    求人情報を収集
    JSON保存 → バリデーション実行

    if バリデーション成功:
        gathering-todo.md を [x] に更新
    else:
        JSON削除、error.log に記録、[ ] のまま
```

#### 求人収集の取得手順

1. ページ取得

- `hiring_url` にアクセス
- タイムアウト: 30 秒、エラー時は 1 回リトライ

2. エンジニア求人フィルタリング

多くのサイトでは、求人一覧ページ(詳細ページの URL リンク付き)が表示されます。
必ず以下のフィルタリングを行い、エンジニアに関連する求人情報のみ取得するようにしてください。

含む: Engineer, Developer, SRE, DevOps, QA, Data Scientist, ML, AI, エンジニア, 開発, EM, エンジニアリングマネージャー 等
除外: Sales, Marketing, HR, 営業, 人事 等

もし、アクセス先に求人のフィルタリング機能や検索機能がある場合は、うまくフィルタリングや検索を活用してください。
ページネーションがある場合必ずフィルタリングを行ったのちに最後のページまで遷移してください。

3. 求人情報の取得

求人リンクから以下を取得してください

- 求人名: positions[].name として保存
- 求人詳細ページの URL: positions[].link として保存

調査に時間がかかるため、詳細 ページには絶対にアクセスしないでください。
万が一、link が取得できない場合は空文字列としてください。

※ 必ず全件取得ルール

- ページング: 最終ページまで処理
- 省略禁止: 必ず全件収集

処理中は 1〜3 秒の遅延を入れる。

### 4. 結果保存

**JSON 形式（CSV の全フィールド + positions）:**

```json
{
  "company_name_ja": "メルカリ",
  "company_name_en": "Mercari",
  "description": "フリマアプリ「メルカリ」を運営",
  "description_en": "Operates flea market app Mercari",
  "hiring_url": "https://careers.mercari.com/",
  "num_of_employees": "2000+",
  "sales": 170000000000,
  "foreign_engineers": true,
  "logo_url": "https://logo.clearbit.com/mercari.com",
  "company_url": "https://about.mercari.com/",
  "positions": [
    {
      "name": "Backend Engineer", // 求人リンクから取得した求人タイトル
      "link": "https://careers.mercari.com/jobs/123" // 求人リンクから取得した詳細ページへのリンク
    }
  ]
}
```

**JSON 出力後、必ずバリデーションを実行:**

```bash
npx ts-node scripts/validate-company.ts {yyyymm}/{企業キー}.json
```

このスクリプトは `schemas/company-position.ts` の Zod スキーマで型チェックを行う。
失敗時は JSON を削除し、error.log に記録する。

**エラー時: {yyyymm}/error.log に追記**

```
[2024-12-25 10:30:00] astroscale: CONNECTION_ERROR - Failed to connect
[2024-12-25 10:31:00] somecompany: VALIDATION_ERROR - sales must be number
```

### 5. 完了サマリー

```
✅ 求人情報収集完了

処理サマリー:
- 処理企業数: {N}社
- 成功: {成功数}社
- 失敗: {失敗数}社（error.log 参照）
- 取得ポジション総数: {件数}件
```

## 禁止事項

以下のような行為は禁止します。もし、禁止事項を破らなければならない事情が発生した場合は、即座に作業を中断し、ユーザに判断を仰いでください
特に、統計情報に狂いが生じる可能性のある操作は絶対にやめてください。

1. 全ての求人情報を取得しない
   → 今回の調査で最も大事なのは求人の網羅性(数)です。数が多いから途中で調査をやめたり、詳細ページのリンクが取得できないからといってその求人をスキップする用なことは絶対に避けてください。あなたが 1 件でもこのような操作を行うことで統計データに狂いが生じ、会社の信頼を損なうことになります
2. ユーザの判断を仰がない
   → 判断に迷う場面に遭遇したにも関わらず、ユーザに判断を仰がないで誤魔化すことは絶対にやめてください
3. 指示した以外の方法で求人を取得する
4. バリデーション処理をスキップする
   → これは絶対にやめてください。統計情報に狂いが生じます

## 重要事項

1. **1 社ずつ順次処理**（並行実行禁止）
2. **全件収集**（省略禁止）
3. **バリデーション必須**: JSON 出力後に `scripts/validate-company.ts` を実行
4. **エラー時は JSON を作成しない**: error.log に記録、TODO は未完了のまま
5. **コミット不要**
