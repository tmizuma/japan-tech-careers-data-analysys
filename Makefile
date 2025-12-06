.PHONY: rankings clean

# ランキングJSONを生成
rankings:
	python3 generate_rankings.py

# 生成されたランキングファイルを削除
clean:
	rm -f sales_ranking.json position_ranking.json
