#!/usr/bin/env python3
"""
CSVファイル内のURLリンク切れをチェックするスクリプト
"""

import csv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Union


@dataclass
class LinkResult:
    company: str
    url_type: str
    url: str
    status: Union[int, str]
    is_broken: bool


def check_url(company: str, url_type: str, url: str, timeout: int = 10) -> LinkResult:
    """URLの有効性をチェック"""
    if not url or url.strip() == "":
        return LinkResult(company, url_type, url, "Empty", True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers, verify=False)
        # HEADが405の場合はGETで再試行
        if response.status_code == 405:
            response = requests.get(url, timeout=timeout, allow_redirects=True, headers=headers, verify=False)

        is_broken = response.status_code >= 400
        return LinkResult(company, url_type, url, response.status_code, is_broken)
    except requests.exceptions.Timeout:
        return LinkResult(company, url_type, url, "Timeout", True)
    except requests.exceptions.SSLError:
        return LinkResult(company, url_type, url, "SSL Error", True)
    except requests.exceptions.ConnectionError:
        return LinkResult(company, url_type, url, "Connection Error", True)
    except Exception as e:
        return LinkResult(company, url_type, url, str(e)[:50], True)


def main():
    csv_file = "company_list"
    url_columns = ["logo_url", "company_url", "hiring_url"]

    # CSVを読み込み
    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"チェック対象: {len(rows)} 企業 × {len(url_columns)} URL = {len(rows) * len(url_columns)} リンク\n")

    # チェックするタスクを作成
    tasks = []
    for row in rows:
        company = row.get("company_name_ja", row.get("company_name_en", "Unknown"))
        for col in url_columns:
            url = row.get(col, "")
            tasks.append((company, col, url))

    # 並列でチェック実行
    results: list[LinkResult] = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_url, *task): task for task in tasks}

        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            status_str = "OK" if not result.is_broken else "NG"
            print(f"[{i}/{len(tasks)}] {status_str} - {result.company} ({result.url_type}): {result.status}")

    # 結果集計
    broken = [r for r in results if r.is_broken]

    print("\n" + "=" * 60)
    print(f"チェック完了: {len(results)} リンク中 {len(broken)} 件のリンク切れ")
    print("=" * 60)

    if broken:
        print("\n【リンク切れ一覧】\n")
        for r in sorted(broken, key=lambda x: (x.company, x.url_type)):
            print(f"企業: {r.company}")
            print(f"  種類: {r.url_type}")
            print(f"  URL: {r.url}")
            print(f"  状態: {r.status}")
            print()
    else:
        print("\nリンク切れはありませんでした。")


if __name__ == "__main__":
    main()
