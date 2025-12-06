#!/usr/bin/env python3
"""
JSONファイルを集計してランキングJSONを生成するスクリプト
"""

import json
import os
from pathlib import Path


def load_company_data(json_dir: str) -> dict:
    """指定ディレクトリ内のすべてのJSONファイルを読み込む"""
    companies = {}
    json_path = Path(json_dir)

    for json_file in json_path.glob("*.json"):
        company_key = json_file.stem  # ファイル名（拡張子なし）をキーとして使用
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        # positionsの数を計算し、positions配列を削除
        positions = data.pop("positions", [])
        data["num_of_positions"] = len(positions)

        companies[company_key] = data

    return companies


def sort_by_sales(companies: dict) -> list:
    """salesの降順でソート"""
    return sorted(
        companies.items(),
        key=lambda x: x[1].get("sales", -1) if x[1].get("sales", -1) != -1 else float("-inf"),
        reverse=True,
    )


def sort_by_positions(companies: dict) -> list:
    """num_of_positionsの降順でソート"""
    return sorted(companies.items(), key=lambda x: x[1].get("num_of_positions", 0), reverse=True)


def create_ranking_json(sorted_companies: list) -> dict:
    """ランキングJSON形式に変換"""
    return {"companies": {key: value for key, value in sorted_companies}}


def main():
    json_dir = "202512"
    output_dir = "."

    # JSONファイルを読み込み
    print(f"Loading JSON files from {json_dir}/...")
    companies = load_company_data(json_dir)
    print(f"Loaded {len(companies)} companies")

    # salesランキングを生成
    print("Generating sales_ranking.json...")
    sales_sorted = sort_by_sales(companies)
    sales_ranking = create_ranking_json(sales_sorted)
    with open(os.path.join(output_dir, "sales_ranking.json"), "w", encoding="utf-8") as f:
        json.dump(sales_ranking, f, ensure_ascii=False, indent=2)
    print("  -> sales_ranking.json created")

    # positionsランキングを生成
    print("Generating position_ranking.json...")
    positions_sorted = sort_by_positions(companies)
    position_ranking = create_ranking_json(positions_sorted)
    with open(os.path.join(output_dir, "position_ranking.json"), "w", encoding="utf-8") as f:
        json.dump(position_ranking, f, ensure_ascii=False, indent=2)
    print("  -> position_ranking.json created")

    print("Done!")


if __name__ == "__main__":
    main()
