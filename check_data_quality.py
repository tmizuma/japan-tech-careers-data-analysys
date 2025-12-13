#!/usr/bin/env python3
"""
CSVファイルの欠損値と型の統一性をチェックするスクリプト
"""

import csv
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class DataIssue:
    row_num: int
    company: str
    column: str
    issue_type: str
    value: str


def check_missing_values(rows: list[dict], columns: list[str]) -> list[DataIssue]:
    """全てのカラムに値が存在するかチェック"""
    issues = []
    for i, row in enumerate(rows, start=2):  # ヘッダーが1行目なので2から開始
        company = row.get("company_name_ja", row.get("company_name_en", "Unknown"))
        for col in columns:
            value = row.get(col, "")
            if value is None or str(value).strip() == "":
                issues.append(DataIssue(i, company, col, "欠損値", repr(value)))
    return issues


def check_type_consistency(rows: list[dict]) -> list[DataIssue]:
    """型の統一性をチェック"""
    issues = []

    # foreign_engineers: TRUE/FALSE の統一性
    fe_values = defaultdict(list)
    for i, row in enumerate(rows, start=2):
        company = row.get("company_name_ja", row.get("company_name_en", "Unknown"))
        fe_val = row.get("foreign_engineers", "")
        fe_values[fe_val].append((i, company))

    # true/false以外の値をチェック（boolean型として小文字で統一）
    valid_values = {"true", "false"}
    for val, entries in fe_values.items():
        if val not in valid_values and val.strip() != "":
            for row_num, company in entries:
                issues.append(DataIssue(
                    row_num, company, "foreign_engineers",
                    "不正な値", f"'{val}' (期待: 'true' または 'false')"
                ))

    # sales: 数値または -1 であるべき
    for i, row in enumerate(rows, start=2):
        company = row.get("company_name_ja", row.get("company_name_en", "Unknown"))
        sales = row.get("sales", "")
        if sales.strip() != "":
            try:
                int(sales)
            except ValueError:
                issues.append(DataIssue(
                    i, company, "sales",
                    "不正な数値形式", f"'{sales}'"
                ))

    # num_of_employees: 一定のパターンであるべき
    ne_patterns = defaultdict(list)
    for i, row in enumerate(rows, start=2):
        company = row.get("company_name_ja", row.get("company_name_en", "Unknown"))
        ne_val = row.get("num_of_employees", "")
        ne_patterns[ne_val].append((i, company))

    # パターンを分析して報告
    print("\n【num_of_employees の値パターン】")
    for val, entries in sorted(ne_patterns.items(), key=lambda x: -len(x[1])):
        print(f"  '{val}': {len(entries)}件")

    # foreign_engineers のパターンも表示
    print("\n【foreign_engineers の値パターン】")
    for val, entries in sorted(fe_values.items(), key=lambda x: -len(x[1])):
        print(f"  '{val}': {len(entries)}件")

    return issues


def main():
    csv_file = "company_list.csv"

    # CSVを読み込み
    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        rows = list(reader)

    print(f"チェック対象: {len(rows)} 企業, {len(columns)} カラム")
    print(f"カラム: {', '.join(columns)}\n")

    # 1. 欠損値チェック
    print("=" * 60)
    print("【1. 欠損値チェック】")
    print("=" * 60)
    missing_issues = check_missing_values(rows, columns)
    if missing_issues:
        print(f"\n欠損値が {len(missing_issues)} 件見つかりました:\n")
        for issue in missing_issues:
            print(f"  行{issue.row_num} [{issue.company}] {issue.column}: {issue.issue_type}")
    else:
        print("\n欠損値はありませんでした。")

    # 2. 型の統一性チェック
    print("\n" + "=" * 60)
    print("【2. 型の統一性チェック】")
    print("=" * 60)
    type_issues = check_type_consistency(rows)
    if type_issues:
        print(f"\n型の問題が {len(type_issues)} 件見つかりました:\n")
        for issue in type_issues:
            print(f"  行{issue.row_num} [{issue.company}] {issue.column}: {issue.issue_type} - {issue.value}")
    else:
        print("\n型の問題はありませんでした。")

    # 結果サマリー
    total_issues = len(missing_issues) + len(type_issues)
    print("\n" + "=" * 60)
    print(f"チェック完了: 合計 {total_issues} 件の問題が見つかりました")
    print("=" * 60)

    if total_issues > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
