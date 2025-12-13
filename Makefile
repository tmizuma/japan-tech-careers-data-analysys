.PHONY: rankings clean check-links check-data

# ランキングJSONを生成
rankings:
	python3 generate_rankings.py

# 生成されたランキングファイルを削除
clean:
	rm -rf current && mkdir -p current

# CSVのリンク切れをチェック
check-links:
	python3 check_links.py

# CSVの欠損値・型の統一性をチェック
check-data:
	python3 check_data_quality.py
