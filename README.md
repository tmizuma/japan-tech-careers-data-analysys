# 日本ソフトウェア企業分析ツール

日本のソフトウェア企業に関する情報を管理・分析するためのツール群です。

## 必要環境

- Python 3.x
- Make

## ファイル構成

```
.
├── company_list.csv          # 企業マスターデータ
├── check_links.py            # URLリンク切れチェックスクリプト
├── check_data_quality.py     # データ品質チェックスクリプト
├── generate_rankings.py      # ランキング生成スクリプト
├── 202512/                   # 月別企業詳細データ（JSON）
└── current/                  # 生成されたランキングファイル
```

## 使い方

### データ品質チェック

CSVの欠損値や型の統一性をチェックします:

```bash
make check-data
```

### リンク切れチェック

CSVに含まれるURLのリンク切れをチェックします:

```bash
make check-links
```

### ランキング生成

202512/フォルダ内の企業JSONから、売上高・求人数のランキングJSONを生成します:

```bash
make rankings
```

出力ファイル:
- `current/sales_ranking.json` - 売上高ランキング
- `current/position_ranking.json` - 求人ポジション数ランキング

### クリーンアップ

生成されたランキングファイルを削除します:

```bash
make clean
```

## company_list.csv のフォーマット

| カラム | 型 | 説明 |
|--------|-----|------|
| company_name_ja | string | 企業名（日本語） |
| company_name_en | string | 企業名（英語） |
| description | string | 企業説明（日本語） |
| description_en | string | 企業説明（英語） |
| hiring_url | string | 採用ページURL |
| num_of_employees | string | 従業員数（例: "100+", "2000+"） |
| sales | integer | 売上高（円）。不明の場合は -1 |
| foreign_engineers | boolean | 外国人エンジニア採用実績（true/false） |
| logo_url | string | ロゴ画像URL |
| company_url | string | 企業サイトURL |
