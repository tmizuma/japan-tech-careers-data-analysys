# 企業ランキング生成ツール

202512/ フォルダ内の企業JSONファイルを集計し、ランキングJSONを生成します。

## 必要環境

- Python 3.x
- Make

## 実行方法

### Makeを使用する場合

```bash
make rankings
```

### 直接実行する場合

```bash
python3 generate_rankings.py
```

## 出力ファイル

- `sales_ranking.json`: 売上高順にソートされた企業ランキング
- `position_ranking.json`: 求人ポジション数順にソートされた企業ランキング

## クリーンアップ

生成されたランキングファイルを削除するには:

```bash
make clean
```

## 入力データ形式

202512/ フォルダ内のJSONファイルは以下の形式を想定しています:

```json
{
  "company_name_ja": "企業名（日本語）",
  "company_name_en": "Company Name (English)",
  "description": "企業説明",
  "description_en": "Company description",
  "hiring_url": "採用ページURL",
  "num_of_employees": "従業員数",
  "sales": 売上高（数値、不明の場合は-1）,
  "foreign_engineers": true/false,
  "logo_url": "ロゴURL",
  "company_url": "企業URL",
  "positions": [
    {
      "name": "ポジション名",
      "description": "ポジション説明",
      "techstack": ["技術1", "技術2"],
      "link": "求人URL"
    }
  ]
}
```

## 出力データ形式

```json
{
  "companies": {
    "企業key": {
      "company_name_ja": "...",
      "company_name_en": "...",
      "description": "...",
      "description_en": "...",
      "hiring_url": "...",
      "num_of_employees": "...",
      "sales": ...,
      "foreign_engineers": ...,
      "logo_url": "...",
      "company_url": "...",
      "num_of_positions": ポジション数
    }
  }
}
```
