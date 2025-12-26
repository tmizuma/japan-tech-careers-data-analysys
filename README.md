# 日本ソフトウェア企業分析ツール

日本のソフトウェア企業に関する情報を管理・分析するためのツール群です。

## 必要環境

- Python 3.x
- Make

## 手順

1. company_list.csv の最新化 (必要であれば)

- add-company command を使って企業を追加
- S3 バケットにロゴを追加する

2. CSV の整合性チェック

```bash
make check-links
make check-data
```

3. スクレイピング

yyyymmdd/ フォルダを作成し、スクレイピングを実行

```bash
/gather-japan-position-info company_list.csv 202512 --from 1 --to 1000
```

結果チェック

```bash
npx ts-node scripts/validate-all-companies.ts 202512
```

4.ranking データの作成

```bash
make clear
make rankings

# データの検証
npx ts-node scripts/validate-ranking.ts
```
