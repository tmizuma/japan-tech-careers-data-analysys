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

`current/` フォルダに以下のファイルが出力されます:

- `current/sales_ranking.json`: 売上高順にソートされた企業ランキング
- `current/position_ranking.json`: 求人ポジション数順にソートされた企業ランキング

## クリーンアップ

生成されたランキングファイルを削除するには:

```bash
make clean
```
