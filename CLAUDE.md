# 目的

このリポジトリの目的は、日本のソフトウェア企業に関して様々な分析を行うことです。
すべての分析の起点は、 company_list.csv から始まります。

# company_list.csv のスキーマ

| カラム名 | 型 | 説明 |
|---------|-----|------|
| company_name_ja | string | 企業名（日本語） |
| company_name_en | string | 企業名（英語） |
| description | string | 企業説明（日本語） |
| description_en | string | 企業説明（英語） |
| hiring_url | string | 採用ページURL |
| num_of_employees | string | 従業員数（例: "100+", "2000+"） |
| sales | integer | 売上高（円）。不明の場合は -1 |
| foreign_engineers | boolean | 外国人エンジニア採用実績（true/false、クォートなし） |
| logo_url | string | ロゴ画像URL |
| company_url | string | 企業サイトURL |

# company_list.csv を修正した場合の対応

## URL を修正した場合

company_list.csv の URL の修正を行なった場合は、必ず `make check-links` を実行して、CSV の中にリンク切れ URL が含まれていないことを保証してください。

## データを追加・修正した場合

データの追加や修正を行った場合は、`make check-data` を実行して、欠損値や型の不統一がないことを確認してください。

# 利用可能なスクリプト

| スクリプト | 説明 | Makeターゲット |
|-----------|------|----------------|
| check_links.py | CSVのURL（logo_url, company_url, hiring_url）のリンク切れをチェック | `make check-links` |
| check_data_quality.py | CSVの欠損値と型の統一性をチェック | `make check-data` |
| generate_rankings.py | 202512/フォルダのJSONから売上・求人数ランキングを生成 | `make rankings` |
